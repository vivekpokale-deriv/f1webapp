"""
Test script for the prediction service.
"""

import requests
import json
import time
import argparse
import os

BASE_URL = "http://127.0.0.1:5002"
MODEL_PATH = 'models/trained_models/qualifying_time_predictor.json'

def check_server_status():
    """
    Check if the Flask server is running.
    """
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            return True
    except requests.exceptions.ConnectionError:
        return False
    return False

def train_model():
    """
    Train the model with a default set of races.
    """
    print("--- Training Model ---")
    train_payload = {
        "years": [2023],  # Using 2023 data for testing
        "races": ["Bahrain Grand Prix", "Saudi Arabian Grand Prix"]
    }
    try:
        train_response = requests.post(f"{BASE_URL}/api/predictions/train/qualifying_time_model", json=train_payload)
        train_response.raise_for_status()
        print("Training request successful.")
        print(train_response.json())
    except requests.exceptions.RequestException as e:
        print(f"Error during training request: {e}")
        return False
    return True

def run_prediction(year, race, driver):
    """
    Run a prediction for a given year, race, and driver.
    """
    print("\n--- Getting Prediction ---")
    predict_params = {
        "year": year,
        "race": race,
        "driver": driver
    }
    try:
        print(f"\nRequesting prediction for {driver} at the {year} {race}...")
        predict_response = requests.get(f"{BASE_URL}/api/predictions/predict/qualifying_time", params=predict_params)
        predict_response.raise_for_status()
        print("Prediction request successful.")
        print(predict_response.json())
    except requests.exceptions.RequestException as e:
        print(f"Error during prediction request: {e}")

def main():
    """
    Main function to run the test script.
    """
    parser = argparse.ArgumentParser(description="Test script for the F1 prediction service.")
    parser.add_argument('--force-train', action='store_true', help="Force retraining of the model.")
    parser.add_argument('--year', type=int, default=2023, help="Year for the prediction.")
    parser.add_argument('--race', type=str, default="Italian Grand Prix", help="Race for the prediction.")
    parser.add_argument('--driver', type=str, default="VER", help="Driver for the prediction.")
    args = parser.parse_args()

    if not check_server_status():
        print("Flask server is not running. Please start the server with the following command:")
        print("python -m f1webapp.run")
        return

    if args.force_train or not os.path.exists(MODEL_PATH):
        if not train_model():
            return # Stop if training fails
        print("\nWaiting for model to train...")
        time.sleep(5) # Give it a moment to save

    run_prediction(args.year, args.race, args.driver)

if __name__ == "__main__":
    main()
