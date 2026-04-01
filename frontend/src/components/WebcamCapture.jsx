import React, { useCallback, useMemo, useRef, useState, useEffect } from 'react';
import { Camera, X, Loader2, Sun, AlertTriangle } from 'lucide-react';

function WebcamCapture({ onCapture, onCancel }) {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const sampleCanvasRef = useRef(null);
  const [stream, setStream] = useState(null);
  const [error, setError] = useState('');
  const [countdown, setCountdown] = useState(null);
  const [hint, setHint] = useState('Align your face in the oval and hold still.');
  const [quality, setQuality] = useState({ lighting: 'unknown', stability: 'unknown' });
  const [capturing, setCapturing] = useState(false);
  const lastFrameRef = useRef(null);

  const stopWebcam = useCallback(() => {
    if (stream) {
      stream.getTracks().forEach(track => track.stop());
    }
  }, [stream]);

  const startWebcam = useCallback(async () => {
    try {
      const mediaStream = await navigator.mediaDevices.getUserMedia({
        video: {
          width: { ideal: 1280 },
          height: { ideal: 720 },
          facingMode: 'user'
        }
      });
      
      if (videoRef.current) {
        videoRef.current.srcObject = mediaStream;
      }
      setStream(mediaStream);
      setError('');
    } catch (err) {
      console.error('Webcam error:', err);
      setError('Unable to access webcam. Please ensure you have granted camera permissions.');
    }
  }, []);

  useEffect(() => {
    startWebcam();
    return () => {
      stopWebcam();
    };
  }, [startWebcam, stopWebcam]);

  useEffect(() => {
    if (!stream) return;
    let raf = 0;
    let lastHintAt = 0;

    const analyze = (t) => {
      raf = requestAnimationFrame(analyze);
      const video = videoRef.current;
      const sampleCanvas = sampleCanvasRef.current;
      if (!video || !sampleCanvas) return;
      if (video.readyState < 2) return;

      const w = 160;
      const h = 120;
      sampleCanvas.width = w;
      sampleCanvas.height = h;
      const ctx = sampleCanvas.getContext('2d', { willReadFrequently: true });
      ctx.drawImage(video, 0, 0, w, h);
      const frame = ctx.getImageData(0, 0, w, h).data;

      // Lighting (avg luminance)
      let sum = 0;
      for (let i = 0; i < frame.length; i += 4) {
        // relative luminance approximation
        sum += 0.2126 * frame[i] + 0.7152 * frame[i + 1] + 0.0722 * frame[i + 2];
      }
      const avg = sum / (frame.length / 4);
      const lighting = avg < 55 ? 'low' : avg > 190 ? 'high' : 'good';

      // Stability (frame-to-frame difference)
      let stability = 'unknown';
      const last = lastFrameRef.current;
      if (last && last.length === frame.length) {
        let diff = 0;
        for (let i = 0; i < frame.length; i += 16) {
          diff += Math.abs(frame[i] - last[i]);
        }
        const normalized = diff / (frame.length / 16);
        stability = normalized > 12 ? 'moving' : 'steady';
      }
      lastFrameRef.current = frame;

      const nextQuality = { lighting, stability };
      setQuality(nextQuality);

      if (t - lastHintAt > 900) {
        lastHintAt = t;
        if (lighting === 'low') setHint('Lighting is low. Face a light source or increase brightness.');
        else if (lighting === 'high') setHint('Lighting is harsh. Avoid backlight and reduce glare.');
        else if (stability === 'moving') setHint('Hold still for a sharper capture.');
        else setHint('Great. Keep your face centered in the oval.');
      }
    };

    raf = requestAnimationFrame(analyze);
    return () => cancelAnimationFrame(raf);
  }, [stream]);

  const handleCapture = () => {
    // Start countdown
    let count = 3;
    setCountdown(count);
    setCapturing(true);
    
    const interval = setInterval(() => {
      count--;
      setCountdown(count);
      
      if (count === 0) {
        clearInterval(interval);
        captureImage();
        setCountdown(null);
        setCapturing(false);
      }
    }, 1000);
  };

  const captureImage = () => {
    const video = videoRef.current;
    const canvas = canvasRef.current;
    
    if (video && canvas) {
      const context = canvas.getContext('2d');
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      
      // Draw video frame to canvas
      context.drawImage(video, 0, 0);
      
      // Convert to base64
      const imageData = canvas.toDataURL('image/jpeg', 0.95);
      
      stopWebcam();
      onCapture(imageData);
    }
  };

  const qualityBadge = useMemo(() => {
    const issues = [];
    if (quality.lighting === 'low') issues.push('Low light');
    if (quality.lighting === 'high') issues.push('Glare');
    if (quality.stability === 'moving') issues.push('Moving');

    if (issues.length === 0 && (quality.lighting === 'good' || quality.lighting === 'unknown')) {
      return { tone: 'good', text: 'Good quality' };
    }
    if (issues.length === 0) return { tone: 'neutral', text: 'Analyzing…' };
    return { tone: 'warn', text: issues.join(' • ') };
  }, [quality]);

  return (
    <div className="relative">
      {error && (
        <div className="bg-red-500/20 border border-red-500 text-red-200 px-4 py-3 rounded-lg mb-4">
          {error}
        </div>
      )}

      <div className="relative bg-black rounded-lg overflow-hidden">
        <video
          ref={videoRef}
          autoPlay
          playsInline
          muted
          className="w-full h-auto"
        />
        
        {countdown !== null && (
          <div className="absolute inset-0 flex items-center justify-center bg-black/50">
            <div className="text-9xl font-bold text-white animate-pulse">
              {countdown}
            </div>
          </div>
        )}

        {/* Face detection overlay */}
        <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
          <div className={`w-64 h-80 border-4 rounded-full opacity-60 ${capturing ? 'border-green-400 animate-pulse' : 'border-purple-400'}`}></div>
        </div>

        <div className="absolute left-3 top-3 right-3 flex items-start justify-between gap-3">
          <div
            className={[
              'px-3 py-1 rounded-full text-xs font-semibold inline-flex items-center gap-2',
              qualityBadge.tone === 'good' ? 'bg-green-900/60 text-green-200 border border-green-500/40' : '',
              qualityBadge.tone === 'warn' ? 'bg-yellow-900/60 text-yellow-200 border border-yellow-500/40' : '',
              qualityBadge.tone === 'neutral' ? 'bg-gray-900/60 text-gray-200 border border-gray-500/30' : ''
            ].join(' ')}
          >
            {qualityBadge.tone === 'warn' ? <AlertTriangle className="w-4 h-4" /> : <Sun className="w-4 h-4" />}
            {qualityBadge.text}
          </div>

          {capturing && (
            <div className="px-3 py-1 rounded-full text-xs font-semibold bg-purple-900/60 text-purple-200 border border-purple-500/40 inline-flex items-center gap-2">
              <Loader2 className="w-4 h-4 animate-spin" />
              Capturing
            </div>
          )}
        </div>
      </div>

      <canvas ref={canvasRef} className="hidden" />
      <canvas ref={sampleCanvasRef} className="hidden" />

      <div className="flex gap-3 mt-4">
        <button
          type="button"
          onClick={onCancel}
          className="flex-1 py-3 bg-gray-600 hover:bg-gray-700 text-white rounded-lg font-semibold transition-all flex items-center justify-center gap-2"
        >
          <X className="w-5 h-5" />
          Cancel
        </button>
        <button
          type="button"
          onClick={handleCapture}
          disabled={countdown !== null}
          className="flex-1 py-3 bg-purple-600 hover:bg-purple-700 text-white rounded-lg font-semibold transition-all disabled:opacity-50 flex items-center justify-center gap-2"
        >
          <Camera className="w-5 h-5" />
          {countdown !== null ? 'Capturing...' : 'Capture Face'}
        </button>
      </div>

      <p className="text-purple-300 text-sm text-center mt-3">
        {hint}
      </p>
    </div>
  );
}

export default WebcamCapture;