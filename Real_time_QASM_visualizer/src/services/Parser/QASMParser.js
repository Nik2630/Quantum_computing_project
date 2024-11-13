class QASMParser {
  constructor() {
    this.supportedGates = new Set(['h', 'x', 'y', 'z', 'cx', 'measure']);
  }

  parse(code) {
    try {
      const lines = code.split('\n');
      const circuit = {
        qubits: new Map(),
        classical: new Map(),
        operations: []
      };

      lines.forEach((line, lineNumber) => {
        const trimmedLine = line.trim().toLowerCase();
        
        // Skip empty lines and comments
        if (!trimmedLine || trimmedLine.startsWith('//')) return;
        
        // Skip OPENQASM version and include statements
        if (trimmedLine.startsWith('openqasm') || trimmedLine.startsWith('include')) return;

        // Parse qubit declarations
        if (trimmedLine.startsWith('qubit')) {
          this.parseQubitDeclaration(trimmedLine, circuit);
        }
        // Parse classical bit declarations
        else if (trimmedLine.startsWith('bit')) {
          this.parseClassicalDeclaration(trimmedLine, circuit);
        }
        // Parse gates and measurements
        else {
          this.parseOperation(trimmedLine, circuit);
        }
      });

      return circuit;
    } catch (error) {
      console.error('Parsing error:', error);
      throw error;
    }
  }

  parseQubitDeclaration(line, circuit) {
    const match = line.match(/qubit\[(\d+)\]\s+(\w+)/);
    if (match) {
      const [_, size, name] = match;
      circuit.qubits.set(name, parseInt(size));
    }
  }

  parseClassicalDeclaration(line, circuit) {
    const match = line.match(/bit\[(\d+)\]\s+(\w+)/);
    if (match) {
      const [_, size, name] = match;
      circuit.classical.set(name, parseInt(size));
    }
  }

  parseOperation(line, circuit) {
    // Remove semicolon if present
    line = line.replace(';', '');
    const parts = line.split(/\s+/);
    
    if (parts.length === 0) return;

    const gate = parts[0];
    if (!this.supportedGates.has(gate)) return;

    if (gate === 'measure') {
      const [_, source, arrow, target] = parts;
      circuit.operations.push({
        type: 'measure',
        source: this.parseRegisterReference(source),
        target: this.parseRegisterReference(target)
      });
    } else {
      const targets = parts.slice(1).map(t => this.parseRegisterReference(t));
      circuit.operations.push({
        type: 'gate',
        gate: gate,
        targets: targets
      });
    }
  }

  parseRegisterReference(ref) {
    const parts = ref.split('[');
    if (parts.length === 1) return { register: ref };
    
    return {
      register: parts[0],
      index: parseInt(parts[1].replace(']', ''))
    };
  }
}

export default QASMParser; 