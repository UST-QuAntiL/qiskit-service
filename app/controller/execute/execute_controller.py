from flask_smorest import Blueprint

from app import routes
from app.model.circuit_response import (
    ExecuteResponseSchema
)
from app.model.algorithm_request import (
    ExecuteRequest,
    ExecuteRequestSchema
)

blp = Blueprint(
    "Execute",
    __name__,
    description="execute",
)


@blp.route("/qiskit-service/api/v1.0/execute", methods=["POST"])
@blp.arguments(
    ExecuteRequestSchema,
    description='''\
                Execution via URL:
                    \"impl-url\": \"URL-OF-IMPLEMENTATION\" 
                Execution via data:
                    \"impl-data\": \"BASE64-ENCODED-IMPLEMENTATION\"
                Execution via OpenQASM-String:
                    \"qasm-string\": \"OpenQASM String\"
                Execution via transpiled OpenQASM String:
                    \"transpiled-qasm\":\"TRANSPILED-QASM-STRING\" 
                for Batch Execution of multiple circuits use:
                    \"impl-url\": [\"URL-OF-IMPLEMENTATION-1\", \"URL-OF-IMPLEMENTATION-2\"]''',
    example={
        "impl-url": "https://raw.githubusercontent.com/UST-QuAntiL/nisq-analyzer-content/master/example-implementations"
            "/Grover-SAT/grover-fix-sat-qiskit.py",
        "qpu-name": "ibmq_qasm_simulator",
        "impl-language": "qiskit",
        "token": "YOUR-IBMQ-TOKEN"
    }
)
@blp.response(200, ExecuteResponseSchema)
def encoding(json: ExecuteRequest):
    if json:
        return routes.transpile_circuit()

