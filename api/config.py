"""
Configuration for the F1 Web App.
"""

import os

class Config:
    """Base configuration."""
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key-for-development-only')
    DEBUG = False
    TESTING = False
    
    # FastF1 settings
    CACHE_DIR = os.environ.get('F1_CACHE_DIR', 'cache')
    
    # File paths
    SCHEDULE_FILE = os.environ.get('F1_SCHEDULE_FILE', 'data/sched.csv')
    FLAGS_FILE = os.environ.get('F1_FLAGS_FILE', 'data/country_flags.json')
    
    # Plot settings
    DEFAULT_FIG_SIZE = (12, 8)
    DEFAULT_MINI_SECTORS = 20


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True


class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    DEBUG = True


class ProductionConfig(Config):
    """Production configuration."""
    # Production settings would go here
    pass


# Dictionary of configurations
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}


def get_config():
    """
    Get the configuration based on the environment.
    
    Returns:
        Config: The configuration object
    """
    env = os.environ.get('FLASK_ENV', 'default')
    return config.get(env, config['default'])
