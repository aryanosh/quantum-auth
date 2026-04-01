import React, { useState } from 'react';
import { Fingerprint, Check, X, Loader2 } from 'lucide-react';
import { startRegistration, startAuthentication } from '@simplewebauthn/browser';

const API_ROOT = (process.env.REACT_APP_API_URL || 'http://localhost:5000/api').replace(/\/api\/?$/, '');

const FingerprintScanner = ({
  mode = 'enroll',
  onScanComplete,
  username = '', // Required for login
  authToken = '' // Required for registration
}) => {
  const [status, setStatus] = useState('idle'); // idle, scanning, success, error
  const [message, setMessage] = useState('');

  const handleEnroll = async () => {
    setStatus('scanning');
    setMessage('Prompting for fingerprint...');

    try {
      // 1. Get options from server
      const resp = await fetch(`${API_ROOT}/api/webauthn/register/begin`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${authToken}`,
          'Content-Type': 'application/json'
        }
      });

      const optionsJSON = await resp.json();
      if (!optionsJSON.success) throw new Error(optionsJSON.message);

      // 2. Pass to browser API
      const attResp = await startRegistration(optionsJSON.options);

      // 3. functional verification
      const verifyResp = await fetch(`${API_ROOT}/api/webauthn/register/complete`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${authToken}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(attResp)
      });

      const verifyJSON = await verifyResp.json();

      if (verifyJSON.success) {
        setStatus('success');
        setMessage('Fingerprint enrolled successfully!');
        if (onScanComplete) onScanComplete({ success: true });
      } else {
        throw new Error(verifyJSON.message);
      }

    } catch (error) {
      console.error(error);
      setStatus('error');
      setMessage(error.message || 'Enrollment failed');
      if (onScanComplete) onScanComplete({ success: false, message: error.message });
    }
  };

  const handleVerify = async () => {
    setStatus('scanning');
    setMessage('Prompting for fingerprint...');

    try {
      // 1. Get options
      const resp = await fetch(`${API_ROOT}/api/webauthn/login/begin`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username })
      });

      const optionsJSON = await resp.json();
      if (!optionsJSON.success) {
        throw new Error(optionsJSON.message);
      }

      // 2. Browser API
      const asseResp = await startAuthentication(optionsJSON.options);

      // 3. Verify
      const verifyResp = await fetch(`${API_ROOT}/api/webauthn/login/complete`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          username,
          ...asseResp
        })
      });

      const verifyJSON = await verifyResp.json();

      if (verifyJSON.success) {
        setStatus('success');
        setMessage('Fingerprint verified!');
        if (onScanComplete) onScanComplete({ success: true, token: verifyJSON.token });
      } else {
        throw new Error(verifyJSON.message);
      }

    } catch (error) {
      console.error(error);
      setStatus('error');
      setMessage(error.message || 'Verification failed');
      if (onScanComplete) onScanComplete({ success: false, message: error.message });
    }
  };

  const startAction = () => {
    if (mode === 'enroll') handleEnroll();
    else handleVerify();
  };

  return (
    <div className="w-full max-w-sm mx-auto p-6 bg-gray-800 rounded-xl border border-gray-700 text-center">
      <div className="mb-6 flex justify-center">
        <div className={`
          p-4 rounded-full transition-colors duration-500
          ${status === 'idle' ? 'bg-gray-700 text-gray-400' : ''}
          ${status === 'scanning' ? 'bg-blue-900/50 text-blue-400 animate-pulse' : ''}
          ${status === 'success' ? 'bg-green-900/50 text-green-400' : ''}
          ${status === 'error' ? 'bg-red-900/50 text-red-400' : ''}
        `}>
          {status === 'scanning' ? <Loader2 className="w-12 h-12 animate-spin" /> :
            status === 'success' ? <Check className="w-12 h-12" /> :
              status === 'error' ? <X className="w-12 h-12" /> :
                <Fingerprint className="w-12 h-12" />
          }
        </div>
      </div>

      <h3 className="text-xl font-semibold text-white mb-2">
        {mode === 'enroll' ? 'Setup Fingerprint' : 'Fingerprint Login'}
      </h3>

      <p className="text-gray-400 mb-6 text-sm">
        {message || (mode === 'enroll'
          ? "Secure your account with your device's fingerprint scanner."
          : "Scan your fingerprint to log in.")}
      </p>

      {status !== 'success' && (
        <button
          onClick={startAction}
          disabled={status === 'scanning'}
          className="w-full py-3 px-4 bg-purple-600 hover:bg-purple-700 disabled:bg-purple-800 
                   text-white font-medium rounded-lg transition-colors flex items-center justify-center gap-2"
        >
          {status === 'scanning' ? 'Waiting for sensor...' : 'Start Scan'}
        </button>
      )}
    </div>
  );
};

export default FingerprintScanner;