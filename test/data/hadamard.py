import qiskit

def get_circuit(**kwargs):

    reg = qiskit.QuantumRegister(1, "q")
    circuit = qiskit.QuantumCircuit(reg)
    circuit.h(reg)
    circuit.measure_all()

    return circuit

if __name__ == "__main__":

    c = get_circuit()
    print(c)
