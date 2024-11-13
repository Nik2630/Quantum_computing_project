from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from qiskit import QuantumCircuit, transpile
from qiskit_aer import Aer
from qiskit.visualization import circuit_drawer, plot_state_city, plot_bloch_multivector
import qiskit.qasm3
import numpy as np
import matplotlib.pyplot as plt
import base64
import io 

circuit = qiskit.qasm3.loads('''// OpenQASM 3 code
OPENQASM 3;
include "stdgates.inc";

qubit[4] q;
bit[4] c;

h q[0];
cx q[0], q[1];
measure q -> c;
''')
        
# Draw circuit
# circuit_buffer = io.BytesIO()
# circuit_drawer(circuit, output='mpl', filename=circuit_buffer, style={'backgroundcolor': '#FFFFFF'})
# circuit_buffer.seek(0)
# circuit_image = base64.b64encode(circuit_buffer.getvalue()).decode()

# Calculate state vector
backend = Aer.get_backend('statevector_simulator')
circuit = transpile(circuit, backend)
job = backend.run(circuit)
result = job.result()
statevector = result.get_statevector()

# Visualize state vector
# plt.figure(figsize=(8, 6))
plot_bloch_multivector(statevector)
plt.show()
plt.close()