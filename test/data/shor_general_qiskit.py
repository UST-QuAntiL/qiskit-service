from qiskit.algorithms.factorizers import Shor


def get_circuit(**kwargs):
    """Get circuit of Shor with input n."""
    n = kwargs["n"]
    shor_circuit = Shor.construct_circuit(N=n, measurement=True)
    return shor_circuit
