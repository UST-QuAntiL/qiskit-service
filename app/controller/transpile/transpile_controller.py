from flask_smorest import Blueprint

from app import routes
from app.model.circuit_response import (
    TranspileURLResponseSchema,
    TranspileDataResponseSchema,
    TranspileQASMResponseSchema
)
from app.model.algorithm_request import (
    TranspileURLRequestSchema,
    TranspileURLRequest,
    TranspileDataRequest,
    TranspileDataRequestSchema,
    TranspileQASMRequest,
    TranspileQASMRequestSchema
)

blp = Blueprint(
    "Transpile",
    __name__,
    description="Transpile",
)


@blp.route("/qiskit-service/api/v1.0/transpile", methods=["POST"])
@blp.arguments(
    TranspileURLRequestSchema,
    example=dict(
        url="https://raw.githubusercontent.com/UST-QuAntiL/nisq-analyzer-content/master/example-implementations"
            "/Grover-SAT/grover-fix-sat-qiskit.py",
        qpu_name="ibmq_qasm_simulator",
        impl_language="qiskit",
        token="YOUR-IBMQ-TOKEN"
    ),

)
@blp.response(200, TranspileURLResponseSchema)
def encoding(json: TranspileURLRequest):
    if json:
        return routes.transpile_circuit(json)


# @blp.route("/qiskit-service/api/v1.0/transpile", methods=["POST"])
# @blp.arguments(
#     TranspileDataRequestSchema,
#     example=dict(
#         data="https://raw.githubusercontent.com/UST-QuAntiL/nisq-analyzer-content/master/example-implementations"
#              "/Grover-SAT/grover-fix-sat-qiskit.py",
#         qpu_name="ibmq_qasm_simulator",
#         impl_language="qiskit",
#         token="YOUR-IBMQ-TOKEN"
#     )
# )
# @blp.response(200, TranspileDataResponseSchema)
# def encoding(json: TranspileDataRequest):
#     if json:
#         return routes.transpile_circuit()
#
#
# @blp.route("/qiskit-service/api/v1.0/transpile", methods=["POST"])
# @blp.arguments(
#     TranspileQASMRequestSchema,
#     example=dict(
#         url="https://raw.githubusercontent.com/UST-QuAntiL/nisq-analyzer-content/master/example-implementations"
#             "/Grover-SAT/grover-fix-sat-qiskit.py",
#         qpu_name="ibmq_qasm_simulator",
#         impl_language="qiskit",
#         token="YOUR-IBMQ-TOKEN"
#     )
# )
# @blp.response(200, TranspileQASMResponseSchema)
# def encoding(json: TranspileQASMRequest):
#     if json:
#         return routes.transpile_circuit()
