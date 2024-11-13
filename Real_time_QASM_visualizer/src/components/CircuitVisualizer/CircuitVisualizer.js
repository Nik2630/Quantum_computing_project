import React, { useEffect, useState } from 'react';
import './CircuitVisualizer.css';

const CircuitVisualizer = ({ qasmCode }) => {
  const [circuitImage, setCircuitImage] = useState(null);
  const [stateImage, setStateImage] = useState(null);
  const [probabilities, setProbabilities] = useState(null);
  const [error, setError] = useState(null);
  const [lastValidCode, setLastValidCode] = useState('');

  useEffect(() => {
    if (qasmCode && qasmCode.trim()) {
      const isCompleteLine = qasmCode.trim().endsWith(';') || qasmCode.trim().endsWith('\n');
      
      if (isCompleteLine) {
        visualizeCircuit(qasmCode);
      }
    }
  }, [qasmCode]);

  const visualizeCircuit = async (code) => {
    try {
      const response = await fetch('http://localhost:8000/api/visualize', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ code }),
      });

      if (!response.ok) {
        throw new Error('Failed to visualize circuit');
      }

      const data = await response.json();
      setCircuitImage(data.circuit_image);
      setStateImage(data.state_image);
      setProbabilities(data.probabilities);
      setError(null);
      setLastValidCode(code);
    } catch (error) {
      if (code !== lastValidCode) {
        console.error('Error visualizing circuit:', error);
        if (!circuitImage) {
          setError(error.message);
        }
      }
    }
  };

  const renderProbabilities = () => {
    if (!probabilities) return null;
    return (
      <div className="probabilities-container">
        <h3>State Probabilities</h3>
        <div className="probabilities-grid">
          {Object.entries(probabilities).map(([state, prob]) => (
            <div key={state} className="probability-item">
              <span className="state-label">|{state}⟩:</span>
              <span className="probability-value">{(prob * 100).toFixed(2)}%</span>
            </div>
          ))}
        </div>
      </div>
    );
  };

  return (
    <div className="visualizer-container">
      <div className="visualizer-header">
        <h2>Quantum Circuit Visualization</h2>
      </div>
      <div className="visualizer-content">
        {error && !circuitImage ? (
          <div className="error-message">{error}</div>
        ) : (
          <div className="visualization-layout">
            <div className="circuit-container">
              <h3>Circuit Diagram</h3>
              {circuitImage && (
                <img 
                  src={`data:image/png;base64,${circuitImage}`} 
                  alt="Quantum Circuit" 
                  className="circuit-image"
                />
              )}
            </div>
            <div className="state-analysis-container">
              <div className="state-container">
                <h3>State Vector Visualization</h3>
                {stateImage && (
                  <img 
                    src={`data:image/png;base64,${stateImage}`} 
                    alt="State Vector" 
                    className="state-image"
                  />
                )}
              </div>
              {renderProbabilities()}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default CircuitVisualizer; 