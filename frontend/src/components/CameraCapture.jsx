import { useEffect, useRef, useState } from 'react';

export default function CameraCapture({ label, onCapture, capturedPreview }) {
  const videoRef = useRef(null);
  const streamRef = useRef(null);
  const [active, setActive] = useState(false);
  const [error, setError] = useState('');

  const startCamera = async () => {
    setError('');
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: 'user', width: { ideal: 640 }, height: { ideal: 480 } },
        audio: false,
      });
      streamRef.current = stream;
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        await videoRef.current.play();
      }
      setActive(true);
    } catch {
      setError('Camera access denied. Allow camera permission or upload a photo instead.');
    }
  };

  const stopCamera = () => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((t) => t.stop());
      streamRef.current = null;
    }
    setActive(false);
  };

  useEffect(() => () => stopCamera(), []);

  const capturePhoto = () => {
    const video = videoRef.current;
    if (!video) return;
    const canvas = document.createElement('canvas');
    canvas.width = video.videoWidth || 640;
    canvas.height = video.videoHeight || 480;
    const ctx = canvas.getContext('2d');
    ctx.drawImage(video, 0, 0);
    canvas.toBlob(
      (blob) => {
        if (!blob) return;
        const file = new File([blob], 'live-selfie.jpg', { type: 'image/jpeg' });
        onCapture(file, canvas.toDataURL('image/jpeg', 0.9));
        stopCamera();
      },
      'image/jpeg',
      0.92
    );
  };

  return (
    <div className="camera-capture-box">
      <label className="camera-label">{label}</label>
      {error && <p className="camera-error">{error}</p>}
      {capturedPreview && !active && (
        <img src={capturedPreview} alt="Captured" className="camera-preview-img" />
      )}
      {active && (
        <video ref={videoRef} className="camera-video" playsInline muted />
      )}
      <div className="camera-actions">
        {!active ? (
          <button type="button" className="btn btn-outline" onClick={startCamera}>
            <i className="fas fa-camera"></i> Open Live Camera
          </button>
        ) : (
          <>
            <button type="button" className="btn btn-primary" onClick={capturePhoto}>
              <i className="fas fa-circle"></i> Capture Live Photo
            </button>
            <button type="button" className="btn btn-outline" onClick={stopCamera}>
              Cancel
            </button>
          </>
        )}
      </div>
    </div>
  );
}
