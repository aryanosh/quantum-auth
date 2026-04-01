import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Shield, Eye, EyeOff, Loader2, Mail, User } from 'lucide-react';
import FingerprintScanner from './FingerprintScanner';
import WebcamCapture from './WebcamCapture';
import { useAuth } from '../auth/AuthContext';

export default function Register() {
  const navigate = useNavigate();
  const { register, status } = useAuth();
  const [step, setStep] = useState(1); // 1: form, 2: face, 3: fingerprint, 4: success
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    confirmPassword: '',
    face_image: null,
    fingerprint_data: null
  });
  const [showPassword, setShowPassword] = useState(false);
  const loading = status === 'authenticating';
  const [error, setError] = useState('');

  // Validate form
  const validateForm = () => {
    if (formData.username.length < 3) {
      setError('Username must be at least 3 characters');
      return false;
    }
    if (!formData.email.includes('@')) {
      setError('Please enter a valid email');
      return false;
    }
    if (formData.password.length < 8) {
      setError('Password must be at least 8 characters');
      return false;
    }
    if (formData.password !== formData.confirmPassword) {
      setError('Passwords do not match');
      return false;
    }
    return true;
  };

  // Handle form submission (step 1)
  const handleFormSubmit = (e) => {
    e.preventDefault();
    setError('');
    
    if (validateForm()) {
      setStep(2); // Move to face capture
    }
  };

  // Skip face capture
  const skipFace = () => {
    setStep(3);
  };

  // Handle fingerprint scan
  const handleFingerprintScan = (result) => {
    if (result.success) {
      setFormData(prev => ({ ...prev, fingerprint_data: result.data }));
      // Submit registration
      handleRegisterSubmit(result.data);
    } else {
      setError(result.message || 'Fingerprint scan failed');
    }
  };

  // Skip fingerprint
  const skipFingerprint = () => {
    handleRegisterSubmit(null);
  };

  // Submit registration
  const handleRegisterSubmit = async (fingerprintData) => {
    setError('');

    try {
      const data = await register({
        username: formData.username,
        email: formData.email,
        password: formData.password,
        face_image: formData.face_image,
        fingerprint_data: fingerprintData || formData.fingerprint_data
      });

      if (data.success) {
        setStep(4); // Success screen
        
        setTimeout(() => {
          navigate('/dashboard');
        }, 2000);
      } else {
        setError(data.message || 'Registration failed');
        setStep(1);
      }
    } catch (err) {
      console.error('Registration error:', err);
      setError('Failed to connect to server. Please try again.');
      setStep(1);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-900 via-indigo-900 to-blue-900 flex items-center justify-center p-4">
      <div className="max-w-md w-full">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-20 h-20 bg-gradient-to-r from-pink-500 to-purple-500 rounded-full mb-4">
            <Shield className="w-10 h-10 text-white" />
          </div>
          <h1 className="text-4xl font-bold text-white mb-2">Create Account</h1>
          <p className="text-gray-300">Quantum-secure registration</p>
        </div>

        {/* Progress Indicator */}
        <div className="flex items-center justify-center gap-2 mb-8">
          <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold ${step >= 1 ? 'bg-green-500 text-white' : 'bg-gray-700 text-gray-400'}`}>
            {step > 1 ? '✓' : '1'}
          </div>
          <div className="w-8 h-0.5 bg-gray-700"></div>
          <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold ${step >= 2 ? 'bg-blue-500 text-white' : 'bg-gray-700 text-gray-400'}`}>
            {step > 2 ? '✓' : '2'}
          </div>
          <div className="w-8 h-0.5 bg-gray-700"></div>
          <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold ${step >= 3 ? 'bg-purple-500 text-white' : 'bg-gray-700 text-gray-400'}`}>
            {step > 3 ? '✓' : '3'}
          </div>
        </div>

        {/* Error Message */}
        {error && (
          <div className="mb-6 p-4 bg-red-900 bg-opacity-50 border border-red-500 rounded-lg">
            <p className="text-red-200 text-sm">{error}</p>
          </div>
        )}

        {/* Step 1: Basic Info */}
        {step === 1 && (
          <div className="bg-gray-800 bg-opacity-50 backdrop-blur-lg rounded-2xl shadow-2xl p-8 border border-gray-700">
            <h2 className="text-2xl font-bold text-white mb-6">Basic Information</h2>
            
            <form onSubmit={handleFormSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  <User className="w-4 h-4 inline mr-2" />
                  Username
                </label>
                <input
                  type="text"
                  value={formData.username}
                  onChange={(e) => setFormData({ ...formData, username: e.target.value })}
                  className="w-full px-4 py-3 bg-gray-900 border border-gray-600 rounded-lg text-white 
                           focus:outline-none focus:ring-2 focus:ring-purple-500"
                  placeholder="Choose a username"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  <Mail className="w-4 h-4 inline mr-2" />
                  Email
                </label>
                <input
                  type="email"
                  value={formData.email}
                  onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                  className="w-full px-4 py-3 bg-gray-900 border border-gray-600 rounded-lg text-white 
                           focus:outline-none focus:ring-2 focus:ring-purple-500"
                  placeholder="your@email.com"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">Password</label>
                <div className="relative">
                  <input
                    type={showPassword ? 'text' : 'password'}
                    value={formData.password}
                    onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                    className="w-full px-4 py-3 bg-gray-900 border border-gray-600 rounded-lg text-white 
                             focus:outline-none focus:ring-2 focus:ring-purple-500 pr-12"
                    placeholder="Min. 8 characters"
                    required
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-white"
                  >
                    {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                  </button>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">Confirm Password</label>
                <input
                  type="password"
                  value={formData.confirmPassword}
                  onChange={(e) => setFormData({ ...formData, confirmPassword: e.target.value })}
                  className="w-full px-4 py-3 bg-gray-900 border border-gray-600 rounded-lg text-white 
                           focus:outline-none focus:ring-2 focus:ring-purple-500"
                  placeholder="Re-enter password"
                  required
                />
              </div>

              <button
                type="submit"
                className="w-full bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 
                         text-white font-bold py-3 px-6 rounded-lg transition-all duration-200"
              >
                Next: Face Capture →
              </button>
            </form>

            <div className="mt-6 text-center">
              <p className="text-gray-400 text-sm">
                Already have an account?{' '}
                <button
                  onClick={() => navigate('/login')}
                  className="text-purple-400 hover:text-purple-300 font-medium"
                >
                  Login here
                </button>
              </p>
            </div>
          </div>
        )}

        {/* Step 2: Face Capture */}
        {step === 2 && (
          <div className="bg-gray-800 bg-opacity-50 backdrop-blur-lg rounded-2xl shadow-2xl p-8 border border-gray-700">
            <h2 className="text-2xl font-bold text-white mb-6 text-center">Face Enrollment (Optional)</h2>

            <div className="mb-6">
              <WebcamCapture
                onCancel={() => setStep(1)}
                onCapture={(img) => {
                  setFormData(prev => ({ ...prev, face_image: img }));
                  setStep(3);
                }}
              />
            </div>

            <div className="space-y-3">
              <button
                onClick={skipFace}
                className="w-full bg-gray-700 hover:bg-gray-600 text-white font-bold py-3 px-6 rounded-lg transition-all"
              >
                Skip (Not Recommended)
              </button>

              <button
                onClick={() => {
                  setStep(1);
                }}
                className="w-full bg-gray-800 hover:bg-gray-700 text-white py-2 px-4 rounded-lg transition-all text-sm"
              >
                ← Back
              </button>
            </div>
          </div>
        )}

        {/* Step 3: Fingerprint */}
        {step === 3 && (
          <div>
            <FingerprintScanner
              mode="enroll"
              onScanComplete={handleFingerprintScan}
            />
            
            <div className="mt-4 space-y-2">
              <button
                onClick={skipFingerprint}
                disabled={loading}
                className="w-full bg-gray-700 hover:bg-gray-600 text-white font-bold py-3 px-6 rounded-lg transition-all disabled:opacity-50"
              >
                {loading ? 'Registering...' : 'Skip (Not Recommended)'}
              </button>

              <button
                onClick={() => setStep(2)}
                className="w-full bg-gray-800 hover:bg-gray-700 text-white py-2 px-4 rounded-lg transition-all text-sm"
              >
                ← Back
              </button>
            </div>
          </div>
        )}

        {/* Step 4: Success */}
        {step === 4 && (
          <div className="bg-gray-800 bg-opacity-50 backdrop-blur-lg rounded-2xl shadow-2xl p-8 border border-gray-700 text-center">
            <div className="inline-flex items-center justify-center w-20 h-20 bg-green-500 rounded-full mb-6">
              <Shield className="w-10 h-10 text-white" />
            </div>
            <h2 className="text-3xl font-bold text-white mb-4">Registration Successful!</h2>
            <p className="text-gray-300 mb-6">
              Your quantum-secure account has been created.
              <br />
              Redirecting to dashboard...
            </p>
            <Loader2 className="w-8 h-8 animate-spin text-purple-500 mx-auto" />
          </div>
        )}
      </div>
    </div>
  );
}