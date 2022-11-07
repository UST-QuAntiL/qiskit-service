from flask_smorest import Blueprint

from app import routes
from app.model.circuit_response import (
    TranspileResponseSchema,
)
from app.model.algorithm_request import (
    TranspileRequestSchema,
    TranspileRequest,
)

blp = Blueprint(
    "Transpile",
    __name__,
    description="Transpile",
)


@blp.route("/qiskit-service/api/v1.0/transpile", methods=["POST"])
@blp.arguments(
    TranspileRequestSchema,
    description='''\
                Transpile via URL:
                    \"impl-url\": \"URL-OF-IMPLEMENTATION\" 
                Transpile via data:
                    \"impl-data\": \"BASE64-ENCODED-IMPLEMENTATION\"
                Transpile via OpenQASM-String
                    \"qasm-string\": \"OpenQASM String\"
                ''',
    example={
        "impl-url": "https://raw.githubusercontent.com/UST-QuAntiL/nisq-analyzer-content/master/example-implementations"
            "/Grover-SAT/grover-fix-sat-qiskit.py",
        "qpu-name": "ibmq_qasm_simulator",
        "impl-language": "qiskit",
        "token": "YOUR-IBMQ-TOKEN"
    },

)
@blp.response(200, TranspileResponseSchema)
def encoding(json: TranspileRequest):
    if json:
        return routes.transpile_circuit(json)

