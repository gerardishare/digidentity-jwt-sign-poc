import os
from importlib import import_module

def load_config():
    """Load configuration based on environment"""
    env = os.getenv('FLASK_ENV', 'preprod')
    try:
        config_module = import_module(f'config.{env}')
        return config_module
    except ImportError:
        raise ImportError(f"Configuration for environment '{env}' not found") 