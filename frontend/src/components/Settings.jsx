import React, { useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, Camera, Shield, Save, AlertTriangle } from 'lucide-react';
import WebcamCapture from './WebcamCapture';
import api from '../services/api';
import { useAuth } from '../auth/AuthContext';

export default function Settings() {
  const navigate = useNavigate();
  const { user, token, loadUser, biometricUpdatedAt, markBiometricUpdated } = useAuth();
  const [mode, setMode] = useState('idle'); // idle | capture
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');

  const biometricStatus = useMemo(() => {
    const registered = user?.biometrics_registered || {};
    return {
      face: Boolean(registered.face),
      fingerprint: Boolean(registered.fingerprint)
    };
  }, [user]);

  const handleReEnroll = async (faceImage) => {
    setError('');
    setMessage('');
    setSaving(true);

    try {
      const resp = await api.updateBiometrics(token, { face_image: faceImage });
      if (!resp?.success) {
        throw new Error(resp?.message || 'Failed to update biometrics.');
      }

      markBiometricUpdated();
      await loadUser();
      setMessage('Face re-enrolled successfully. Your encrypted embedding has been updated.');
      setMode('idle');
    } catch (e) {
      const msg = e?.message || 'Failed to update biometrics.';
      // If backend doesn’t implement this endpoint yet, make it obvious.
      if (msg.toLowerCase().includes('not found')) {
        setError('This backend does not expose `/api/update-biometrics` yet. Add the endpoint to enable re-enrollment.');
      } else {
        setError(msg);
      }
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-900 via-indigo-900 to-blue-900 p-8">
      <div className="max-w-4xl mx-auto">
        <div className="flex items-center justify-between mb-6">
          <button
            onClick={() => navigate('/dashboard')}
            className="inline-flex items-center gap-2 px-4 py-2 bg-gray-800/60 hover:bg-gray-800 text-white rounded-lg border border-gray-700 transition-all"
          >
            <ArrowLeft className="w-4 h-4" />
            Back
          </button>

          <div className="inline-flex items-center gap-2 text-white/90">
            <Shield className="w-5 h-5 text-purple-300" />
            <span className="font-semibold">Security Settings</span>
          </div>
        </div>

        {(error || message) && (
          <div className="mb-6">
            {error && (
              <div className="p-4 bg-red-900/50 border border-red-500 rounded-lg text-red-100 flex items-start gap-3">
                <AlertTriangle className="w-5 h-5 mt-0.5" />
                <div>
                  <p className="font-semibold">Update failed</p>
                  <p className="text-sm opacity-90">{error}</p>
                </div>
              </div>
            )}
            {message && (
              <div className="p-4 bg-green-900/40 border border-green-500 rounded-lg text-green-100">
                {message}
              </div>
            )}
          </div>
        )}

        <div className="grid md:grid-cols-2 gap-6">
          <div className="bg-gray-800/50 backdrop-blur-lg rounded-2xl shadow-2xl p-6 border border-gray-700">
            <h2 className="text-xl font-bold text-white mb-4">Biometric Status</h2>

            <div className="space-y-3">
              <div className="p-4 bg-gray-900/50 rounded-lg border border-gray-700">
                <p className="text-gray-400 text-sm mb-1">Face</p>
                <p className="text-white font-semibold">{biometricStatus.face ? 'Enrolled' : 'Not enrolled'}</p>
              </div>

              <div className="p-4 bg-gray-900/50 rounded-lg border border-gray-700">
                <p className="text-gray-400 text-sm mb-1">Fingerprint</p>
                <p className="text-white font-semibold">{biometricStatus.fingerprint ? 'Enrolled' : 'Not enrolled'}</p>
              </div>

              <div className="p-4 bg-gray-900/50 rounded-lg border border-gray-700">
                <p className="text-gray-400 text-sm mb-1">Last biometric update</p>
                <p className="text-white font-semibold">
                  {biometricUpdatedAt ? new Date(biometricUpdatedAt).toLocaleString() : '—'}
                </p>
                <p className="text-gray-400 text-xs mt-1">
                  Stored locally for demo/portfolio UX unless backend exposes an “updated_at” field.
                </p>
              </div>
            </div>
          </div>

          <div className="bg-gray-800/50 backdrop-blur-lg rounded-2xl shadow-2xl p-6 border border-gray-700">
            <h2 className="text-xl font-bold text-white mb-4">Face Re-enrollment</h2>
            <p className="text-gray-300 text-sm mb-4">
              Re-capture your face to update the encrypted embedding stored on the server.
            </p>

            {mode === 'idle' && (
              <button
                onClick={() => {
                  setError('');
                  setMessage('');
                  setMode('capture');
                }}
                disabled={saving}
                className="w-full py-3 px-4 bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 disabled:opacity-50
                         text-white font-bold rounded-lg transition-all flex items-center justify-center gap-2"
              >
                <Camera className="w-5 h-5" />
                Start Capture
              </button>
            )}

            {mode === 'capture' && (
              <div>
                <div className="mb-4">
                  <WebcamCapture
                    onCancel={() => setMode('idle')}
                    onCapture={(img) => handleReEnroll(img)}
                  />
                </div>

                <div className="text-xs text-gray-400 flex items-center gap-2">
                  <Save className="w-4 h-4" />
                  During update: “extract embedding → encrypt → store”.
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

