import React, { useState } from 'react';
import Split from 'split.js';
import { useEffect, useRef } from 'react';
import CodeEditor from '../CodeEditor/CodeEditor';
import CircuitVisualizer from '../CircuitVisualizer/CircuitVisualizer';
import './Layout.css';

const Layout = () => {
  const splitRef = useRef();
  const [qasmCode, setQasmCode] = useState('');
  
  useEffect(() => {
    if (splitRef.current) {
      Split(['#editor-pane', '#visualizer-pane'], {
        sizes: [50, 50],
        minSize: [300, 300],
        gutterSize: 10,
        cursor: 'col-resize'
      });
    }
  }, []);

  const handleCodeChange = (value) => {
    setQasmCode(value);
  };

  return (
    <div className="layout-container" ref={splitRef}>
      <div id="editor-pane" className="pane">
        <CodeEditor onChange={handleCodeChange} />
      </div>
      <div id="visualizer-pane" className="pane">
        <CircuitVisualizer qasmCode={qasmCode} />
      </div>
    </div>
  );
};

export default Layout; 