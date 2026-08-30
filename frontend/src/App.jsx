import { useState, useEffect } from 'react';
import './App.css';

function App() {
  const [cpuData, setCpuData] = useState(null);
  const [isConnected, setIsConnected] = useState(false);
  const [error, setError] = useState(null);
  const [recentReadings, setRecentReadings] = useState([]);
  const [warnings, setWarnings] = useState([]);
  const [warningCount, setWarningCount] = useState(0);
  const [toasts, setToasts] = useState([]);

  // Fetch recent readings from API
  const fetchRecentReadings = async () => {
    try {
      const response = await fetch('http://localhost:8000/readings?limit=10');
      const data = await response.json();
      setRecentReadings(data);
      
      const recentWarnings = data.filter(r => r.status === 'warning');
      setWarnings(recentWarnings);
      setWarningCount(recentWarnings.length);
    } catch (err) {
      console.error('Failed to fetch recent readings:', err);
    }
  };

  // Fetch warning count from stats
  const fetchStats = async () => {
    try {
      const response = await fetch('http://localhost:8000/readings/stats');
      const data = await response.json();
      setWarningCount(data.warning_count || 0);
    } catch (err) {
      console.error('Failed to fetch stats:', err);
    }
  };

  // Show toast notification
  const showToast = (message) => {
    const id = Date.now();
    setToasts(prev => [...prev, { id, message }]);
    setTimeout(() => {
      setToasts(prev => prev.filter(t => t.id !== id));
    }, 5000);
  };

  useEffect(() => {
    fetchRecentReadings();
    fetchStats();

    const websocket = new WebSocket('ws://localhost:8000/ws/metrics');

    websocket.onopen = () => {
      console.log('✅ Connected to WebSocket');
      setIsConnected(true);
      setError(null);
    };

    websocket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        setCpuData(data);
        
        setRecentReadings(prev => {
          const newList = [data, ...prev];
          return newList.slice(0, 10);
        });
        
        // Check if it's a warning
        if (data.status === 'warning') {
          // Show toast notification
          showToast(`🚨 High CPU detected: ${data.value.toFixed(1)}%`);
          
          // Add to warnings list
          setWarnings(prev => {
            const newWarnings = [data, ...prev];
            return newWarnings.slice(0, 20);
          });
          setWarningCount(prev => prev + 1);
        }
      } catch (err) {
        console.error('Error parsing data:', err);
      }
    };

    websocket.onclose = () => {
      console.log('❌ WebSocket disconnected');
      setIsConnected(false);
    };

    websocket.onerror = (err) => {
      console.error('WebSocket error:', err);
      setError('Failed to connect to WebSocket');
    };

    return () => {
      websocket.close();
    };
  }, []);

  const cpuPercentage = cpuData ? Math.min(cpuData.value, 100) : 0;
  const isWarning = cpuData?.status === 'warning';
  const hasWarnings = warnings.length > 0;

  return (
    <div className="app-container">
      {/* Toast notifications */}
      <div className="toast-container">
        {toasts.map((toast) => (
          <div key={toast.id} className="toast-warning">
            <span>🚨</span> {toast.message}
          </div>
        ))}
      </div>

      <div className="bg-animation">
        <div className="orb orb-1"></div>
        <div className="orb orb-2"></div>
        <div className="orb orb-3"></div>
      </div>

      <div className="dashboard">
        <header className="header">
          <div className="header-left">
            <div className="logo">
              <span className="logo-icon">⚡</span>
              <h1>Health Monitor</h1>
            </div>
            <div className={`connection-status ${isConnected ? 'connected' : 'disconnected'}`}>
              <span className="status-dot"></span>
              {isConnected ? 'Live' : 'Offline'}
            </div>
          </div>
          <div className="header-right">
            <div className="time-display">
              {new Date().toLocaleTimeString()}
            </div>
          </div>
        </header>

        {error && (
          <div className="error-banner">
            <span>⚠️</span> {error}
          </div>
        )}

        {/* Warning banner */}
        {isWarning && (
          <div className="warning-banner">
            <span>🚨</span> 
            <strong>HIGH CPU USAGE DETECTED!</strong> 
            Current: {cpuData?.value.toFixed(1)}% | Threshold: {cpuData?.threshold || 80}%
          </div>
        )}

        <div className="dashboard-grid">
          <div className="card cpu-card">
            <div className="card-header">
              <span className="card-icon">🖥️</span>
              <h3>CPU Usage</h3>
            </div>
            <div className="cpu-display">
              <div className="cpu-number">
                <span className="number">{cpuData ? cpuData.value.toFixed(1) : '--'}</span>
                <span className="percent">%</span>
              </div>
              <div className="cpu-bar-container">
                <div 
                  className={`cpu-bar ${isWarning ? 'warning' : 'normal'}`}
                  style={{ width: `${cpuPercentage}%` }}
                >
                  <div className="bar-shine"></div>
                </div>
              </div>
              <div className="cpu-status">
                <span className={`status-badge ${cpuData?.status || ''}`}>
                  {cpuData?.status === 'warning' ? '⚠️ High Load' : '✅ Normal'}
                </span>
                <span className="timestamp">
                  Updated: {cpuData ? new Date(cpuData.created_at).toLocaleTimeString() : '--'}
                </span>
              </div>
            </div>
          </div>

          <div className="card stats-card">
            <div className="card-header">
              <span className="card-icon">📊</span>
              <h3>System Stats</h3>
            </div>
            <div className="stats-grid">
              <div className="stat-item">
                <span className="stat-label">Total Readings</span>
                <span className="stat-value">{recentReadings.length}</span>
              </div>
              <div className="stat-item">
                <span className="stat-label">Warnings</span>
                <span className={`stat-value warning-number`}>{warningCount}</span>
              </div>
              <div className="stat-item">
                <span className="stat-label">Threshold</span>
                <span className="stat-value">{cpuData?.threshold || 80}%</span>
              </div>
              <div className="stat-item">
                <span className="stat-label">Status</span>
                <span className={`stat-value ${isConnected ? 'online' : 'offline'}`}>
                  {isConnected ? 'Online' : 'Offline'}
                </span>
              </div>
            </div>
          </div>
        </div>

        <div className="dashboard-bottom">
          <div className={`card warnings-card ${hasWarnings ? 'has-warnings' : ''}`}>
            <div className="card-header">
              <span className="card-icon">🚨</span>
              <h3>Warning Log</h3>
              <span className="warning-badge">{warnings.length}</span>
            </div>
            <div className="warnings-list">
              {warnings.length === 0 ? (
                <div className="empty-state">
                  <span className="empty-icon">✅</span>
                  <p>All systems healthy</p>
                </div>
              ) : (
                warnings.map((warning) => (
                  <div key={warning.id} className="warning-item">
                    <span className="warning-time">
                      {new Date(warning.created_at).toLocaleTimeString()}
                    </span>
                    <span className="warning-value">{warning.value.toFixed(1)}%</span>
                    <span className="warning-icon">🚨</span>
                  </div>
                ))
              )}
            </div>
          </div>

          <div className="card activity-card">
            <div className="card-header">
              <span className="card-icon">📋</span>
              <h3>Recent Activity</h3>
            </div>
            <div className="activity-list">
              {recentReadings.slice(0, 8).map((reading) => (
                <div key={reading.id} className={`activity-item ${reading.status}`}>
                  <span className="activity-time">
                    {new Date(reading.created_at).toLocaleTimeString()}
                  </span>
                  <span className="activity-value">{reading.value.toFixed(1)}%</span>
                  <span className={`activity-status ${reading.status}`}>
                    {reading.status === 'warning' ? '⚠️' : '✅'}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>

        <footer className="footer">
          <span>Live Server Health Monitor v1.0</span>
          <span>•</span>
          <span>WebSocket Connected</span>
          <span>•</span>
          <span>Real-time Monitoring</span>
        </footer>
      </div>
    </div>
  );
}

export default App;
