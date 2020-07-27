from qiskit.aqua.algorithms.factorizers import Shor


def get_circuit(**kwargs):
    """Get circuit of Shor with input n."""
    n = kwargs["n"]
    shor = Shor(n)
    shor_circuit = shor.construct_circuit(measurement=True)
    return shor_circuit