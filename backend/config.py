import os
from datetime import timedelta


class Config:
    """Application configuration with enhanced security settings"""
    
    # Flask
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'quantum-auth-secret-key-change-in-production'
    DEBUG = os.environ.get('DEBUG', 'True').lower() == 'true'
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///database.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
    
    # JWT
    JWT_SECRET_KEY = SECRET_KEY
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
    
    # CORS
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '*').split(',')
    
    # ==========================================
    # BIOMETRIC SECURITY THRESHOLDS
    # ==========================================
    
    # Face Recognition Threshold (0.0 - 1.0)
    # Higher = Stricter matching (less false positives, more false negatives)
    # Lower = Looser matching (more false positives, less false negatives)
    # 
    # Recommended values:
    # - 0.95: Very strict (same person, same conditions)
    # - 0.85: Strict (same person, different lighting/angle)
    # - 0.80: Moderate (recommended for production)
    # - 0.75: Lenient (testing only)
    # - 0.70: Very lenient (NOT recommended)
    FACE_SIMILARITY_THRESHOLD = float(os.environ.get('FACE_THRESHOLD', '0.82'))
    
    # Fingerprint Match Threshold (0-100)
    # Higher = Stricter matching
    # Typical values: 40-60, with 50 being standard
    FINGERPRINT_MATCH_THRESHOLD = int(os.environ.get('FINGERPRINT_THRESHOLD', '55'))
    
    # ==========================================
    # BIOMETRIC POLICY SETTINGS
    # ==========================================
    
    # Require biometric for login if registered
    # If True: Users who register with biometrics MUST use them to login
    # If False: Biometric is optional even if registered
    REQUIRE_BIOMETRIC_IF_REGISTERED = os.environ.get('REQUIRE_BIOMETRIC', 'True').lower() == 'true'
    
    # Allow password-only login for users without biometrics
    ALLOW_PASSWORD_ONLY_LOGIN = os.environ.get('ALLOW_PASSWORD_ONLY', 'True').lower() == 'true'
    
    # Maximum failed biometric attempts before temporary lockout
    MAX_FAILED_BIOMETRIC_ATTEMPTS = int(os.environ.get('MAX_FAILED_ATTEMPTS', '5'))
    
    # Lockout duration in minutes
    BIOMETRIC_LOCKOUT_DURATION = int(os.environ.get('LOCKOUT_DURATION', '15'))
    
    # ==========================================
    # IMAGE QUALITY REQUIREMENTS
    # ==========================================
    
    # Minimum image resolution for face recognition (width x height)
    MIN_FACE_IMAGE_WIDTH = 200
    MIN_FACE_IMAGE_HEIGHT = 200
    
    # Face detection confidence (0.0 - 1.0)
    FACE_DETECTION_CONFIDENCE = 0.7
    
    # Minimum face size ratio (face_width / image_width)
    MIN_FACE_SIZE_RATIO = 0.20
    MAX_FACE_SIZE_RATIO = 0.95
    
    # Brightness thresholds (0-255)
    MIN_IMAGE_BRIGHTNESS = 40
    MAX_IMAGE_BRIGHTNESS = 220
    
    # Blur detection threshold (Laplacian variance)
    MIN_IMAGE_SHARPNESS = 100
    
    # ==========================================
    # SECURITY SETTINGS
    # ==========================================
    
    # Upload limits
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    
    # Session security
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Rate limiting (requests per hour)
    RATE_LIMIT_LOGIN = 10  # Max login attempts per hour
    RATE_LIMIT_REGISTER = 5  # Max registration attempts per hour
    RATE_LIMIT_API = 100  # Max API calls per hour
    
    # ==========================================
    # LOGGING AND MONITORING
    # ==========================================
    
    # Enable detailed security logging
    ENABLE_SECURITY_LOGGING = True
    
    # Log failed authentication attempts
    LOG_FAILED_ATTEMPTS = True
    
    # Log successful authentications
    LOG_SUCCESSFUL_AUTH = True
    
    # Log biometric similarity scores
    LOG_SIMILARITY_SCORES = True
    
    # ==========================================
    # DEVELOPMENT/TESTING FLAGS
    # ==========================================
    
    # Bypass biometric verification (TESTING ONLY - NEVER IN PRODUCTION!)
    BYPASS_BIOMETRIC_VERIFICATION = os.environ.get('BYPASS_BIOMETRIC', 'False').lower() == 'true'
    
    # Use lower thresholds for testing
    if DEBUG and BYPASS_BIOMETRIC_VERIFICATION:
        FACE_SIMILARITY_THRESHOLD = 0.60  # Lower threshold for testing
        print("⚠️  WARNING: Biometric bypass enabled - FOR TESTING ONLY!")
    
    # ==========================================
    # HELPER METHODS
    # ==========================================
    
    @staticmethod
    def get_threshold_info():
        """Get human-readable threshold information"""
        return {
            'face_threshold': {
                'value': Config.FACE_SIMILARITY_THRESHOLD,
                'description': 'Cosine similarity threshold (0.0-1.0)',
                'strictness': Config._get_strictness_level(Config.FACE_SIMILARITY_THRESHOLD)
            },
            'fingerprint_threshold': {
                'value': Config.FINGERPRINT_MATCH_THRESHOLD,
                'description': 'Match score threshold (0-100)',
                'strictness': 'Standard' if Config.FINGERPRINT_MATCH_THRESHOLD == 50 else (
                    'Strict' if Config.FINGERPRINT_MATCH_THRESHOLD > 50 else 'Lenient'
                )
            },
            'policy': {
                'require_if_registered': Config.REQUIRE_BIOMETRIC_IF_REGISTERED,
                'allow_password_only': Config.ALLOW_PASSWORD_ONLY_LOGIN
            }
        }
    
    @staticmethod
    def _get_strictness_level(threshold):
        """Get human-readable strictness level"""
        if threshold >= 0.90:
            return 'Very Strict'
        elif threshold >= 0.82:
            return 'Strict (Recommended)'
        elif threshold >= 0.75:
            return 'Moderate'
        elif threshold >= 0.70:
            return 'Lenient'
        else:
            return 'Very Lenient (Not Recommended)'


# Print configuration on import (only in debug mode)
if __name__ == "__main__":
    print("\n" + "="*60)
    print("QUANTUM-SAFE AUTHENTICATION - CONFIGURATION")
    print("="*60)
    
    config = Config()
    threshold_info = Config.get_threshold_info()
    
    print(f"\n📊 Biometric Thresholds:")
    print(f"  Face Recognition: {threshold_info['face_threshold']['value']} "
          f"({threshold_info['face_threshold']['strictness']})")
    print(f"  Fingerprint: {threshold_info['fingerprint_threshold']['value']} "
          f"({threshold_info['fingerprint_threshold']['strictness']})")
    
    print(f"\n🔐 Security Policy:")
    print(f"  Require Biometric if Registered: {threshold_info['policy']['require_if_registered']}")
    print(f"  Allow Password-Only Login: {threshold_info['policy']['allow_password_only']}")
    
    print(f"\n🖼️  Image Quality Requirements:")
    print(f"  Min Resolution: {config.MIN_FACE_IMAGE_WIDTH}x{config.MIN_FACE_IMAGE_HEIGHT}")
    print(f"  Detection Confidence: {config.FACE_DETECTION_CONFIDENCE}")
    print(f"  Face Size Ratio: {config.MIN_FACE_SIZE_RATIO}-{config.MAX_FACE_SIZE_RATIO}")
    
    if config.BYPASS_BIOMETRIC_VERIFICATION:
        print(f"\n⚠️  WARNING: BIOMETRIC BYPASS IS ENABLED!")
        print(f"   This should NEVER be enabled in production!")
    
    print("\n" + "="*60 + "\n")