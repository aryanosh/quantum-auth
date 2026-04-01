import base64
import secrets
import requests
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC  # Fixed: Changed from PBKDF2 to PBKDF2HMAC
import logging

# Try to import liboqs for PQC
try:
    import oqs
    OQS_AVAILABLE = True
except ImportError:
    OQS_AVAILABLE = False
    logging.warning("liboqs not available, using Fernet fallback")


class QuantumCrypto:
    """
    Handles quantum-inspired cryptography including:
    - Post-quantum key encapsulation (Kyber)
    - Quantum random number generation
    - Fallback to classical cryptography
    """
    
    def __init__(self):
        self.pqc_available = OQS_AVAILABLE
        self.kem_algorithm = "Kyber768"  # NIST Level 3
        self.qrng_api_url = "https://qrng.anu.edu.au/API/jsonI.php"
        
        # Initialize master key for Fernet fallback
        self.master_key = self._generate_master_key()
        self.fernet = Fernet(self.master_key)
        
        # Initialize PQC if available
        if self.pqc_available:
            try:
                self.kem = oqs.KeyEncapsulation(self.kem_algorithm)
                logging.info(f"PQC initialized with {self.kem_algorithm}")
            except Exception as e:
                logging.error(f"Failed to initialize PQC: {e}")
                self.pqc_available = False
    
    def _generate_master_key(self):
        """Generate a master key for Fernet encryption"""
        # Use quantum random numbers if possible
        random_bytes = self.get_quantum_random_bytes(32)
        
        # Derive key using PBKDF2HMAC
        kdf = PBKDF2HMAC(  # Fixed: Changed from PBKDF2 to PBKDF2HMAC
            algorithm=hashes.SHA256(),
            length=32,
            salt=b'quantum_auth_salt_v1',  # In production, use unique salt
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(random_bytes))
        return key
    
    def get_quantum_random_bytes(self, length=32):
        """
        Get quantum random bytes from ANU QRNG API
        Falls back to cryptographically secure random if unavailable
        """
        try:
            # Request quantum random numbers
            params = {
                'length': length,
                'type': 'uint8',
                'size': 1
            }
            
            response = requests.get(
                self.qrng_api_url,
                params=params,
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                if data['success']:
                    # Convert array to bytes
                    random_array = data['data']
                    return bytes(random_array)
            
            logging.warning("QRNG API failed, using fallback")
        
        except Exception as e:
            logging.warning(f"QRNG error: {e}, using fallback")
        
        # Fallback to cryptographically secure random
        return secrets.token_bytes(length)
    
    def encrypt(self, plaintext):
        """
        Encrypt data using PQC or Fernet fallback
        """
        if isinstance(plaintext, str):
            plaintext = plaintext.encode('utf-8')
        
        if self.pqc_available:
            return self._encrypt_pqc(plaintext)
        else:
            return self._encrypt_fernet(plaintext)
    
    def decrypt(self, ciphertext):
        """
        Decrypt data using PQC or Fernet fallback
        """
        if self.pqc_available:
            decrypted = self._decrypt_pqc(ciphertext)
        else:
            decrypted = self._decrypt_fernet(ciphertext)
        
        # Try to decode as string
        try:
            return decrypted.decode('utf-8')
        except:
            return decrypted
    
    def _encrypt_pqc(self, plaintext):
        """
        Encrypt using Kyber KEM + AES
        """
        try:
            # Generate ephemeral keypair for this encryption
            public_key = self.kem.generate_keypair()
            
            # Encapsulate to get shared secret
            ciphertext_kem, shared_secret = self.kem.encap_secret(public_key)
            
            # Use shared secret to derive encryption key
            kdf = PBKDF2HMAC(  # Fixed: Changed from PBKDF2 to PBKDF2HMAC
                algorithm=hashes.SHA256(),
                length=32,
                salt=b'pqc_salt',
                iterations=100000,
            )
            encryption_key = base64.urlsafe_b64encode(kdf.derive(shared_secret))
            
            # Encrypt plaintext with derived key
            f = Fernet(encryption_key)
            encrypted_data = f.encrypt(plaintext)
            
            # Combine KEM ciphertext and encrypted data
            # Format: [kem_length(4 bytes)][kem_ciphertext][encrypted_data]
            kem_length = len(ciphertext_kem).to_bytes(4, 'big')
            combined = kem_length + ciphertext_kem + encrypted_data
            
            # Base64 encode for storage
            return base64.b64encode(combined).decode('utf-8')
        
        except Exception as e:
            logging.error(f"PQC encryption failed: {e}")
            # Fallback to Fernet
            return self._encrypt_fernet(plaintext)
    
    def _decrypt_pqc(self, ciphertext):
        """
        Decrypt using Kyber KEM + AES
        """
        try:
            # Decode from base64
            combined = base64.b64decode(ciphertext)
            
            # Extract KEM ciphertext length
            kem_length = int.from_bytes(combined[:4], 'big')
            
            # Extract KEM ciphertext and encrypted data
            ciphertext_kem = combined[4:4+kem_length]
            encrypted_data = combined[4+kem_length:]
            
            # Note: In production, you'd need to store the private key securely
            # This is a simplified example - proper key management is crucial
            
            # For demonstration, we'll use Fernet fallback for actual decryption
            # In a real system, you'd use the KEM to derive the decryption key
            return self._decrypt_fernet(base64.b64encode(encrypted_data).decode('utf-8'))
        
        except Exception as e:
            logging.error(f"PQC decryption failed: {e}")
            # Fallback to Fernet
            return self._decrypt_fernet(ciphertext)
    
    def _encrypt_fernet(self, plaintext):
        """
        Encrypt using Fernet (AES-128-CBC)
        """
        encrypted = self.fernet.encrypt(plaintext)
        return base64.b64encode(encrypted).decode('utf-8')
    
    def _decrypt_fernet(self, ciphertext):
        """
        Decrypt using Fernet
        """
        encrypted = base64.b64decode(ciphertext)
        return self.fernet.decrypt(encrypted)
    
    def generate_secure_token(self, length=32):
        """
        Generate a cryptographically secure token using quantum randomness
        """
        random_bytes = self.get_quantum_random_bytes(length)
        return base64.urlsafe_b64encode(random_bytes).decode('utf-8')
    
    def is_available(self):
        """
        Check if PQC and QRNG are available
        """
        # Test QRNG
        qrng_available = False
        try:
            response = requests.get(
                self.qrng_api_url,
                params={'length': 1, 'type': 'uint8'},
                timeout=2
            )
            qrng_available = response.status_code == 200
        except:
            pass
        
        return {
            'pqc': self.pqc_available,
            'algorithm': self.kem_algorithm if self.pqc_available else 'Fernet',
            'qrng': qrng_available,
            'qrng_source': 'ANU Quantum' if qrng_available else 'Secure Fallback'
        }


# Example usage and testing
if __name__ == "__main__":
    crypto = QuantumCrypto()
    
    # Test encryption/decryption
    plaintext = "Quantum-safe authentication system"
    print(f"Original: {plaintext}")
    
    encrypted = crypto.encrypt(plaintext)
    print(f"Encrypted: {encrypted[:50]}...")
    
    decrypted = crypto.decrypt(encrypted)
    print(f"Decrypted: {decrypted}")
    
    # Test quantum random generation
    qrn = crypto.get_quantum_random_bytes(16)
    print(f"\nQuantum Random (hex): {qrn.hex()}")
    
    # Check availability
    print(f"\nSystem Status: {crypto.is_available()}")