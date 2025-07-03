import React, { useState, useEffect, useRef } from 'react';

function App() {
  const [pipelineStatus, setPipelineStatus] = useState('Idle');
  const [recentDetections, setRecentDetections] = useState([]);
  const [recentOrbits, setRecentOrbits] = useState([]);
  const [currentFilename, setCurrentFilename] = useState('');
  const [error, setError] = useState(null);
  const [imageDataB64, setImageDataB64] = useState(''); // New state for Base64 image
  const canvasRef = useRef(null); // Ref for the canvas element

  useEffect(() => {
    const fetchPipelineData = async () => {
      try {
        const response = await fetch('http://127.0.0.1:8000/latest_results'); 
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        console.log('Fetched data:', data);

        setPipelineStatus(data.status);
        setCurrentFilename(data.filename || 'N/A');
        setImageDataB64(data.image_data_b64 || ''); // Update image data

        if (data.error) {
          setError(data.error);
        } else {
          setError(null);
        }

        // Update detections, ensuring we only add new ones and keep a limited history
        if (data.detections && data.detections.length > 0) {
          setRecentDetections(prev => {
            const newDetections = [...data.detections.map(d => ({ ...d, filename: data.filename })), ...prev];
            return newDetections.slice(0, 10); // Keep last 10 batches of detections
          });
        } else if (data.status === 'success') { // If successful but no detections, clear previous
            setRecentDetections([]);
        }

        // Update orbital elements
        if (data.orbital_elements && data.orbital_elements.length > 0) {
          setRecentOrbits(prev => {
            const newOrbits = [...data.orbital_elements.map(o => ({ ...o, filename: data.filename })), ...prev];
            return newOrbits.slice(0, 10); // Keep last 10 batches of orbital elements
          });
        } else if (data.status === 'success') { // If successful but no orbits, clear previous
            setRecentOrbits([]);
        }

      } catch (e) {
        console.error('Error fetching pipeline data:', e);
        setPipelineStatus('Error');
        setError(`Failed to connect to backend or fetch data: ${e.message}. Is backend running?`);
      }
    };

    fetchPipelineData(); // Initial fetch
    const intervalId = setInterval(fetchPipelineData, 3000); // Poll every 3 seconds

    return () => clearInterval(intervalId);
  }, []);

  // Effect to draw image and detections on canvas whenever imageDataB64 or recentDetections change
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    const img = new Image();

    img.onload = () => {
      // Set canvas dimensions to match image
      canvas.width = img.width;
      canvas.height = img.height;

      // Clear canvas and draw image
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      ctx.drawImage(img, 0, 0, canvas.width, canvas.height);

      // Draw detections
      recentDetections.forEach(detection => {
        ctx.beginPath();
        ctx.arc(detection.x, detection.y, 5, 0, Math.PI * 2); // Circle at detection coords, radius 5
        ctx.strokeStyle = 'red'; // Red circle
        ctx.lineWidth = 2;
        ctx.stroke();
        ctx.fillStyle = 'rgba(255, 0, 0, 0.3)'; // Semi-transparent red fill
        ctx.fill();
      });
    };

    if (imageDataB64) {
      img.src = `data:image/png;base64,${imageDataB64}`;
    } else {
      // Clear canvas if no image data
      ctx.clearRect(0, 0, canvas.width, canvas.height);
    }
  }, [imageDataB64, recentDetections]); // Re-run effect when image or detections change


  const getStatusColor = (status) => {
    switch (status) {
      case 'success': return 'bg-green-500';
      case 'failed': return 'bg-red-500';
      case 'processing': return 'bg-blue-500';
      case 'Error': return 'bg-red-700';
      default: return 'bg-gray-400';
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 font-inter text-gray-800 p-4 sm:p-6 lg:p-8 flex flex-col items-center">
      <div className="w-full max-w-4xl bg-white shadow-xl rounded-lg p-6 sm:p-8">
        <h1 className="text-3xl sm:text-4xl font-bold text-center text-indigo-700 mb-6">
          <span className="inline-block mr-2">🌌</span>Multi-Agent Asteroid Detection
        </h1>

        {/* Pipeline Status */}
        <div className="mb-8 p-4 bg-indigo-50 rounded-lg shadow-inner flex flex-col sm:flex-row items-center justify-between">
          <div className="flex items-center mb-2 sm:mb-0">
            <span className={`w-4 h-4 rounded-full mr-3 ${getStatusColor(pipelineStatus)} animate-pulse`}></span>
            <span className="text-lg font-semibold">Pipeline Status:</span>
            <span className={`ml-2 px-3 py-1 rounded-full text-sm font-bold text-white ${getStatusColor(pipelineStatus)}`}>
              {pipelineStatus}
            </span>
          </div>
          <p className="text-sm text-gray-600">
            Current File: <span className="font-medium text-indigo-600">{currentFilename}</span>
          </p>
        </div>

        {error && (
          <div className="mb-6 p-4 bg-red-100 border border-red-400 text-red-700 rounded-lg" role="alert">
            <strong className="font-bold">Error:</strong>
            <span className="block sm:inline ml-2">{error}</span>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Image Visualization */}
          <div className="bg-gray-50 p-6 rounded-lg shadow-md flex flex-col items-center justify-center">
            <h2 className="text-xl font-semibold text-gray-700 mb-4 flex items-center">
              <svg className="w-6 h-6 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"></path></svg>
              Image & Detections
            </h2>
            {imageDataB64 ? (
              <canvas ref={canvasRef} className="max-w-full h-auto rounded-md border border-gray-300 shadow-inner"></canvas>
            ) : (
              <p className="text-gray-500">No image data received yet. Waiting for pipeline...</p>
            )}
          </div>

          {/* Recent Detections */}
          <div className="bg-blue-50 p-6 rounded-lg shadow-md">
            <h2 className="text-xl font-semibold text-blue-700 mb-4 flex items-center">
              <svg className="w-6 h-6 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0zM10 7v3m0 0v3m0-3h3m-3 0H7"></path></svg>
              Recent Detections
            </h2>
            {recentDetections.length === 0 ? (
              <p className="text-gray-500">No detections yet. Waiting for data...</p>
            ) : (
              <div className="max-h-64 overflow-y-auto pr-2">
                {recentDetections.map((det, index) => (
                  <div key={index} className="mb-2 p-3 bg-blue-100 rounded-md text-sm shadow-sm">
                    <p><span className="font-semibold">File:</span> {det.filename}</p>
                    <p><span className="font-semibold">Coords (X, Y):</span> ({det.x}, {det.y})</p>
                    <p><span className="font-semibold">Confidence:</span> {(det.confidence * 100).toFixed(2)}%</p>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Estimated Orbital Elements */}
          <div className="bg-purple-50 p-6 rounded-lg shadow-md">
            <h2 className="text-xl font-semibold text-purple-700 mb-4 flex items-center">
              <svg className="w-6 h-6 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 6.253v13.5m0-13.5c-4.142 0-7.5 3.133-7.5 7s3.358 7 7.5 7V6.253zM12 6.253c4.142 0 7.5 3.133 7.5 7s-3.358 7-7.5 7V6.253z"></path></svg>
              Estimated Orbital Elements
            </h2>
            {recentOrbits.length === 0 ? (
              <p className="text-gray-500">No orbital elements yet. Waiting for detections...</p>
            ) : (
              <div className="max-h-64 overflow-y-auto pr-2">
                {recentOrbits.map((orbit, index) => (
                  <div key={index} className="mb-2 p-3 bg-purple-100 rounded-md text-sm shadow-sm">
                    <p><span className="font-semibold">File:</span> {orbit.filename}</p>
                    <p><span className="font-semibold">RA:</span> {orbit.ra}</p>
                    <p><span className="font-semibold">Dec:</span> {orbit.dec}</p>
                    <p><span className="font-semibold">Epoch:</span> {orbit.epoch}</p>
                    <p><span className="font-semibold">Confidence:</span> {(orbit.confidence * 100).toFixed(2)}%</p>
                    {/* You can display more elements. For now, just a sample. */}
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        <div className="mt-8 text-center text-gray-500 text-sm">
          <p>Real-time asteroid detection pipeline powered by Multi-Agent AI.</p>
          <p>Simulated data stream for demonstration purposes.</p>
        </div>
      </div>
    </div>
  );
}

export default App;
