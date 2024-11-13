import React, { useCallback } from 'react';
import CodeMirror from '@uiw/react-codemirror';
import { javascript } from '@codemirror/lang-javascript';
import { linter, lintGutter } from '@codemirror/lint';
import './CodeEditor.css';

const CodeEditor = ({ onChange }) => {
  const initialCode = `// OpenQASM 3 code
OPENQASM 3;
include "stdgates.inc";

qubit[2] q;
bit[2] c;

h q[0];
cx q[0], q[1];
measure q -> c;
`;

  // QASM syntax checking
  const qasmLinter = useCallback((view) => {
    const diagnostics = [];
    const text = view.state.doc.toString();
    const lines = text.split('\n');

    lines.forEach((line, i) => {
      const trimmedLine = line.trim();
      if (!trimmedLine || trimmedLine.startsWith('//')) return;

      // Check for basic QASM syntax
      if (trimmedLine !== '' && !trimmedLine.endsWith(';') && 
          !trimmedLine.startsWith('OPENQASM') && 
          !trimmedLine.startsWith('include')) {
        diagnostics.push({
          from: view.state.doc.line(i + 1).from,
          to: view.state.doc.line(i + 1).to,
          severity: 'warning',
          message: 'Line should end with a semicolon',
        });
      }

      // Check for valid gate operations
      const validGates = ['h', 'x', 'y', 'z', 'cx', 'measure'];
      const firstWord = trimmedLine.split(' ')[0].toLowerCase();
      if (!validGates.includes(firstWord) && 
          !trimmedLine.startsWith('qubit') && 
          !trimmedLine.startsWith('bit') &&
          !trimmedLine.startsWith('OPENQASM') && 
          !trimmedLine.startsWith('include') &&
          trimmedLine !== '') {
        diagnostics.push({
          from: view.state.doc.line(i + 1).from,
          to: view.state.doc.line(i + 1).to,
          severity: 'error',
          message: `Unknown gate or declaration: ${firstWord}`,
        });
      }

      // Check qubit/bit declarations
      if (trimmedLine.startsWith('qubit') || trimmedLine.startsWith('bit')) {
        const pattern = /^(qubit|bit)\[(\d+)\]\s+(\w+);$/;
        if (!pattern.test(trimmedLine)) {
          diagnostics.push({
            from: view.state.doc.line(i + 1).from,
            to: view.state.doc.line(i + 1).to,
            severity: 'error',
            message: 'Invalid qubit/bit declaration format',
          });
        }
      }
    });

    return diagnostics;
  }, []);

  return (
    <div className="editor-container">
      <div className="editor-header">
        <h2>OpenQASM 3 Editor</h2>
      </div>
      <CodeMirror
        value={initialCode}
        height="calc(100% - 60px)"
        onChange={onChange}
        theme="dark"
        extensions={[
          javascript(),
          lintGutter(),
          linter(qasmLinter)
        ]}
        basicSetup={{
          lineNumbers: true,
          highlightActiveLineGutter: true,
          highlightSpecialChars: true,
          history: true,
          foldGutter: true,
          drawSelection: true,
          dropCursor: true,
          allowMultipleSelections: true,
          indentOnInput: true,
          bracketMatching: true,
          closeBrackets: true,
          autocompletion: true,
          rectangularSelection: true,
          crosshairCursor: true,
          highlightActiveLine: true,
          highlightSelectionMatches: true,
          closeBracketsKeymap: true,
          defaultKeymap: true,
          searchKeymap: true,
          historyKeymap: true,
          foldKeymap: true,
          completionKeymap: true,
          lintKeymap: true,
        }}
      />
    </div>
  );
};

export default CodeEditor; 