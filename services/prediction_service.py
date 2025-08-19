"""
Service for handling F1 qualifying lap time prediction.
"""

import logging
import fastf1
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
import numpy as np
import pandas as pd
import os

logger = logging.getLogger('f1webapp')

class PredictionService:
    """
    Service for predicting F1 qualifying lap times.
    """

    def __init__(self, session_service=None):
        """
        Initialize the prediction service.
        
        Args:
            session_service: Optional SessionService instance for session caching
        """
        from services.session_service import SessionService
        self.session_service = session_service or SessionService
        
        # Get the absolute path to the models directory
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.model_path = os.path.join(base_dir, 'models', 'trained_models', 'qualifying_time_predictor.json')
        
        self.model = self._load_model()
        self.feature_names = None

    def _load_model(self):
        """
        Load the trained XGBoost model and feature names.
        """
        feature_names_path = self.model_path.replace('.json', '_features.json')
        if os.path.exists(self.model_path) and os.path.exists(feature_names_path):
            logger.info(f"Loading model from {self.model_path}")
            model = xgb.XGBRegressor()
            model.load_model(self.model_path)
            
            logger.info(f"Loading feature names from {feature_names_path}")
            with open(feature_names_path, 'r') as f:
                self.feature_names = json.load(f)
            
            return model
        else:
            logger.warning(f"Model file or feature names file not found. The model needs to be trained.")
            return None

    def _get_telemetry_features(self, lap):
        """
        Extract telemetry features for a given lap.
        """
        try:
            telemetry = lap.get_telemetry()
            
            avg_rpm = telemetry['RPM'].mean()
            full_throttle_percent = (telemetry['Throttle'] == 100).mean()
            braking_percent = (telemetry['Brake'] == True).mean()

            return {
                'AvgRPM': avg_rpm,
                'FullThrottlePercent': full_throttle_percent,
                'BrakingPercent': braking_percent
            }
        except Exception as e:
            logger.error(f"Could not get telemetry for lap {lap['LapNumber']}: {e}")
            return {
                'AvgRPM': np.nan,
                'FullThrottlePercent': np.nan,
                'BrakingPercent': np.nan
            }

    def _prepare_data_for_session(self, year, race):
        """
        Prepare training data for a single race weekend.
        """
        # Load all practice sessions and qualifying
        sessions = {}
        for session_name in ['FP1', 'FP2', 'FP3', 'Q']:
            try:
                session = self.session_service.get_session(year, race, session_name)
                session.load(telemetry=True, weather=True)
                sessions[session_name] = session
            except Exception as e:
                logger.error(f"Could not load session {session_name} for {year} {race}: {e}")
                return pd.DataFrame(), pd.Series()

        # Check for wet sessions
        for session_name in ['FP1', 'FP2', 'FP3']:
            if sessions[session_name].weather_data['Rainfall'].any():
                logger.info(f"Skipping {year} {race} due to wet practice session {session_name}.")
                return pd.DataFrame(), pd.Series()

        # Get qualifying results
        quali_results = sessions['Q'].results

        all_laps_data = []

        for session_name in ['FP1', 'FP2', 'FP3']:
            session = sessions[session_name]
            practice_laps = session.laps.pick_quicklaps() # Laps within 107% of fastest

            for _, lap in practice_laps.iterrows():
                lap_data = {
                    'LapTime': lap['LapTime'].total_seconds(),
                    'Compound': lap['Compound'],
                    'TyreLife': lap['TyreLife'],
                    'Driver': lap['Driver'],
                    'Team': lap['Team'],
                    'TrackID': race,
                    'TrackTemp': session.weather_data['TrackTemp'].mean(), # Average track temp for the session
                    'StDevLapTime': practice_laps[practice_laps['Driver'] == lap['Driver']]['LapTime'].dt.total_seconds().std()
                }

                telemetry_features = self._get_telemetry_features(lap)
                lap_data.update(telemetry_features)

                all_laps_data.append(lap_data)

        if not all_laps_data:
            return pd.DataFrame(), pd.Series()

        features_df = pd.DataFrame(all_laps_data)
        
        # Get labels
        labels = []
        for _, row in features_df.iterrows():
            driver_quali_result = quali_results[quali_results['Abbreviation'] == row['Driver']]
            if not driver_quali_result.empty:
                q1 = driver_quali_result['Q1'].iloc[0]
                q2 = driver_quali_result['Q2'].iloc[0]
                q3 = driver_quali_result['Q3'].iloc[0]
                
                fastest_quali_lap = min(q for q in [q1, q2, q3] if pd.notna(q))
                if pd.notna(fastest_quali_lap):
                    labels.append(fastest_quali_lap.total_seconds())
                else:
                    labels.append(np.nan)
            else:
                labels.append(np.nan)
        
        labels_s = pd.Series(labels, index=features_df.index)

        # Drop rows where we couldn't get a label
        valid_indices = labels_s.dropna().index
        features_df = features_df.loc[valid_indices].reset_index(drop=True)
        labels_s = labels_s.loc[valid_indices].reset_index(drop=True)

        return features_df, labels_s

    def train_model(self, years, races, update=False):
        """
        Train or update the XGBoost model.
        """
        all_features_df = pd.DataFrame()
        all_labels_s = pd.Series(dtype=np.float64)

        for year in years:
            for race in races:
                features_df, labels_s = self._prepare_data_for_session(year, race)
                if not features_df.empty:
                    all_features_df = pd.concat([all_features_df, features_df], ignore_index=True)
                    all_labels_s = pd.concat([all_labels_s, labels_s], ignore_index=True)

        if all_features_df.empty:
            logger.error("No data available for training.")
            return

        # One-hot encode categorical features
        X = pd.get_dummies(all_features_df, columns=['Compound', 'Driver', 'Team', 'TrackID'], dummy_na=True)
        y = all_labels_s

        # Handle missing values
        X = X.fillna(X.mean())
        
        self.feature_names = X.columns.tolist()

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        if update and self.model:
            logger.info("Updating existing model.")
            self.model.fit(X_train, y_train, xgb_model=self.model.get_booster())
        else:
            logger.info("Training new model.")
            model = xgb.XGBRegressor(objective='reg:squarederror', n_estimators=100, learning_rate=0.1, max_depth=5)
            model.fit(X_train, y_train)
            self.model = model

        y_pred = self.model.predict(X_test)
        mse = mean_squared_error(y_test, y_pred)
        logger.info(f"Model training complete. MSE: {mse}")

        # Save the model and feature names
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        self.model.save_model(self.model_path)
        logger.info(f"Model saved to {self.model_path}")
        
        feature_names_path = self.model_path.replace('.json', '_features.json')
        with open(feature_names_path, 'w') as f:
            json.dump(self.feature_names, f)
        logger.info(f"Feature names saved to {feature_names_path}")

    def predict_lap_time(self, year, race, driver):
        """
        Predict the qualifying lap time for a given driver.
        """
        if self.model is None:
            raise Exception("Model not loaded. Please train the model first.")

        # Prepare data for prediction (similar to training data prep)
        sessions = {}
        for session_name in ['FP1', 'FP2', 'FP3']:
            try:
                session = self.session_service.get_session(year, race, session_name)
                session.load(telemetry=True, weather=True)
                sessions[session_name] = session
            except Exception as e:
                logger.error(f"Could not load session {session_name} for {year} {race}: {e}")
                raise Exception(f"Could not load session {session_name}")

        if any(s.weather_data['Rainfall'].any() for s in sessions.values()):
            raise Exception("Cannot predict for a wet session.")

        all_laps_data = []
        for session_name in ['FP1', 'FP2', 'FP3']:
            session = sessions[session_name]
            driver_laps = session.laps.pick_driver(driver).pick_quicklaps()
            if not driver_laps.empty:
                for _, lap in driver_laps.iterrows():
                    lap_data = {
                        'LapTime': lap['LapTime'].total_seconds(),
                        'Compound': lap['Compound'],
                        'TyreLife': lap['TyreLife'],
                        'Driver': lap['Driver'],
                        'Team': lap['Team'],
                        'TrackID': race,
                        'TrackTemp': session.weather_data['TrackTemp'].mean(),
                        'StDevLapTime': driver_laps['LapTime'].dt.total_seconds().std()
                    }
                    telemetry_features = self._get_telemetry_features(lap)
                    lap_data.update(telemetry_features)
                    all_laps_data.append(lap_data)
        
        if not all_laps_data:
            raise Exception(f"No representative practice laps found for driver {driver}.")

        features_df = pd.DataFrame(all_laps_data)
        
        # One-hot encode and align columns with the trained model
        X = pd.get_dummies(features_df, columns=['Compound', 'Driver', 'Team', 'TrackID'], dummy_na=True)
        X = X.reindex(columns=self.feature_names, fill_value=0)
        X = X.fillna(X.mean())

        # Predict the qualifying time for each practice lap and take the average
        predictions = self.model.predict(X)
        return float(predictions.mean())
