class CircuitRenderer {
  constructor(canvas) {
    this.canvas = canvas;
    this.ctx = canvas.getContext('2d');
    this.padding = 40;
    this.wireSpacing = 60;
    this.gateSize = 40;
  }

  render(circuit) {
    this.clear();
    this.circuit = circuit;
    
    // Calculate total number of qubits and classical bits
    this.totalQubits = Array.from(circuit.qubits.values()).reduce((a, b) => a + b, 0);
    this.totalClassical = Array.from(circuit.classical.values()).reduce((a, b) => a + b, 0);
    
    this.drawWires();
    this.drawOperations();
  }

  clear() {
    this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
  }

  drawWires() {
    const startY = this.padding;
    const endX = this.canvas.width - this.padding;

    // Draw quantum wires
    for (let i = 0; i < this.totalQubits; i++) {
      const y = startY + i * this.wireSpacing;
      this.drawLine(this.padding, y, endX, y);
      this.ctx.fillText(`q${i}`, 10, y + 5);
    }

    // Draw classical wires
    for (let i = 0; i < this.totalClassical; i++) {
      const y = startY + (this.totalQubits + i) * this.wireSpacing;
      this.drawClassicalWire(this.padding, y, endX, y);
      this.ctx.fillText(`c${i}`, 10, y + 5);
    }
  }

  drawOperations() {
    let xOffset = this.padding + 50;
    
    this.circuit.operations.forEach(op => {
      if (op.type === 'gate') {
        this.drawGate(op, xOffset);
      } else if (op.type === 'measure') {
        this.drawMeasurement(op, xOffset);
      }
      xOffset += this.gateSize + 20;
    });
  }

  drawGate(operation, x) {
    operation.targets.forEach((target, index) => {
      const y = this.padding + target.index * this.wireSpacing;
      
      if (operation.gate === 'cx' && index === 0) {
        // Draw control point
        this.drawControlPoint(x + this.gateSize/2, y);
      } else {
        // Draw gate
        this.drawGateBox(operation.gate, x, y);
      }
    });

    // Draw connection line for controlled gates
    if (operation.gate === 'cx' && operation.targets.length === 2) {
      const y1 = this.padding + operation.targets[0].index * this.wireSpacing;
      const y2 = this.padding + operation.targets[1].index * this.wireSpacing;
      this.drawLine(x + this.gateSize/2, y1, x + this.gateSize/2, y2);
    }
  }

  drawGateBox(gate, x, y) {
    this.ctx.strokeRect(x, y - this.gateSize/2, this.gateSize, this.gateSize);
    this.ctx.fillText(gate.toUpperCase(), x + 5, y + 5);
  }

  drawControlPoint(x, y) {
    this.ctx.beginPath();
    this.ctx.arc(x, y, 5, 0, 2 * Math.PI);
    this.ctx.fill();
  }

  drawMeasurement(operation, x) {
    const sourceY = this.padding + operation.source.index * this.wireSpacing;
    const targetY = this.padding + (this.totalQubits + operation.target.index) * this.wireSpacing;
    
    // Draw measurement symbol
    this.ctx.beginPath();
    this.ctx.arc(x + this.gateSize/2, sourceY, this.gateSize/3, 0, 2 * Math.PI);
    this.ctx.stroke();
    this.drawLine(x + this.gateSize/2, sourceY, x + this.gateSize/2, targetY);
  }

  drawLine(x1, y1, x2, y2) {
    this.ctx.beginPath();
    this.ctx.moveTo(x1, y1);
    this.ctx.lineTo(x2, y2);
    this.ctx.stroke();
  }

  drawClassicalWire(x1, y1, x2, y2) {
    this.ctx.beginPath();
    this.ctx.moveTo(x1, y1);
    this.ctx.lineTo(x2, y2);
    this.ctx.stroke();
    
    // Draw parallel line for classical wire
    this.ctx.beginPath();
    this.ctx.moveTo(x1, y1 + 3);
    this.ctx.lineTo(x2, y2 + 3);
    this.ctx.stroke();
  }
}

export default CircuitRenderer; 