from qiskit import QuantumRegister, ClassicalRegister
from qiskit import QuantumCircuit

qc = QuantumCircuit()

q = QuantumRegister(5, 'q')
c = ClassicalRegister(3, 'c')

qc.add_register(q)
qc.add_register(c)

qc.h(q[0])
qc.h(q[1])
qc.h(q[2])
qc.h(q[1])
qc.cx(q[2], q[3])
qc.cu1(0, q[1], q[0])
qc.cx(q[2], q[4])
qc.h(q[0])
qc.cu1(0, q[1], q[2])
qc.cu1(0, q[0], q[2])
qc.h(q[2])
qc.measure(q[0], c[0])
qc.measure(q[1], c[1])
qc.measure(q[2], c[2])