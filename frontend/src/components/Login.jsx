import React, { useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { Shield, Eye, EyeOff, Camera, Loader2 } from 'lucide-react';
import FingerprintScanner from './FingerprintScanner';
import WebcamCapture from './WebcamCapture';
import { useAuth } from '../auth/AuthContext';

export default function Login() {
  const navigate = useNavigate();
  const location = useLocation();
  const { login, status } = useAuth();
  const [step, setStep] = useState(1); // 1: password, 2: face, 3: fingerprint
  const [formData, setFormData] = useState({
    username: '',
    password: '',
    face_image: null,
    fingerprint_data: null
  });
  const [showPassword, setShowPassword] = useState(false);
  const loading = status === 'authenticating';
  const [error, setError] = useState('');
  const [requiresBiometric, setRequiresBiometric] = useState(null);

  // Handle initial password login
  const handlePasswordLogin = async (e) => {
    e.preventDefault();
    setError('');

    try {
      const data = await login({
        username: formData.username,
        password: formData.password
      });

      if (data.success) {
        const next = location.state?.from?.pathname || '/dashboard';
        navigate(next, { replace: true });
      } else if (data.requires_biometric === 'face') {
        // Face verification required
        setRequiresBiometric('face');
        setStep(2);
      } else if (data.requires_biometric === 'fingerprint') {
        // Fingerprint verification required
        setRequiresBiometric('fingerprint');
        setStep(3);
      } else {
        setError(data.message || 'Login failed');
      }
    } catch (err) {
      console.error('Login error:', err);
      setError('Failed to connect to server. Please try again.');
    }
  };

  const handleFaceLogin = async (faceImage) => {
    setError('');

    try {
      const data = await login({
        username: formData.username,
        password: formData.password,
        face_image: faceImage
      });

      if (data.success) {
        const next = location.state?.from?.pathname || '/dashboard';
        navigate(next, { replace: true });
      } else if (data.requires_biometric === 'fingerprint') {
        // Still need fingerprint
        setRequiresBiometric('fingerprint');
        setStep(3);
      } else {
        setError(data.message || 'Face verification failed');
        setStep(1); // Go back to start
      }
    } catch (err) {
      console.error('Face login error:', err);
      setError('Face verification failed. Please try again.');
      setStep(1);
    }
  };

  // Handle fingerprint verification
  const handleFingerprintScan = async (result) => {
    if (result.success) {
      setError('');

      try {
        const data = await login({
          username: formData.username,
          password: formData.password,
          face_image: formData.face_image,
          fingerprint_data: result.data
        });

        if (data.success) {
          const next = location.state?.from?.pathname || '/dashboard';
          navigate(next, { replace: true });
        } else {
          setError(data.message || 'Fingerprint verification failed');
          setStep(1); // Go back to start
        }
      } catch (err) {
        console.error('Fingerprint login error:', err);
        setError('Fingerprint verification failed. Please try again.');
        setStep(1);
      }
    } else {
      setError(result.message || 'Fingerprint scan failed');
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
          <h1 className="text-4xl font-bold text-white mb-2">Quantum-Secure Login</h1>
          <p className="text-gray-300">Multi-factor authentication required</p>
        </div>

        {/* Progress Indicator */}
        <div className="flex items-center justify-center gap-4 mb-8">
          <div className={`flex items-center gap-2 ${step >= 1 ? 'text-green-400' : 'text-gray-500'}`}>
            <div className={`w-8 h-8 rounded-full flex items-center justify-center ${step >= 1 ? 'bg-green-500' : 'bg-gray-700'}`}>
              {step > 1 ? '✓' : '1'}
            </div>
            <span className="text-sm font-medium">Password</span>
          </div>
          
          <div className="w-8 h-0.5 bg-gray-700"></div>
          
          <div className={`flex items-center gap-2 ${step >= 2 ? 'text-blue-400' : 'text-gray-500'}`}>
            <div className={`w-8 h-8 rounded-full flex items-center justify-center ${step >= 2 ? 'bg-blue-500' : 'bg-gray-700'}`}>
              <Camera className="w-4 h-4" />
            </div>
            <span className="text-sm font-medium">Biometrics</span>
          </div>
        </div>

        {/* Error Message */}
        {error && (
          <div className="mb-6 p-4 bg-red-900 bg-opacity-50 border border-red-500 rounded-lg">
            <p className="text-red-200 text-sm">{error}</p>
          </div>
        )}

        {/* Step 1: Password */}
        {step === 1 && (
          <div className="bg-gray-800 bg-opacity-50 backdrop-blur-lg rounded-2xl shadow-2xl p-8 border border-gray-700">
            <h2 className="text-2xl font-bold text-white mb-6">Enter Credentials</h2>
            
            <form onSubmit={handlePasswordLogin} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">Username</label>
                <input
                  type="text"
                  value={formData.username}
                  onChange={(e) => setFormData({ ...formData, username: e.target.value })}
                  className="w-full px-4 py-3 bg-gray-900 border border-gray-600 rounded-lg text-white 
                           focus:outline-none focus:ring-2 focus:ring-purple-500"
                  placeholder="Enter username"
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
                    placeholder="Enter password"
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

              <button
                type="submit"
                disabled={loading}
                className="w-full bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 
                         text-white font-bold py-3 px-6 rounded-lg transition-all duration-200 
                         flex items-center justify-center gap-2 disabled:opacity-50"
              >
                {loading ? (
                  <>
                    <Loader2 className="w-5 h-5 animate-spin" />
                    Authenticating...
                  </>
                ) : (
                  <>
                    <Shield className="w-5 h-5" />
                    Login
                  </>
                )}
              </button>
            </form>

            <div className="mt-6 text-center">
              <p className="text-gray-400 text-sm">
                Don't have an account?{' '}
                <button
                  onClick={() => navigate('/register')}
                  className="text-purple-400 hover:text-purple-300 font-medium"
                >
                  Register here
                </button>
              </p>
            </div>
          </div>
        )}

        {/* Step 2: Face Verification */}
        {step === 2 && requiresBiometric === 'face' && (
          <div className="bg-gray-800 bg-opacity-50 backdrop-blur-lg rounded-2xl shadow-2xl p-8 border border-gray-700">
            <h2 className="text-2xl font-bold text-white mb-6 text-center">Face Verification Required</h2>
            
            <div className="mb-6">
              <WebcamCapture
                onCancel={() => setStep(1)}
                onCapture={(img) => {
                  setFormData(prev => ({ ...prev, face_image: img }));
                  handleFaceLogin(img);
                }}
              />
            </div>

            <div className="space-y-4">
              <button
                onClick={() => {
                  setStep(1);
                }}
                className="w-full bg-gray-700 hover:bg-gray-600 text-white font-bold py-3 px-6 rounded-lg transition-all"
              >
                ← Back
              </button>
            </div>
          </div>
        )}

        {/* Step 3: Fingerprint Verification */}
        {step === 3 && requiresBiometric === 'fingerprint' && (
          <div>
            <FingerprintScanner
              mode="verify"
              onScanComplete={handleFingerprintScan}
              storedFingerprint={null}
              username={formData.username}
            />
            
            <button
              onClick={() => setStep(1)}
              className="w-full mt-4 bg-gray-700 hover:bg-gray-600 text-white font-bold py-3 px-6 rounded-lg transition-all"
            >
              ← Back to Login
            </button>
          </div>
        )}
      </div>
    </div>
  );
}