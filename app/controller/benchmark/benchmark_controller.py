from flask_smorest import Blueprint

from app import routes
from app.model.circuit_response import (
    BenchmarkResponseSchema,
    ResultsResponseSchema
)
from app.model.calculation_request import (
    BenchmarkRequest,
    BenchmarkRequestSchema
)

blp = Blueprint(
    "Benchmark Request",
    __name__,
    description="Send QPU information, the width and depth of the circuit, the number of circuits you want to create, "
                "the number of shots and your IBM Quantum Experience token to the API to get the result on the IBM "
                "Quantum Simulator, and the stated QPU. The response also contains a link to the summary of the "
                "benchmark.",
)


@blp.route("/qiskit-service/api/v1.0/randomize", methods=["POST"])
@blp.doc(description="Please make sure that \"number-of-qubits\", \"number-of-circuits\" and "
                     "\"min-depth-of-circuit\" are greater than 0. "
                     "Also, \"max-depth-of-cicuit\" has to be greater or equal to \"min-depth-of-circuit\"")
@blp.arguments(
    BenchmarkRequestSchema,
    example={
        "qpu-name": "ibmq_qasm_simulator",
        "number-of-qubits": 3,
        "min-depth-of-circuit": 1,
        "max-depth-of-circuit": 2,
        "number-of-circuits": 3,
        "shots": 1024,
        "token": "YOUR-IBMQ-TOKEN",
        "clifford": False
    }
)
@blp.response(200, BenchmarkResponseSchema)
def encoding(json: BenchmarkRequest):
    if json:
        return routes.randomize(json)


@blp.route("/qiskit-service/api/v1.0/benchmarks/<benchmark_id>", methods=["GET"])
@blp.response(200, ResultsResponseSchema)
def encoding(json):
    if json:
        return
