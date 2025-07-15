"""
Error handling utilities for F1 Web App API.
"""

import logging
from flask import Blueprint, jsonify, request
from werkzeug.exceptions import HTTPException

logger = logging.getLogger('f1webapp')


class APIError(Exception):
    """Base class for API errors."""
    
    def __init__(self, message, status_code=400, errors=None):
        """
        Initialize API error.
        
        Args:
            message: Error message
            status_code: HTTP status code
            errors: Optional dictionary of specific errors
        """
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.errors = errors


def register_error_handlers(app):
    """
    Register error handlers for the Flask app.
    
    Args:
        app: Flask application
    """
    @app.errorhandler(APIError)
    def handle_api_error(error):
        """Handle custom API errors."""
        response = {
            'success': False,
            'message': error.message
        }
        
        if error.errors:
            response['errors'] = error.errors
            
        return jsonify(response), error.status_code
    
    @app.errorhandler(HTTPException)
    def handle_http_error(error):
        """Handle HTTP exceptions."""
        response = {
            'success': False,
            'message': error.description
        }
        
        return jsonify(response), error.code
    
    @app.errorhandler(Exception)
    def handle_generic_error(error):
        """Handle generic exceptions."""
        # Log the error
        logger.error(f"Unhandled exception: {str(error)}")
        logger.exception(error)
        
        response = {
            'success': False,
            'message': 'An unexpected error occurred'
        }
        
        return jsonify(response), 500


def configure_error_handling(blueprint):
    """
    Configure error handling for a blueprint.
    
    Args:
        blueprint: Flask Blueprint
    """
    @blueprint.errorhandler(APIError)
    def handle_api_error(error):
        """Handle custom API errors."""
        response = {
            'success': False,
            'message': error.message
        }
        
        if error.errors:
            response['errors'] = error.errors
            
        return jsonify(response), error.status_code
