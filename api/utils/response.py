"""
Response utilities for F1 Web App API.
"""

from flask import jsonify


def create_response(data=None, status_code=200, error=None):
    """
    Create a standardized API response.
    
    Args:
        data: The data to include in the response
        status_code: HTTP status code (default: 200)
        error: Optional error message
        
    Returns:
        Response: Flask response object
    """
    response = {}
    
    if error:
        response['success'] = False
        response['error'] = error
    else:
        response['success'] = True
        if data is not None:
            response['data'] = data
    
    return jsonify(response), status_code


def success_response(data=None, message=None, status_code=200):
    """
    Create a standardized success response.
    
    Args:
        data: The data to include in the response
        message: Optional message to include in the response
        status_code: HTTP status code (default: 200)
        
    Returns:
        tuple: (response, status_code)
    """
    response = {
        'success': True
    }
    
    if data is not None:
        response['data'] = data
        
    if message is not None:
        response['message'] = message
        
    return jsonify(response), status_code


def error_response(message, status_code=400, errors=None):
    """
    Create a standardized error response.
    
    Args:
        message: Error message
        status_code: HTTP status code (default: 400)
        errors: Optional dictionary of specific errors
        
    Returns:
        tuple: (response, status_code)
    """
    response = {
        'success': False,
        'message': message
    }
    
    if errors is not None:
        response['errors'] = errors
        
    return jsonify(response), status_code
