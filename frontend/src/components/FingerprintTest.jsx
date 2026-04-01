import React, { useState } from 'react';
import FingerprintScanner from './FingerprintScanner';

export default function FingerprintTest() {
  const [mode, setMode] = useState('enroll');
  const [enrolledFingerprint, setEnrolledFingerprint] = useState(null);
  const [result, setResult] = useState(null);

  const handleScanComplete = (data) => {
    setResult(data);
    
    if (mode === 'enroll' && data.success) {
      setEnrolledFingerprint(data.data);
      setTimeout(() => {
        alert('Fingerprint enrolled successfully! You can now test verification.');
      }, 1000);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-indigo-900 p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-4xl font-bold text-white text-center mb-8">
          🔐 Real Fingerprint Authentication System
        </h1>

        {/* Mode Selector */}
        <div className="flex gap-4 justify-center mb-8">
          <button
            onClick={() => {
              setMode('enroll');
              setResult(null);
            }}
            className={`px-6 py-3 rounded-lg font-bold transition-all ${
              mode === 'enroll'
                ? 'bg-green-600 text-white'
                : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
            }`}
          >
            Enrollment Mode
          </button>
          <button
            onClick={() => {
              setMode('verify');
              setResult(null);
            }}
            disabled={!enrolledFingerprint}
            className={`px-6 py-3 rounded-lg font-bold transition-all ${
              mode === 'verify' && enrolledFingerprint
                ? 'bg-blue-600 text-white'
                : 'bg-gray-700 text-gray-300'
            } disabled:opacity-50 disabled:cursor-not-allowed`}
          >
            Verification Mode
          </button>
        </div>

        {/* Scanner */}
        <FingerprintScanner
          mode={mode}
          onScanComplete={handleScanComplete}
          storedFingerprint={enrolledFingerprint}
        />

        {/* Status Display */}
        {result && (
          <div className={`mt-6 p-4 rounded-lg ${
            result.success ? 'bg-green-900 bg-opacity-50' : 'bg-red-900 bg-opacity-50'
          }`}>
            <p className={`text-center font-bold ${
              result.success ? 'text-green-300' : 'text-red-300'
            }`}>
              {result.success ? '✅ Success!' : '❌ Failed'}
            </p>
            {result.message && (
              <p className="text-center text-white mt-2">{result.message}</p>
            )}
            {result.score !== undefined && (
              <p className="text-center text-white mt-1">
                Match Score: {result.score.toFixed(1)}%
              </p>
            )}
          </div>
        )}

        {/* Instructions */}
        <div className="mt-8 bg-gray-800 rounded-lg p-6">
          <h3 className="text-xl font-bold text-white mb-4">📋 How It Works</h3>
          <ol className="space-y-3 text-gray-300">
            <li className="flex gap-3">
              <span className="font-bold text-green-400">1.</span>
              <span><strong>Enrollment:</strong> Scan your fingerprint to register it</span>
            </li>
            <li className="flex gap-3">
              <span className="font-bold text-blue-400">2.</span>
              <span><strong>Verification:</strong> Scan again to verify - it will only match YOUR fingerprint</span>
            </li>
            <li className="flex gap-3">
              <span className="font-bold text-purple-400">3.</span>
              <span><strong>Security:</strong> Hash-based matching ensures different fingerprints are rejected</span>
            </li>
          </ol>
        </div>

        {/* Back Button */}
        <div className="mt-6 text-center">
          <button
            onClick={() => window.location.href = '/login'}
            className="px-6 py-3 bg-gray-700 hover:bg-gray-600 text-white rounded-lg font-bold transition-all"
          >
            ← Back to Login
          </button>
        </div>
      </div>
    </div>
  );
}