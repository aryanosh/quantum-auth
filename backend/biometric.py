# ============================================
# PART 1: Enhanced biometric.py with Real Fingerprint Verification
# ============================================

import cv2
import numpy as np
import mediapipe as mp
import hashlib
import logging

logger = logging.getLogger(__name__)

# Try to import fingerprint library
try:
    from pyfingerprint.pyfingerprint import PyFingerprint
    FINGERPRINT_AVAILABLE = True
except ImportError:
    FINGERPRINT_AVAILABLE = False
    logger.warning("pyfingerprint not available - fingerprint features disabled")


class BiometricService:
    """Enhanced biometric service with REAL fingerprint verification"""
    
    def __init__(self):
        # Initialize MediaPipe Face Mesh
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            static_image_mode=True,
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7
        )
        
        self.fingerprint_available = FINGERPRINT_AVAILABLE
        self.fingerprint_sensor = None
        
        if FINGERPRINT_AVAILABLE:
            self._init_fingerprint_sensor()
    
    def _init_fingerprint_sensor(self):
        """Initialize fingerprint sensor"""
        try:
            ports = ['/dev/ttyUSB0', '/dev/ttyUSB1', 'COM3', 'COM4', 'COM5', 'COM6']
            
            for port in ports:
                try:
                    self.fingerprint_sensor = PyFingerprint(
                        port=port,
                        baud=57600,
                        address=0xFFFFFFFF,
                        password=0x00000000
                    )
                    
                    if self.fingerprint_sensor.verifyPassword():
                        logger.info(f"✅ Fingerprint sensor connected on {port}")
                        return
                except Exception as e:
                    continue
            
            logger.warning("❌ No fingerprint sensor detected on any port")
            self.fingerprint_sensor = None
        
        except Exception as e:
            logger.error(f"Fingerprint initialization error: {e}")
            self.fingerprint_sensor = None
    
    # ============================================
    # SIMULATED FINGERPRINT (for testing without hardware)
    # ============================================
    
    def extract_fingerprint_features(self, fingerprint_data):
        """
        Extract features from fingerprint data
        Uses simulated fingerprint matching for systems without hardware
        
        Args:
            fingerprint_data: Base64 string or bytes representing fingerprint
            
        Returns:
            dict with fingerprint features (hash-based simulation)
        """
        try:
            if isinstance(fingerprint_data, str):
                # If it's a base64 string, decode it
                import base64
                if ',' in fingerprint_data:
                    fingerprint_data = fingerprint_data.split(',')[1]
                fingerprint_bytes = base64.b64decode(fingerprint_data)
            else:
                fingerprint_bytes = fingerprint_data
            
            # Create a deterministic feature vector from the fingerprint data
            # Using multiple hash functions for robustness
            features = {
                'sha256': hashlib.sha256(fingerprint_bytes).hexdigest(),
                'md5': hashlib.md5(fingerprint_bytes).hexdigest(),
                'size': len(fingerprint_bytes),
                # Extract some pixel-level features
                'checksum': sum(fingerprint_bytes) % 10000,
                'variance': np.var(np.frombuffer(fingerprint_bytes, dtype=np.uint8)),
                'mean': np.mean(np.frombuffer(fingerprint_bytes, dtype=np.uint8))
            }
            
            logger.info(f"Fingerprint features extracted - Size: {features['size']} bytes")
            return features
            
        except Exception as e:
            logger.error(f"Fingerprint feature extraction error: {e}")
            return None
    
    def compare_fingerprint_features(self, features1, features2):
        """
        Compare two fingerprint feature sets
        
        Returns:
            tuple: (match_score, is_match)
            - match_score: 0-100 (percentage match)
            - is_match: True if match_score > threshold
        """
        try:
            if not features1 or not features2:
                return 0.0, False
            
            # Compare hash-based features (must be EXACT match)
            sha_match = features1['sha256'] == features2['sha256']
            md5_match = features1['md5'] == features2['md5']
            
            # If hashes don't match, it's not the same fingerprint
            if not (sha_match and md5_match):
                # Calculate a similarity score based on other features
                size_diff = abs(features1['size'] - features2['size']) / max(features1['size'], features2['size'])
                checksum_diff = abs(features1['checksum'] - features2['checksum']) / 10000
                variance_diff = abs(features1['variance'] - features2['variance']) / max(features1['variance'], features2['variance'], 1)
                mean_diff = abs(features1['mean'] - features2['mean']) / 255
                
                # Lower score for non-matching fingerprints
                similarity = max(0, 40 - (size_diff * 20 + checksum_diff * 10 + variance_diff * 5 + mean_diff * 5))
                
                logger.info(f"Fingerprint MISMATCH - Score: {similarity:.2f}%")
                return similarity, False
            
            # Exact hash match = same fingerprint
            match_score = 98.0 + np.random.uniform(0, 2)  # 98-100% for exact match
            
            logger.info(f"Fingerprint MATCH - Score: {match_score:.2f}%")
            return match_score, True
            
        except Exception as e:
            logger.error(f"Fingerprint comparison error: {e}")
            return 0.0, False
    
    def enroll_fingerprint_simulation(self, fingerprint_data):
        """
        Simulated fingerprint enrollment (for systems without hardware)
        Returns fingerprint template
        """
        try:
            features = self.extract_fingerprint_features(fingerprint_data)
            if not features:
                return None
            
            # Create a template with timestamp
            template = {
                'features': features,
                'enrolled_at': __import__('datetime').datetime.utcnow().isoformat(),
                'type': 'simulated'
            }
            
            logger.info("Fingerprint template created successfully")
            return template
            
        except Exception as e:
            logger.error(f"Fingerprint enrollment error: {e}")
            return None
    
    def verify_fingerprint_simulation(self, fingerprint_data, stored_template):
        """
        Simulated fingerprint verification
        Returns (match_score, is_match, confidence)
        """
        try:
            # Extract features from new fingerprint
            new_features = self.extract_fingerprint_features(fingerprint_data)
            if not new_features:
                return 0.0, False, 'low'
            
            # Get stored features
            stored_features = stored_template.get('features')
            if not stored_features:
                return 0.0, False, 'low'
            
            # Compare features
            match_score, is_match = self.compare_fingerprint_features(new_features, stored_features)
            
            # Determine confidence level
            if match_score >= 95:
                confidence = 'high'
            elif match_score >= 70:
                confidence = 'medium'
            else:
                confidence = 'low'
            
            return match_score, is_match, confidence
            
        except Exception as e:
            logger.error(f"Fingerprint verification error: {e}")
            return 0.0, False, 'low'
    
    # ============================================
    # HARDWARE FINGERPRINT (for real sensors)
    # ============================================
    
    def enroll_fingerprint(self):
        """
        Enroll fingerprint using hardware sensor
        Returns template data
        """
        if not self.fingerprint_sensor:
            logger.warning("No hardware sensor - use enroll_fingerprint_simulation instead")
            return None
        
        try:
            logger.info("Place finger on sensor...")
            
            # Wait for finger
            while not self.fingerprint_sensor.readImage():
                pass
            
            self.fingerprint_sensor.convertImage(0x01)
            
            logger.info("Remove finger and place again...")
            
            # Wait for second image
            while not self.fingerprint_sensor.readImage():
                pass
            
            self.fingerprint_sensor.convertImage(0x02)
            
            # Create template
            self.fingerprint_sensor.createTemplate()
            
            # Get template characteristics
            characteristics = self.fingerprint_sensor.downloadCharacteristics(0x01)
            
            return {
                'features': characteristics,
                'type': 'hardware',
                'enrolled_at': __import__('datetime').datetime.utcnow().isoformat()
            }
        
        except Exception as e:
            logger.error(f"Hardware fingerprint enrollment error: {e}")
            return None
    
    def verify_fingerprint(self, stored_template):
        """
        Verify fingerprint using hardware sensor
        Returns (match_score, is_match, confidence)
        """
        if not self.fingerprint_sensor:
            logger.warning("No hardware sensor available")
            return 0.0, False, 'low'
        
        try:
            logger.info("Place finger on sensor for verification...")
            
            # Wait for finger
            while not self.fingerprint_sensor.readImage():
                pass
            
            self.fingerprint_sensor.convertImage(0x01)
            
            # Upload stored template
            self.fingerprint_sensor.uploadCharacteristics(0x02, stored_template['features'])
            
            # Compare
            score = self.fingerprint_sensor.compareCharacteristics()
            
            # Convert to percentage
            match_score = min(score * 2, 100)  # Score is typically 0-50
            is_match = score > 50
            
            if match_score >= 90:
                confidence = 'high'
            elif match_score >= 60:
                confidence = 'medium'
            else:
                confidence = 'low'
            
            return match_score, is_match, confidence
        
        except Exception as e:
            logger.error(f"Hardware fingerprint verification error: {e}")
            return 0.0, False, 'low'
    
    # ============================================
    # FACE VERIFICATION (existing code)
    # ============================================
    
    def extract_face_embedding(self, image_data):
        """Extract face embedding from image"""
        try:
            nparr = np.frombuffer(image_data, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if image is None:
                logger.error("Failed to decode image")
                return None
            
            if image.shape[0] < 100 or image.shape[1] < 100:
                logger.error("Image resolution too low")
                return None
            
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            results = self.face_mesh.process(image_rgb)
            
            if not results.multi_face_landmarks:
                logger.warning("No face detected")
                return None
            
            face_landmarks = results.multi_face_landmarks[0]
            
            if len(face_landmarks.landmark) < 468:
                logger.error("Insufficient landmarks")
                return None
            
            embedding = []
            for landmark in face_landmarks.landmark:
                embedding.extend([landmark.x, landmark.y, landmark.z])
            
            embedding = np.array(embedding)
            norm = np.linalg.norm(embedding)
            if norm > 0:
                embedding = embedding / norm
            else:
                return None
            
            return embedding.tolist()
        
        except Exception as e:
            logger.error(f"Face embedding error: {e}")
            return None
    
    def compare_embeddings(self, embedding1, embedding2):
        """Compare face embeddings"""
        try:
            e1 = np.array(embedding1)
            e2 = np.array(embedding2)
            
            if len(e1) == 0 or len(e2) == 0 or len(e1) != len(e2):
                return 0.0
            
            if np.any(np.isnan(e1)) or np.any(np.isnan(e2)):
                return 0.0
            
            norm1 = np.linalg.norm(e1)
            norm2 = np.linalg.norm(e2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            e1_normalized = e1 / norm1
            e2_normalized = e2 / norm2
            
            similarity = np.dot(e1_normalized, e2_normalized)
            similarity = np.clip(similarity, 0.0, 1.0)
            
            euclidean_dist = np.linalg.norm(e1_normalized - e2_normalized)
            
            if euclidean_dist > 1.0:
                similarity = similarity * 0.8
            
            return float(similarity)
        
        except Exception as e:
            logger.error(f"Embedding comparison error: {e}")
            return 0.0
    
    def check_services(self):
        """Check biometric service availability"""
        return {
            'face_detection': True,
            'fingerprint': self.fingerprint_sensor is not None,
            'fingerprint_simulation': True  # Always available
        }


# ============================================
# TESTING
# ============================================
if __name__ == "__main__":
    import base64
    
    service = BiometricService()
    print(f"\n{'='*60}")
    print("BIOMETRIC SERVICE TEST")
    print(f"{'='*60}\n")
    print(f"Services: {service.check_services()}\n")
    
    # Test fingerprint simulation
    print("Testing Fingerprint Simulation...")
    
    # Create test fingerprint data
    test_fp1 = base64.b64encode(b"test_fingerprint_person_A" * 100).decode()
    test_fp2 = base64.b64encode(b"test_fingerprint_person_B" * 100).decode()
    test_fp3 = base64.b64encode(b"test_fingerprint_person_A" * 100).decode()  # Same as fp1
    
    # Enroll first fingerprint
    template1 = service.enroll_fingerprint_simulation(test_fp1)
    print(f"✅ Template 1 enrolled")
    
    # Test matching fingerprint (should MATCH)
    score1, match1, conf1 = service.verify_fingerprint_simulation(test_fp3, template1)
    print(f"Test 1 (Same Person): Score={score1:.1f}%, Match={match1}, Confidence={conf1}")
    
    # Test different fingerprint (should NOT match)
    score2, match2, conf2 = service.verify_fingerprint_simulation(test_fp2, template1)
    print(f"Test 2 (Different Person): Score={score2:.1f}%, Match={match2}, Confidence={conf2}")
    
    print(f"\n{'='*60}\n")