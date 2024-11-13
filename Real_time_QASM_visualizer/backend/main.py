from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from qiskit import QuantumCircuit, transpile
from qiskit_aer import Aer
from qiskit.visualization import circuit_drawer, plot_state_city, plot_bloch_multivector, plot_bloch_vector
from qiskit.quantum_info.states.densitymatrix import DensityMatrix
from qiskit.quantum_info.operators.symplectic import PauliList
from qiskit.visualization.exceptions import VisualizationError
import qiskit.qasm3
import numpy as np
import matplotlib.pyplot as plt
import base64
import io

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QASMCode(BaseModel):
    code: str

@app.post("/api/visualize")
async def visualize_circuit(qasm: QASMCode):
    try:
        # Create circuit from QASM
        circuit = qiskit.qasm3.loads(qasm.code)
        
        # Draw circuit
        circuit_buffer = io.BytesIO()
        circuit_drawer(circuit, output='mpl', filename=circuit_buffer, style={'backgroundcolor': '#FFFFFF'})
        circuit_buffer.seek(0)
        circuit_image = base64.b64encode(circuit_buffer.getvalue()).decode()

        # Calculate state vector
        backend = Aer.get_backend('statevector_simulator')
        circuit = transpile(circuit, backend)
        job = backend.run(circuit)
        result = job.result()
        statevector = result.get_statevector()

        # Visualize state vector
        plt.figure(figsize=(8, 6))
        plot_bloch_multivector_custom(statevector)
        state_buffer = io.BytesIO()
        plt.savefig(state_buffer, format='png', bbox_inches='tight')
        state_buffer.seek(0)
        state_image = base64.b64encode(state_buffer.getvalue()).decode()
        plt.close()

        # Calculate probabilities
        probabilities = np.abs(statevector) ** 2
        prob_dict = {format(i, f'0{circuit.num_qubits}b'): float(prob) 
                    for i, prob in enumerate(probabilities) if prob > 1e-15}

        return {
            "circuit_image": circuit_image,
            "state_image": state_image,
            "probabilities": prob_dict
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) 
    

def plot_bloch_multivector_custom(
    state,
    title="",
    figsize=None,
    *,
    reverse_bits=False,
    filename=None,
    font_size=None,
    title_font_size=None,
    title_pad=1,
):
    # Data
    bloch_data = (
        _bloch_multivector_data(state)[::-1] if reverse_bits else _bloch_multivector_data(state)
    )
    num = len(bloch_data)
    if figsize is not None:
        width, height = figsize
        height *= num
    else:
        width, height = plt.figaspect(num)
    default_title_font_size = font_size if font_size is not None else 16
    title_font_size = title_font_size if title_font_size is not None else default_title_font_size
    fig = plt.figure(figsize=(width, height))
    for i in range(num):
        pos = num - 1 - i if reverse_bits else i
        ax = fig.add_subplot(num, 1, i + 1, projection="3d")
        plot_bloch_vector(
            bloch_data[i], "qubit " + str(pos), ax=ax, figsize=figsize, font_size=font_size
        )
    fig.suptitle(title, fontsize=title_font_size, y=1.0 + title_pad / 100)
    # matplotlib_close_if_inline(fig)
    if filename is None:
        return fig
    else:
        return fig.savefig(filename)
    
def _bloch_multivector_data(state):
    rho = DensityMatrix(state)
    num = rho.num_qubits
    if num is None:
        raise VisualizationError("Input is not a multi-qubit quantum state.")
    pauli_singles = PauliList(["X", "Y", "Z"])
    bloch_data = []
    for i in range(num):
        if num > 1:
            paulis = PauliList.from_symplectic(
                np.zeros((3, (num - 1)), dtype=bool), np.zeros((3, (num - 1)), dtype=bool)
            ).insert(i, pauli_singles, qubit=True)
        else:
            paulis = pauli_singles
        bloch_state = [np.real(np.trace(np.dot(mat, rho.data))) for mat in paulis.matrix_iter()]
        bloch_data.append(bloch_state)
    return bloch_data