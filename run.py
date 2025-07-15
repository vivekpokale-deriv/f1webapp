"""
Entry point for the F1 Web App.
"""

import os
import argparse
import fastf1
from flask import Flask
from api.app import create_app
from api.config import get_config

# Parse command-line arguments
parser = argparse.ArgumentParser(description='Run the F1 Web App')
parser.add_argument('--port', type=int, default=5002, help='Port to run the server on')
args = parser.parse_args()

# Get configuration
config = get_config()

# Enable FastF1 cache
if not os.path.exists(config.CACHE_DIR):
    os.makedirs(config.CACHE_DIR)
fastf1.Cache.enable_cache(config.CACHE_DIR)

# Create Flask app
app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=args.port, debug=config.DEBUG)
