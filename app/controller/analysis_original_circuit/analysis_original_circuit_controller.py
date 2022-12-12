from flask_smorest import Blueprint

from app import routes
from app.model.calculation_request import (
    AnalysisOriginalCircuitRequest,
    AnalysisOriginalCircuitRequestSchema
)
from app.model.circuit_response import (
    AnalysisOriginalCircuitResponseSchema
)


blp = Blueprint(
    "Analysis of Original Circuit",
    __name__,
    description="Request an analysis of the original circuit.",
)


@blp.route("/qiskit-service/api/v1.0/analyze-original-circuit", methods=["POST"])
@blp.arguments(
    AnalysisOriginalCircuitRequestSchema,
    example={
        "impl-url": "https://raw.githubusercontent.com/UST-QuAntiL/nisq-analyzer-content/master/example-implementations/Grover-SAT/grover-fix-sat-qiskit.py",
        "impl-language": "qiskit",
        "input-params":
        {
            "formula":
            {
                "rawValue": "(~A | B)",
                "type": "String"
            }
        }
    },

)
@blp.response(200, AnalysisOriginalCircuitResponseSchema)
def encoding(json: AnalysisOriginalCircuitRequest):
    if json:
        return routes.transpile_circuit(json)
