"""
Main Flask application for F1 Web App.
"""

from flask import Flask, jsonify, render_template
from flask_cors import CORS
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('f1webapp')

def create_app():
    """
    Create and configure the Flask application.
    
    Returns:
        Flask: The configured Flask application
    """
    app = Flask(__name__)
    
    # Enable CORS
    CORS(app)
    
    # Register blueprints
    from api.routes.telemetry import telemetry_bp
    from api.routes.race_analysis import race_analysis_bp
    from api.routes.info import info_bp
    from api.routes.utils import utils_bp
    
    app.register_blueprint(telemetry_bp, url_prefix='/api/telemetry')
    app.register_blueprint(race_analysis_bp, url_prefix='/api/race-analysis')
    app.register_blueprint(info_bp, url_prefix='/api/info')
    app.register_blueprint(utils_bp, url_prefix='/api/utils')
    
    # Health check endpoint
    @app.route('/health')
    def health_check():
        return jsonify({'status': 'ok'})
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Not found'}), 404
    
    @app.errorhandler(500)
    def server_error(error):
        logger.error(f"Server error: {error}")
        return jsonify({'error': 'Internal server error'}), 500
    
    return app
