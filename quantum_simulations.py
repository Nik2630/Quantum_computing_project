from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister, transpile
from qiskit.visualization import plot_histogram, plot_bloch_multivector, plot_circuit_layout, plot_state_qsphere
from qiskit_aer import AerSimulator, QasmSimulator, Aer
from qiskit.result import Result
from qiskit_aer.noise import NoiseModel
from qiskit_aer import noise
import numpy as np
import matplotlib.pyplot as plt
import time

# 1. Quantum Error Detection Circuit
def create_error_detection_circuit():
    qr = QuantumRegister(3, 'q')
    cr = ClassicalRegister(3, 'c')
    qc = QuantumCircuit(qr, cr)
    
    # Encode state
    qc.h(qr[0])
    qc.cx(qr[0], qr[1])
    qc.cx(qr[0], qr[2])
    
    # Add error
    qc.x(qr[0])
    
    # Detect error
    qc.cx(qr[0], qr[1])
    qc.cx(qr[0], qr[2])
    qc.ccx(qr[1], qr[2], qr[0])  # Toffoli gate for correction
    
    qc.measure(qr, cr)
    return qc

# 2. Quantum Register Architecture Simulation
def create_quantum_register_simulation():
    qc = QuantumCircuit(4, 4)
    
    # Initialize register in superposition
    for i in range(4):
        qc.h(i)
    
    # Operations
    qc.cx(0, 1)
    qc.cx(2, 3)
    qc.barrier()
    
    qc.rz(np.pi/4, 0)
    qc.rz(np.pi/4, 2)
    qc.barrier()
    
    # Measurement
    qc.measure_all()
    return qc

# 3. Quantum Memory Operations
def quantum_memory_operations():
    qc = QuantumCircuit(3, 3)
    
    # Write
    qc.h(0)
    qc.cx(0, 1)
    qc.barrier()
    
    # Memory holding period (identity operations)
    qc.id(0)
    qc.id(1)
    qc.barrier()
    
    # Read
    qc.cx(0, 2)
    qc.h(0)
    
    qc.measure_all()
    return qc

# 4. Quantum Arithmetic Circuit
def quantum_arithmetic():
    qc = QuantumCircuit(4, 4)
    
    # Input
    qc.x(0)
    qc.x(1)
    
    # Add
    qc.cx(0, 2)
    qc.cx(1, 2)
    qc.ccx(0, 1, 3)  # Carry bit
    
    qc.measure_all()
    return qc

# 5. Quantum Cache Simulation
def quantum_cache_simulation():
    qr_cache = QuantumRegister(4, 'cache')
    qr_data = QuantumRegister(4, 'data')
    cr = ClassicalRegister(8, 'measurement')
    qc = QuantumCircuit(qr_cache, qr_data, cr)
    
    # Cache write
    qc.h(qr_cache[0])
    qc.cx(qr_cache[0], qr_data[0])
    
    # Cache coherence operation
    for i in range(1, 4):
        qc.cx(qr_cache[0], qr_cache[i])
        qc.cx(qr_data[0], qr_data[i])
    
    qc.measure_all()
    return qc

# 6. Quantum Pipeline Implementation
def quantum_pipeline():
    """Implements a basic quantum pipeline with multiple stages"""
    qc = QuantumCircuit(5, 5)
    
    # Stage 1: Initialization
    qc.h(0)
    qc.barrier()
    
    # Stage 2: Processing
    qc.cx(0, 1)
    qc.barrier()
    
    # Stage 3: Transform
    qc.h(1)
    qc.cx(1, 2)
    qc.barrier()
    
    # Stage 4: Output
    qc.measure_all()
    return qc

# Function to run and visualize results
def run_and_visualize(circuit, name):
    simulator = Aer.get_backend('qasm_simulator')
    transpiled_circuit = transpile(circuit, simulator)
    job = simulator.run(transpiled_circuit, shots=1000)
    result = job.result()
    counts = result.get_counts(circuit)
    
    print(f"\nResults for {name}:")
    print(counts)
    plot_histogram(counts)
    return counts


class QuantumCircuitAnalyzer:
    def __init__(self):
        self.simulator = AerSimulator()
        self.noise_simulator = AerSimulator(noise_model=self.create_noise_model())
    
    def create_noise_model(self):
        noise_model = NoiseModel()
        
        # Define error probabilities
        p_1 = 0.001  # 1-qubit gate error rate
        p_2 = 0.01   # 2-qubit gate error rate
        p_meas = 0.02  # measurement error rate
        
        # Add errors
        error_1 = noise.depolarizing_error(p_1, 1)
        error_2 = noise.depolarizing_error(p_2, 2)
        
        # Add errors to noise model
        noise_model.add_all_qubit_quantum_error(error_1, ['u1', 'u2', 'u3'])
        noise_model.add_all_qubit_quantum_error(error_2, ['cx'])
        
        return noise_model

    def analyze_circuit(self, circuit: QuantumCircuit, shots: int = 1000):
        metrics = {}
        
        # Basic metrics
        metrics['depth'] = circuit.depth()
        metrics['width'] = circuit.width()
        metrics['size'] = circuit.size()
        
        # Count gate types
        gate_counts = {}
        for instruction in circuit.data:
            gate_name = instruction[0].name
            gate_counts[gate_name] = gate_counts.get(gate_name, 0) + 1
        metrics['gate_counts'] = gate_counts
        
        # Performance Metrics
        start_time = time.time()
        result = self.simulator.run(circuit, shots=shots).result()
        execution_time = time.time() - start_time
        metrics['execution_time'] = execution_time
        
        # Error Analysis
        noisy_result = self.noise_simulator.run(circuit, shots=shots).result()
        metrics['error_analysis'] = self.analyze_errors(result, noisy_result)
        
        return metrics
    
    def analyze_errors(self, ideal_result: Result, noisy_result: Result) -> dict:
        ideal_counts = ideal_result.get_counts()
        noisy_counts = noisy_result.get_counts()
        
        total_error = 0
        total_shots = sum(ideal_counts.values())
        
        for state in ideal_counts:
            ideal_prob = ideal_counts[state] / total_shots
            noisy_prob = noisy_counts.get(state, 0) / total_shots
            total_error += abs(ideal_prob - noisy_prob)
        
        return {
            'total_error_rate': total_error / 2,
            'ideal_counts': ideal_counts,
            'noisy_counts': noisy_counts
        }
    
    def visualize_results(self, circuit: QuantumCircuit, metrics: dict):
        figures = []
        
        # Circuit Diagram
        fig1 = plt.figure(figsize=(8, 6))
        circuit.draw(output='mpl', ax=fig1.gca())
        plt.title('Circuit Diagram')
        figures.append(fig1)
        
        # Gates
        fig2 = plt.figure(figsize=(8, 6))
        gate_counts = metrics['gate_counts']
        plt.bar(gate_counts.keys(), gate_counts.values())
        plt.xticks(rotation=45)
        plt.title('Gate Distribution')
        figures.append(fig2)
        
        # Error Analysis
        fig3 = plt.figure(figsize=(8, 6))
        error_data = metrics['error_analysis']
        states = list(error_data['ideal_counts'].keys())
        ideal_probs = [error_data['ideal_counts'][s]/1000 for s in states]
        noisy_probs = [error_data['noisy_counts'][s]/1000 for s in states]
        
        x = np.arange(len(states))
        width = 0.35
        plt.bar(x - width/2, ideal_probs, width, label='Ideal')
        plt.bar(x + width/2, noisy_probs, width, label='Noisy')
        plt.xticks(x, states, rotation=45)
        plt.legend()
        plt.title('Error Analysis')
        figures.append(fig3)
        
        # Performance Metrics
        fig4 = plt.figure(figsize=(8, 6))
        metrics_text = f"""
        Circuit Depth: {metrics['depth']}
        Circuit Width: {metrics['width']}
        Circuit Size: {metrics['size']}
        Execution Time: {metrics['execution_time']:.4f}s
        Error Rate: {metrics['error_analysis']['total_error_rate']:.4f}
        """
        plt.text(0.1, 0.5, metrics_text, fontsize=10)
        plt.axis('off')
        plt.title('Performance Metrics')
        figures.append(fig4)
        
        return figures

def run_analysis_suite():
    analyzer = QuantumCircuitAnalyzer()
    
    # Circuits
    circuits = {
        "Error Detection": create_error_detection_circuit(),
        "Register Simulation": create_quantum_register_simulation(),
        "Memory Operations": quantum_memory_operations(),
        "Arithmetic": quantum_arithmetic(),
        "Cache Simulation": quantum_cache_simulation(),
        "Pipeline": quantum_pipeline()
    }
    
    # Analyze
    results = {}
    for name, circuit in circuits.items():
        print(f"\nAnalyzing {name} circuit...")
        metrics = analyzer.analyze_circuit(circuit)
        
        figures = analyzer.visualize_results(circuit, metrics)
        
        results[name] = {
            'metrics': metrics,
            'figures': figures
        }
        
        # Summary
        print(f"\nResults for {name}:")
        print(f"Circuit depth: {metrics['depth']}")
        print(f"Total gates: {sum(metrics['gate_counts'].values())}")
        print(f"Error rate: {metrics['error_analysis']['total_error_rate']:.4f}")
        print(f"Execution time: {metrics['execution_time']:.4f}s")
    
    return results


def generate_performance_report(results: dict):
    report = "Quantum Circuit Performance Analysis\n"
    report += "=" * 40 + "\n\n"
    
    for name, data in results.items():
        report += f"\n{name} Circuit Analysis:\n"
        report += "-" * 20 + "\n"
        metrics = data['metrics']
        
        report += f"Circuit Metrics:\n"
        report += f"  - Depth: {metrics['depth']}\n"
        report += f"  - Width: {metrics['width']}\n"
        report += f"  - Total Gates: {sum(metrics['gate_counts'].values())}\n"
        
        report += f"\nGate Distribution:\n"
        for gate, count in metrics['gate_counts'].items():
            report += f"  - {gate}: {count}\n"
        
        report += f"\nPerformance:\n"
        report += f"  - Execution Time: {metrics['execution_time']:.4f}s\n"
        report += f"  - Error Rate: {metrics['error_analysis']['total_error_rate']:.4f}\n\n"
    
    return report

if __name__ == "__main__":
    # Run analysis
    results = run_analysis_suite()
    
    # Make report
    report = generate_performance_report(results)
    print(report)
    
    # Save figures
    for name, data in results.items():
        for i, fig in enumerate(data['figures']):
            fig.savefig(f'{name.lower().replace(" ", "_")}_{i+1}.png')