"""
Quantum-Inspired Authentication System - Enhanced Backend with Security Monitoring
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import jwt
from datetime import datetime, timedelta
from functools import wraps
import base64
import json
import time
import logging

from config import Config
from models import db, User
from auth import AuthService
from biometric import BiometricService
from quantum_crypto import QuantumCrypto
from biometric import BiometricService
from quantum_crypto import QuantumCrypto
from utils import validate_request
from webauthn_utils import WebAuthnUtils
from webauthn.helpers import bytes_to_base64url, base64url_to_bytes
from models import db, User, WebAuthnCredential

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config.from_object(Config)
CORS(app)

# DB + Flask config
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///quantum_auth.db'  # or your preferred database
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your-secret-key-here'  # Change this to a random secret key

# Don't create a new SQLAlchemy() instance – use the one from models.py
db.init_app(app)

# Additional config
app.url_map.strict_slashes = False
app.config['TRAP_HTTP_EXCEPTIONS'] = True

# Initialize services
auth_service = AuthService()
biometric_service = BiometricService()
biometric_service = BiometricService()
quantum_crypto = QuantumCrypto()

# WebAuthn Configuration
RP_ID = 'localhost'
RP_NAME = 'Quantum Auth'
ORIGIN = 'http://localhost:3000'
webauthn_utils = WebAuthnUtils(RP_ID, RP_NAME, ORIGIN)

# Security metrics storage (in-memory for demo)
security_metrics = {
    'quantum_operations': [],
    'classical_operations': [],
    'login_attempts': [],
    'encryption_times': []
}


def token_required(f):
    """Decorator for protected routes"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')

        if not token:
            return jsonify({'success': False, 'message': 'Token is missing'}), 401

        try:
            if token.startswith('Bearer '):
                token = token[7:]
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user = User.query.get(data['user_id'])
            if not current_user:
                return jsonify({'success': False, 'message': 'User not found'}), 401
        except jwt.ExpiredSignatureError:
            return jsonify({'success': False, 'message': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'success': False, 'message': 'Invalid token'}), 401

        return f(current_user, *args, **kwargs)

    return decorated


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint with detailed status"""
    quantum_status = quantum_crypto.is_available()
    biometric_status = biometric_service.check_services()

    return jsonify({
        'success': True,
        'message': 'System operational',
        'data': {
            'quantum_crypto': {
                'algorithm': quantum_status['algorithm'],
                'pqc': quantum_status['pqc'],
                'qrng_source': quantum_status['qrng_source'],
                'qrng_active': quantum_status['qrng']
            },
            'biometric_services': biometric_status,
            'timestamp': datetime.utcnow().isoformat(),
            'total_users': User.query.count()
        }
    })


# ============================================
# SINGLE, UPDATED REGISTER ENDPOINT
# (password + face + fingerprint)
# ============================================
@app.route('/api/register', methods=['POST'])
def register():
    """Register new user with biometric data including fingerprint"""
    try:
        data = request.get_json()

        # Validate required fields
        required_fields = ['username', 'password', 'email']
        if not validate_request(data, required_fields):
            return jsonify({
                'success': False,
                'message': 'Missing required fields'
            }), 400

        # Check if user exists
        if User.query.filter_by(username=data['username']).first():
            return jsonify({
                'success': False,
                'message': 'Username already exists'
            }), 400

        if User.query.filter_by(email=data['email']).first():
            return jsonify({
                'success': False,
                'message': 'Email already exists'
            }), 400

        # Hash password
        start_time = time.time()
        password_hash = auth_service.hash_password(data['password'])
        hash_time = (time.time() - start_time) * 1000

        logger.info(f"Password hashing took {hash_time:.2f}ms")

        # Process biometric data
        face_embedding = None
        fingerprint_template = None

        # -------- FACE -----------
        if 'face_image' in data and data['face_image']:
            try:
                image_data_str = data['face_image'].split(',')[1] if ',' in data['face_image'] else data['face_image']
                face_image_data = base64.b64decode(image_data_str)
                face_embedding_obj = biometric_service.extract_face_embedding(face_image_data)

                if face_embedding_obj:
                    start_time = time.time()
                    face_embedding = quantum_crypto.encrypt(json.dumps(face_embedding_obj))
                    encrypt_time = (time.time() - start_time) * 1000
                    logger.info(f"Face encryption took {encrypt_time:.2f}ms")

                    security_metrics['encryption_times'].append({
                        'timestamp': datetime.utcnow().isoformat(),
                        'operation': 'face_encryption',
                        'time_ms': encrypt_time,
                        'method': 'quantum' if quantum_crypto.pqc_available else 'classical'
                    })
                else:
                    logger.warning("Face detection failed during registration")
            except Exception as e:
                logger.error(f"Face processing error: {e}")

        # -------- FINGERPRINT -----------
        if 'fingerprint_data' in data and data['fingerprint_data']:
            try:
                fingerprint_data = data['fingerprint_data']

                # Simulated fingerprint enrollment
                fingerprint_template_obj = biometric_service.enroll_fingerprint_simulation(fingerprint_data)

                if fingerprint_template_obj:
                    start_time = time.time()
                    fingerprint_template = quantum_crypto.encrypt(json.dumps(fingerprint_template_obj))
                    encrypt_time = (time.time() - start_time) * 1000

                    logger.info(f"✅ Fingerprint enrolled and encrypted in {encrypt_time:.2f}ms")

                    security_metrics['encryption_times'].append({
                        'timestamp': datetime.utcnow().isoformat(),
                        'operation': 'fingerprint_encryption',
                        'time_ms': encrypt_time,
                        'method': 'quantum' if quantum_crypto.pqc_available else 'classical'
                    })
                else:
                    logger.warning("❌ Fingerprint enrollment failed")
            except Exception as e:
                logger.error(f"Fingerprint processing error: {e}")

        # Create new user
        new_user = User(
            username=data['username'],
            email=data['email'],
            password_hash=password_hash,
            face_embedding=face_embedding,
            fingerprint_template=fingerprint_template
        )

        db.session.add(new_user)
        db.session.commit()

        # Generate token
        token = auth_service.generate_token(new_user.id, app.config['SECRET_KEY'])

        logger.info(f"User registered: {new_user.username}")

        return jsonify({
            'success': True,
            'message': 'User registered successfully',
            'token': token,
            'data': {
                'user_id': new_user.id,
                'username': new_user.username,
                'email': new_user.email,
                'created_at': new_user.created_at.isoformat(),
                'biometrics_registered': {
                    'face': face_embedding is not None,
                    'fingerprint': fingerprint_template is not None
                },
                'security_info': {
                    'password_hash_time_ms': hash_time,
                    'hash_algorithm': 'Argon2id',
                    'encryption_method': 'Kyber-768' if quantum_crypto.pqc_available else 'Fernet-AES256'
                }
            }
        }), 201

    except Exception as e:
        db.session.rollback()
        logger.error(f"Registration failed: {e}")
        return jsonify({
            'success': False,
            'message': f'Registration failed: {str(e)}'
        }), 500


# ============================================
# UPDATED LOGIN ENDPOINT (with fingerprint)
# ============================================
@app.route('/api/login', methods=['POST'])
def login():
    """Authenticate user with password + biometric data"""
    start_time = time.time()

    try:
        data = request.get_json()

        # Validate required fields
        if not validate_request(data, ['username', 'password']):
            return jsonify({
                'success': False,
                'message': 'Missing username or password'
            }), 400

        # Find user
        user = User.query.filter_by(username=data['username']).first()

        if not user:
            logger.warning(f"Login failed: User {data['username']} not found")
            security_metrics['login_attempts'].append({
                'timestamp': datetime.utcnow().isoformat(),
                'username': data['username'],
                'success': False
            })
            return jsonify({
                'success': False,
                'message': 'Invalid username or password'
            }), 401

        # Verify password
        password_verify_start = time.time()
        password_valid = auth_service.verify_password(data['password'], user.password_hash)
        password_verify_time = (time.time() - password_verify_start) * 1000

        if not password_valid:
            logger.warning(f"Login failed: Invalid password for {data['username']}")
            security_metrics['login_attempts'].append({
                'timestamp': datetime.utcnow().isoformat(),
                'username': data['username'],
                'success': False
            })
            return jsonify({
                'success': False,
                'message': 'Invalid username or password'
            }), 401

        biometric_scores = {'password': True}
        face_verified = False
        fingerprint_verified = False

        # -------- FACE VERIFICATION ----------
        if user.face_embedding:
            if not data.get('face_image'):
                return jsonify({
                    'success': False,
                    'message': 'Face verification required. Please enable camera.',
                    'requires_biometric': 'face'
                }), 401

            try:
                image_data_str = data['face_image'].split(',')[1] if ',' in data['face_image'] else data['face_image']
                face_image_data = base64.b64decode(image_data_str)
                login_embedding = biometric_service.extract_face_embedding(face_image_data)

                if not login_embedding:
                    return jsonify({
                        'success': False,
                        'message': 'No face detected. Please ensure face is visible.'
                    }), 401

                stored_embedding = json.loads(quantum_crypto.decrypt(user.face_embedding))
                similarity = biometric_service.compare_embeddings(login_embedding, stored_embedding)
                biometric_scores['face'] = similarity

                FACE_THRESHOLD = 0.80

                if similarity < FACE_THRESHOLD:
                    logger.warning(f"Face verification FAILED: {similarity:.4f} < {FACE_THRESHOLD}")
                    return jsonify({
                        'success': False,
                        'message': f'Face verification failed. Score: {similarity:.2%}',
                        'similarity_score': float(similarity)
                    }), 401

                face_verified = True
                logger.info(f"✅ Face verified: {similarity:.4f}")

            except Exception as e:
                logger.error(f"Face verification error: {e}")
                return jsonify({
                    'success': False,
                    'message': f'Face verification failed: {str(e)}'
                }), 401

        # -------- FINGERPRINT VERIFICATION ----------
        if user.fingerprint_template:
            if not data.get('fingerprint_data'):
                return jsonify({
                    'success': False,
                    'message': 'Fingerprint verification required. Please scan fingerprint.',
                    'requires_biometric': 'fingerprint'
                }), 401

            try:
                fingerprint_data = data['fingerprint_data']

                # Decrypt stored template
                decrypt_start = time.time()
                stored_template = json.loads(quantum_crypto.decrypt(user.fingerprint_template))
                decrypt_time = (time.time() - decrypt_start) * 1000

                logger.info(f"Fingerprint template decryption took {decrypt_time:.2f}ms")

                match_score, is_match, confidence = biometric_service.verify_fingerprint_simulation(
                    fingerprint_data,
                    stored_template
                )

                biometric_scores['fingerprint'] = match_score
                biometric_scores['fingerprint_confidence'] = confidence

                logger.info(
                    f"Fingerprint verification: Score={match_score:.1f}%, "
                    f"Match={is_match}, Confidence={confidence}"
                )

                if not is_match or match_score < 95:
                    logger.warning(
                        f"❌ Fingerprint verification FAILED: Score={match_score:.1f}%, Match={is_match}"
                    )
                    return jsonify({
                        'success': False,
                        'message': f'Fingerprint verification failed. Match score: {match_score:.1f}%',
                        'match_score': match_score,
                        'is_match': is_match,
                        'confidence': confidence
                    }), 401

                fingerprint_verified = True
                logger.info(f"✅ Fingerprint verified: Score={match_score:.1f}%, Confidence={confidence}")

            except Exception as e:
                logger.error(f"Fingerprint verification error: {e}")
                return jsonify({
                    'success': False,
                    'message': f'Fingerprint verification failed: {str(e)}'
                }), 401

        # Update last login
        user.last_login = datetime.utcnow()
        db.session.commit()

        # Generate token
        token = auth_service.generate_token(user.id, app.config['SECRET_KEY'])

        total_time = (time.time() - start_time) * 1000

        auth_method = 'password'
        if face_verified and fingerprint_verified:
            auth_method = 'password + face + fingerprint'
        elif face_verified:
            auth_method = 'password + face'
        elif fingerprint_verified:
            auth_method = 'password + fingerprint'

        logger.info(f"✅ Login SUCCESSFUL for {user.username} using {auth_method} in {total_time:.2f}ms")

        security_metrics['login_attempts'].append({
            'timestamp': datetime.utcnow().isoformat(),
            'username': user.username,
            'success': True,
            'auth_method': auth_method
        })

        return jsonify({
            'success': True,
            'message': 'Login successful',
            'token': token,
            'data': {
                'user_id': user.id,
                'username': user.username,
                'email': user.email,
                'biometric_verification': biometric_scores,
                'last_login': user.last_login.isoformat(),
                'security_info': {
                    'password_verify_time_ms': password_verify_time,
                    'total_auth_time_ms': total_time,
                    'face_verified': face_verified,
                    'fingerprint_verified': fingerprint_verified,
                    'authentication_method': auth_method
                }
            }
        })

    except Exception as e:
        logger.error(f"Login error: {e}")
        return jsonify({
            'success': False,
            'message': f'Login failed: {str(e)}'
        }), 500


# ============================================
# WEBAUTHN ENDPOINTS
# ============================================

@app.route('/api/webauthn/register/begin', methods=['POST'])
@token_required
def webauthn_register_begin(current_user):
    """Generate WebAuthn registration options"""
    try:
        # Get existing credentials to exclude
        existing_creds = []
        for cred in current_user.webauthn_credentials:
            existing_creds.append(WebAuthnCredential.credential_id)
            
        # Generate options
        options = webauthn_utils.generate_registration_options(current_user, existing_creds)
        
        # Store challenge in session (or cache) - for demo using a global dict (NOT PROD SAFE)
        # In production, use Redis or server-side session
        # For this simple app, we'll return it and expect client to send it back (stateless-ish)
        # BUT verify_registration_response needs the original challenge.
        # We'll use a simple in-memory store for this demo.
        session_key = f"reg_challenge_{current_user.id}"
        app.config[session_key] = options.challenge
        
        return jsonify({
            'success': True,
            'options': json.loads(options.json())
        })
    except Exception as e:
        logger.error(f"WebAuthn register begin error: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/webauthn/register/complete', methods=['POST'])
@token_required
def webauthn_register_complete(current_user):
    """Verify WebAuthn registration"""
    try:
        data = request.get_json()
        
        # Retrieve challenge
        session_key = f"reg_challenge_{current_user.id}"
        challenge = app.config.get(session_key)
        
        if not challenge:
            return jsonify({'success': False, 'message': 'Challenge expired or invalid'}), 400
            
        # Verify
        verification = webauthn_utils.verify_registration_response(
            credential_response=data,
            challenge=challenge
        )
        
        # Save credential
        credential_id = verification.credential_id
        public_key = verification.credential_public_key
        sign_count = verification.sign_count
        
        new_cred = WebAuthnCredential(
            user_id=current_user.id,
            credential_id=credential_id,
            public_key=public_key,
            sign_count=sign_count,
            transports=json.dumps(data.get('response', {}).get('transports', []))
        )
        
        db.session.add(new_cred)
        current_user.fingerprint_template = "WEBAUTHN_ENABLED" # Marker
        db.session.commit()
        
        # Cleanup
        app.config.pop(session_key, None)
        
        return jsonify({
            'success': True, 
            'message': 'Fingerprint registered successfully'
        })
        
    except Exception as e:
        logger.error(f"WebAuthn register complete error: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/webauthn/login/begin', methods=['POST'])
def webauthn_login_begin():
    """Generate WebAuthn login options"""
    try:
        data = request.get_json()
        username = data.get('username')
        
        user = User.query.filter_by(username=username).first()
        if not user:
            return jsonify({'success': False, 'message': 'User not found'}), 404
            
        # Get user's credentials
        credentials = []
        for cred in user.webauthn_credentials:
            credentials.append(cred.credential_id)
            
        if not credentials:
            return jsonify({'success': False, 'message': 'No fingerprint registered for this user'}), 400
            
        # Generate options
        options = webauthn_utils.generate_authentication_options(credentials)
        
        # Store challenge
        session_key = f"auth_challenge_{username}"
        app.config[session_key] = options.challenge
        
        return jsonify({
            'success': True,
            'options': json.loads(options.json())
        })
        
    except Exception as e:
        logger.error(f"WebAuthn login begin error: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/webauthn/login/complete', methods=['POST'])
def webauthn_login_complete():
    """Verify WebAuthn login"""
    try:
        data = request.get_json()
        username = data.get('username')
        
        user = User.query.filter_by(username=username).first()
        if not user:
            return jsonify({'success': False, 'message': 'User not found'}), 404
            
        # Retrieve challenge
        session_key = f"auth_challenge_{username}"
        challenge = app.config.get(session_key)
        
        if not challenge:
            return jsonify({'success': False, 'message': 'Challenge expired'}), 400

        # Find the credential used
        credential_id_b64 = data.get('id')
        credential_id = base64url_to_bytes(credential_id_b64)
        
        stored_cred = WebAuthnCredential.query.filter_by(credential_id=credential_id).first()
        if not stored_cred:
             return jsonify({'success': False, 'message': 'Unknown credential'}), 400
             
        # Verify
        verification = webauthn_utils.verify_authentication_response(
            credential_response=data,
            challenge=challenge,
            public_key=stored_cred.public_key,
            sign_count=stored_cred.sign_count
        )
        
        # Update sign count
        stored_cred.sign_count = verification.new_sign_count
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        # Generate token
        token = auth_service.generate_token(user.id, app.config['SECRET_KEY'])
        
        app.config.pop(session_key, None)
        
        return jsonify({
            'success': True,
            'token': token,
            'username': user.username,
            'message': 'Fingerprint login successful'
        })
        
    except Exception as e:
        logger.error(f"WebAuthn login complete error: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


# ============================================
# NEW: FINGERPRINT TEST ENDPOINT
# ============================================
@app.route('/api/test-fingerprint', methods=['POST'])
def test_fingerprint():
    """Test endpoint to verify fingerprint matching works correctly"""
    try:
        data = request.get_json()

        if 'fingerprint1' not in data or 'fingerprint2' not in data:
            return jsonify({
                'success': False,
                'message': 'Both fingerprint1 and fingerprint2 required'
            }), 400

        # Enroll first fingerprint
        template = biometric_service.enroll_fingerprint_simulation(data['fingerprint1'])

        if not template:
            return jsonify({
                'success': False,
                'message': 'Failed to enroll fingerprint1'
            }), 400

        # Verify second fingerprint against first
        match_score, is_match, confidence = biometric_service.verify_fingerprint_simulation(
            data['fingerprint2'],
            template
        )

        return jsonify({
            'success': True,
            'data': {
                'match_score': match_score,
                'is_match': is_match,
                'confidence': confidence,
                'interpretation': 'MATCH - Same fingerprint' if is_match else 'NO MATCH - Different fingerprint'
            }
        })

    except Exception as e:
        logger.error(f"Fingerprint test error: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@app.route('/api/user', methods=['GET'])
@token_required
def get_user(current_user):
    """Get current user information"""
    return jsonify({
        'success': True,
        'data': {
            'user_id': current_user.id,
            'username': current_user.username,
            'email': current_user.email,
            'created_at': current_user.created_at.isoformat(),
            'last_login': current_user.last_login.isoformat() if current_user.last_login else None,
            'biometrics_registered': {
                'face': current_user.face_embedding is not None,
                'fingerprint': getattr(current_user, 'fingerprint_template', None) is not None
            }
        }
    })


@app.route('/api/user/delete', methods=['DELETE'])
@token_required
def delete_user(current_user):
    """Delete user account"""
    try:
        username = current_user.username
        db.session.delete(current_user)
        db.session.commit()

        logger.info(f"User deleted: {username}")

        return jsonify({
            'success': True,
            'message': 'Account deleted successfully'
        })
    except Exception as e:
        db.session.rollback()
        logger.error(f"Delete failed: {e}")
        return jsonify({
            'success': False,
            'message': f'Delete failed: {str(e)}'
        }), 500


@app.route('/api/admin/users', methods=['GET'])
def get_all_users():
    """Get all users (admin endpoint - should be protected in production)"""
    try:
        users = User.query.all()
        users_list = []

        for user in users:
            users_list.append({
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'created_at': user.created_at.isoformat(),
                'last_login': user.last_login.isoformat() if user.last_login else None,
                'biometrics': {
                    'face': user.face_embedding is not None,
                    'fingerprint': getattr(user, 'fingerprint_template', None) is not None
                }
            })

        return jsonify({
            'success': True,
            'data': {
                'total_users': len(users_list),
                'users': users_list
            }
        })
    except Exception as e:
        logger.error(f"Failed to fetch users: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@app.route('/api/security/metrics', methods=['GET'])
def get_security_metrics():
    """Get security metrics for visualization"""
    try:
        quantum_status = quantum_crypto.is_available()

        recent_encryptions = security_metrics['encryption_times'][-50:]
        quantum_times = [e['time_ms'] for e in recent_encryptions if e.get('method') == 'quantum']
        classical_times = [e['time_ms'] for e in recent_encryptions if e.get('method') == 'classical']

        recent_logins = security_metrics['login_attempts'][-20:]
        successful_logins = len([l for l in recent_logins if l['success']])
        failed_logins = len(recent_logins) - successful_logins

        return jsonify({
            'success': True,
            'data': {
                'quantum_status': quantum_status,
                'encryption_metrics': {
                    'quantum_avg_ms': sum(quantum_times) / len(quantum_times) if quantum_times else 0,
                    'classical_avg_ms': sum(classical_times) / len(classical_times) if classical_times else 0,
                    'total_operations': len(recent_encryptions)
                },
                'login_metrics': {
                    'total_attempts': len(recent_logins),
                    'successful': successful_logins,
                    'failed': failed_logins,
                    'success_rate': (successful_logins / len(recent_logins) * 100) if recent_logins else 0
                },
                'security_comparison': {
                    'quantum_features': [
                        {'name': 'Key Encapsulation', 'quantum': 'Kyber-768', 'classical': 'RSA-2048'},
                        {'name': 'Random Generation', 'quantum': 'ANU QRNG', 'classical': 'PRNG'},
                        {'name': 'Password Hashing', 'quantum': 'Argon2id', 'classical': 'bcrypt'},
                        {'name': 'Encryption', 'quantum': 'AES-256', 'classical': 'AES-128'}
                    ],
                    'strength_scores': {
                        'quantum_resistant': 95,
                        'classical_security': 70,
                        'brute_force_resistance': 98,
                        'side_channel_resistance': 85
                    }
                },
                'recent_activity': recent_logins
            }
        })
    except Exception as e:
        logger.error(f"Failed to fetch metrics: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@app.route('/api/security/test-quantum', methods=['POST'])
def test_quantum():
    """Test quantum operations and compare with classical"""
    try:
        test_data = "Test encryption data for comparison"
        results = {
            'quantum_operations': [],
            'classical_operations': []
        }

        # Test quantum encryption
        for i in range(5):
            start = time.time()
            encrypted = quantum_crypto.encrypt(test_data)
            encrypt_time = (time.time() - start) * 1000

            start = time.time()
            decrypted = quantum_crypto.decrypt(encrypted)
            decrypt_time = (time.time() - start) * 1000

            results['quantum_operations'].append({
                'iteration': i + 1,
                'encrypt_ms': encrypt_time,
                'decrypt_ms': decrypt_time,
                'total_ms': encrypt_time + decrypt_time,
                'success': decrypted == test_data
            })

        # Quantum random numbers
        qrng_samples = []
        for i in range(3):
            start = time.time()
            random_bytes = quantum_crypto.get_quantum_random_bytes(32)
            time_ms = (time.time() - start) * 1000
            qrng_samples.append({
                'iteration': i + 1,
                'time_ms': time_ms,
                'bytes_hex': random_bytes.hex()[:32] + '...'
            })

        return jsonify({
            'success': True,
            'data': {
                'encryption_tests': results,
                'qrng_samples': qrng_samples,
                'quantum_status': quantum_crypto.is_available(),
                'average_encrypt_ms': sum(op['encrypt_ms'] for op in results['quantum_operations']) / 5,
                'average_decrypt_ms': sum(op['decrypt_ms'] for op in results['quantum_operations']) / 5
            }
        })
    except Exception as e:
        logger.error(f"Quantum test failed: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
