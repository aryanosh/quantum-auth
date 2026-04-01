import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Shield, User, Mail, Clock, Fingerprint, Camera, LogOut, Key, Cpu, Dices, Settings as SettingsIcon } from 'lucide-react';
import api from '../services/api';
import { useAuth } from '../auth/AuthContext';

export default function Dashboard() {
  const navigate = useNavigate();
  const { user, logout, loadUser } = useAuth();
  const [loading, setLoading] = useState(true);
  const [health, setHealth] = useState(null);

  useEffect(() => {
    let cancelled = false;
    async function boot() {
      try {
        await loadUser();
        const h = await api.checkHealth();
        if (!cancelled) setHealth(h?.success ? h.data : null);
      } catch (e) {
        if (!cancelled) setHealth(null);
      } finally {
        if (!cancelled) setLoading(false);
      }
    }
    boot();
    return () => {
      cancelled = true;
    };
  }, [loadUser]);

  const handleLogout = () => {
    logout();
    navigate('/login', { replace: true });
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-purple-900 via-indigo-900 to-blue-900 flex items-center justify-center">
        <div className="text-white text-xl">Loading...</div>
      </div>
    );
  }

  if (!user) {
    return null;
  }

  const biometrics = user.biometric_verification || {};
  const securityInfo = user.security_info || {};
  const qc = health?.quantum_crypto || null;
  const enrolled = user.biometrics_registered || {};

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-900 via-indigo-900 to-blue-900 p-8">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="bg-gray-800 bg-opacity-50 backdrop-blur-lg rounded-2xl shadow-2xl p-8 border border-gray-700 mb-8">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="w-16 h-16 bg-gradient-to-r from-pink-500 to-purple-500 rounded-full flex items-center justify-center">
                <User className="w-8 h-8 text-white" />
              </div>
              <div>
                <h1 className="text-3xl font-bold text-white">{user.username}</h1>
                <p className="text-gray-300 flex items-center gap-2">
                  <Mail className="w-4 h-4" />
                  {user.email}
                </p>
              </div>
            </div>
            <button
              onClick={handleLogout}
              className="flex items-center gap-2 px-6 py-3 bg-red-600 hover:bg-red-700 text-white rounded-lg transition-all"
            >
              <LogOut className="w-5 h-5" />
              Logout
            </button>
          </div>
        </div>

        {/* Platform Security Status */}
        <div className="grid md:grid-cols-3 gap-6 mb-8">
          <div className="bg-gray-800 bg-opacity-50 backdrop-blur-lg rounded-xl shadow-xl p-6 border border-gray-700">
            <div className="flex items-center gap-3 mb-3">
              <Cpu className="w-6 h-6 text-purple-300" />
              <h2 className="text-lg font-bold text-white">PQC</h2>
            </div>
            <p className="text-gray-300 text-sm">Encryption algorithm</p>
            <p className="text-white font-semibold mt-2">
              {qc?.pqc ? 'Kyber enabled' : 'Fallback to Fernet'}
            </p>
            {qc?.algorithm && (
              <p className="text-gray-400 text-xs mt-1">{qc.algorithm}</p>
            )}
          </div>

          <div className="bg-gray-800 bg-opacity-50 backdrop-blur-lg rounded-xl shadow-xl p-6 border border-gray-700">
            <div className="flex items-center gap-3 mb-3">
              <Dices className="w-6 h-6 text-blue-300" />
              <h2 className="text-lg font-bold text-white">QRNG</h2>
            </div>
            <p className="text-gray-300 text-sm">Randomness source</p>
            <p className="text-white font-semibold mt-2">
              {qc?.qrng_active ? 'Quantum RNG OK' : 'Secure local fallback'}
            </p>
            {qc?.qrng_source && (
              <p className="text-gray-400 text-xs mt-1">{qc.qrng_source}</p>
            )}
          </div>

          <div className="bg-gray-800 bg-opacity-50 backdrop-blur-lg rounded-xl shadow-xl p-6 border border-gray-700">
            <div className="flex items-center gap-3 mb-3">
              <Shield className="w-6 h-6 text-green-300" />
              <h2 className="text-lg font-bold text-white">Biometrics</h2>
            </div>
            <p className="text-gray-300 text-sm">Enrollment state</p>
            <p className="text-white font-semibold mt-2">
              {enrolled.face ? 'Face enrolled' : 'Face not enrolled'}
            </p>
            <p className="text-gray-400 text-xs mt-1">
              {enrolled.fingerprint ? 'Fingerprint enrolled' : 'Fingerprint not enrolled'}
            </p>
          </div>
        </div>

        {/* Security Status */}
        <div className="grid md:grid-cols-2 gap-6 mb-8">
          {/* Biometric Status */}
          <div className="bg-gray-800 bg-opacity-50 backdrop-blur-lg rounded-xl shadow-xl p-6 border border-gray-700">
            <div className="flex items-center gap-3 mb-4">
              <Shield className="w-6 h-6 text-green-400" />
              <h2 className="text-xl font-bold text-white">Biometric Security</h2>
            </div>

            <div className="space-y-3">
              <div className="flex items-center justify-between p-3 bg-gray-900 bg-opacity-50 rounded-lg">
                <div className="flex items-center gap-2">
                  <Camera className="w-5 h-5 text-blue-400" />
                  <span className="text-gray-300">Face Recognition</span>
                </div>
                {biometrics.face !== undefined ? (
                  <span className="px-3 py-1 bg-green-900 text-green-300 rounded-full text-sm font-medium">
                    {biometrics.face >= 0.80 ? '✓ Active' : '⚠ Low'}
                  </span>
                ) : (
                  <span className="px-3 py-1 bg-gray-700 text-gray-400 rounded-full text-sm">
                    Not Set
                  </span>
                )}
              </div>

              <div className="flex items-center justify-between p-3 bg-gray-900 bg-opacity-50 rounded-lg">
                <div className="flex items-center gap-2">
                  <Fingerprint className="w-5 h-5 text-purple-400" />
                  <span className="text-gray-300">Fingerprint</span>
                </div>
                {biometrics.fingerprint !== undefined ? (
                  <span className="px-3 py-1 bg-green-900 text-green-300 rounded-full text-sm font-medium">
                    ✓ Active
                  </span>
                ) : (
                  <span className="px-3 py-1 bg-gray-700 text-gray-400 rounded-full text-sm">
                    Not Set
                  </span>
                )}
              </div>

              <div className="flex items-center justify-between p-3 bg-gray-900 bg-opacity-50 rounded-lg">
                <div className="flex items-center gap-2">
                  <Key className="w-5 h-5 text-yellow-400" />
                  <span className="text-gray-300">Password</span>
                </div>
                <span className="px-3 py-1 bg-green-900 text-green-300 rounded-full text-sm font-medium">
                  ✓ Active
                </span>
              </div>
            </div>
          </div>

          {/* Account Info */}
          <div className="bg-gray-800 bg-opacity-50 backdrop-blur-lg rounded-xl shadow-xl p-6 border border-gray-700">
            <div className="flex items-center gap-3 mb-4">
              <User className="w-6 h-6 text-blue-400" />
              <h2 className="text-xl font-bold text-white">Account Details</h2>
            </div>

            <div className="space-y-3">
              <div className="p-3 bg-gray-900 bg-opacity-50 rounded-lg">
                <p className="text-gray-400 text-sm mb-1">User ID</p>
                <p className="text-white font-mono">#{user.user_id}</p>
              </div>

              <div className="p-3 bg-gray-900 bg-opacity-50 rounded-lg">
                <p className="text-gray-400 text-sm mb-1">Username</p>
                <p className="text-white">{user.username}</p>
              </div>

              <div className="p-3 bg-gray-900 bg-opacity-50 rounded-lg">
                <p className="text-gray-400 text-sm mb-1">Email</p>
                <p className="text-white">{user.email}</p>
              </div>

              {user.last_login && (
                <div className="p-3 bg-gray-900 bg-opacity-50 rounded-lg">
                  <p className="text-gray-400 text-sm mb-1 flex items-center gap-2">
                    <Clock className="w-4 h-4" />
                    Last Login
                  </p>
                  <p className="text-white">
                    {new Date(user.last_login).toLocaleString()}
                  </p>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Security Info */}
        {securityInfo && (
          <div className="bg-gray-800 bg-opacity-50 backdrop-blur-lg rounded-xl shadow-xl p-6 border border-gray-700">
            <h2 className="text-xl font-bold text-white mb-4">Authentication Details</h2>
            
            <div className="grid md:grid-cols-2 gap-4">
              {securityInfo.authentication_method && (
                <div className="p-4 bg-gray-900 bg-opacity-50 rounded-lg">
                  <p className="text-gray-400 text-sm mb-2">Authentication Method</p>
                  <p className="text-white font-medium capitalize">
                    {securityInfo.authentication_method}
                  </p>
                </div>
              )}

              {securityInfo.face_verified !== undefined && (
                <div className="p-4 bg-gray-900 bg-opacity-50 rounded-lg">
                  <p className="text-gray-400 text-sm mb-2">Face Verification</p>
                  <p className={`font-medium ${securityInfo.face_verified ? 'text-green-400' : 'text-gray-400'}`}>
                    {securityInfo.face_verified ? '✓ Verified' : '✗ Not Verified'}
                  </p>
                </div>
              )}

              {securityInfo.fingerprint_verified !== undefined && (
                <div className="p-4 bg-gray-900 bg-opacity-50 rounded-lg">
                  <p className="text-gray-400 text-sm mb-2">Fingerprint Verification</p>
                  <p className={`font-medium ${securityInfo.fingerprint_verified ? 'text-green-400' : 'text-gray-400'}`}>
                    {securityInfo.fingerprint_verified ? '✓ Verified' : '✗ Not Verified'}
                  </p>
                </div>
              )}

              {securityInfo.total_auth_time_ms && (
                <div className="p-4 bg-gray-900 bg-opacity-50 rounded-lg">
                  <p className="text-gray-400 text-sm mb-2">Authentication Time</p>
                  <p className="text-white font-medium">
                    {securityInfo.total_auth_time_ms.toFixed(0)}ms
                  </p>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Quick Actions */}
        <div className="mt-8 grid md:grid-cols-3 gap-4">
          <button
            onClick={() => navigate('/fingerprint-test')}
            className="p-6 bg-gradient-to-br from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 
                     rounded-xl transition-all text-white text-center"
          >
            <Fingerprint className="w-8 h-8 mx-auto mb-2" />
            <p className="font-bold">Test Fingerprint</p>
          </button>

          <button
            onClick={() => navigate('/settings')}
            className="p-6 bg-gradient-to-br from-green-600 to-blue-600 hover:from-green-700 hover:to-blue-700 
                     rounded-xl transition-all text-white text-center"
          >
            <SettingsIcon className="w-8 h-8 mx-auto mb-2" />
            <p className="font-bold">Security Settings</p>
          </button>

          <button
            onClick={handleLogout}
            className="p-6 bg-gradient-to-br from-red-600 to-pink-600 hover:from-red-700 hover:to-pink-700 
                     rounded-xl transition-all text-white text-center"
          >
            <LogOut className="w-8 h-8 mx-auto mb-2" />
            <p className="font-bold">Sign Out</p>
          </button>
        </div>
      </div>
    </div>
  );
}