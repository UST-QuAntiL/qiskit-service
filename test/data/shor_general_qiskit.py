from qiskit.algorithms.factorizers import Shor


def get_circuit(**kwargs):
    """Get circuit of Shor with input n."""
    N = kwargs["n"]
    shor = Shor(N)
    shor_circuit = shor.construct_circuit(measurement=True)
    return shor_circuit