import os

class Config:
    """Configuration class for the application"""
    
    # Google Maps API Configuration
    GOOGLE_MAPS_API_KEY = os.environ.get('GOOGLE_MAPS_API_KEY', 'your-google-maps-api-key-here')
    
    # Flask Configuration
    SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key-here')
    DEBUG = os.environ.get('DEBUG', 'True').lower() == 'true'
    
    # Server Configuration
    HOST = os.environ.get('HOST', '0.0.0.0')
    PORT = int(os.environ.get('PORT', 5001))
    
    # Default timezone offset for India (IST)
    DEFAULT_TZ_OFFSET = 5.5
    
    # India bounds for timezone detection
    INDIA_BOUNDS = {
        'lat_min': 6.0,
        'lat_max': 37.0,
        'lng_min': 68.0,
        'lng_max': 97.0
    }