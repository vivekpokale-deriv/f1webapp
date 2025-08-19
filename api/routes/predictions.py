"""
API routes for predictions.
"""

from flask import Blueprint, request, jsonify
from services.prediction_service import PredictionService
from services.session_service import SessionService
from api.routes.utils import format_lap_time
import logging

logger = logging.getLogger('f1webapp')
predictions_bp = Blueprint('predictions_bp', __name__)

prediction_service = PredictionService()

@predictions_bp.route('/predict/qualifying_time', methods=['GET'])
def predict_qualifying_time():
    """
    Predict the qualifying lap time for a given driver.
    """
    year = request.args.get('year')
    race = request.args.get('race')
    driver = request.args.get('driver')

    if not all([year, race, driver]):
        return jsonify({"error": "Missing required parameters: year, race, driver"}), 400

    try:
        prediction_seconds = prediction_service.predict_lap_time(int(year), race, driver)
        formatted_time = format_lap_time(prediction_seconds)
        return jsonify({
            "predicted_lap_time_seconds": prediction_seconds,
            "predicted_lap_time_formatted": formatted_time
        })
    except Exception as e:
        logger.error(f"Error predicting lap time: {e}")
        return jsonify({"error": str(e)}), 500

@predictions_bp.route('/train/qualifying_time_model', methods=['POST'])
def train_qualifying_time_model():
    """
    Train the qualifying lap time prediction model.
    """
    data = request.get_json()
    years = data.get('years')
    races = data.get('races')

    if not all([years, races]):
        return jsonify({"error": "Missing required parameters: years, races"}), 400

    try:
        prediction_service.train_model(years, races)
        return jsonify({"message": "Model training initiated."})
    except Exception as e:
        logger.error(f"Error training model: {e}")
        return jsonify({"error": str(e)}), 500
