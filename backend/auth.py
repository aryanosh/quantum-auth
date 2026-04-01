import jwt
from datetime import datetime, timedelta
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError


class AuthService:
    """
    Handles authentication operations
    """
    
    def __init__(self):
        # Use Argon2 for password hashing (memory-hard, GPU-resistant)
        self.ph = PasswordHasher(
            time_cost=2,  # Number of iterations
            memory_cost=65536,  # Memory usage in KiB
            parallelism=4,  # Number of parallel threads
            hash_len=32,  # Length of hash in bytes
            salt_len=16  # Length of salt in bytes
        )
    
    def hash_password(self, password):
        """Hash password using Argon2"""
        return self.ph.hash(password)
    
    def verify_password(self, password, hash):
        """Verify password against hash"""
        try:
            self.ph.verify(hash, password)
            
            # Check if hash needs rehashing (parameters changed)
            if self.ph.check_needs_rehash(hash):
                return 'rehash_needed'
            
            return True
        except VerifyMismatchError:
            return False
    
    def generate_token(self, user_id, secret_key, expires_in=24):
        """
        Generate JWT token
        expires_in: hours
        """
        payload = {
            'user_id': user_id,
            'exp': datetime.utcnow() + timedelta(hours=expires_in),
            'iat': datetime.utcnow()
        }
        
        token = jwt.encode(payload, secret_key, algorithm='HS256')
        return token
    
    def verify_token(self, token, secret_key):
        """Verify JWT token"""
        try:
            payload = jwt.decode(token, secret_key, algorithms=['HS256'])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None