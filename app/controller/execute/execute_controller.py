from flask_smorest import Blueprint

from app import routes
from app.model.circuit_response import (
    ExecuteURLResponseSchema,
    ExecuteDataResponseSchema,
    ExecuteQASMResponseSchema,
    BatchExecuteResponseSchema
)
from app.model.algorithm_request import (
    ExecuteURLRequest,
    ExecuteURLRequestSchema,
    ExecuteDataRequest,
    ExecuteDataRequestSchema,
    ExecuteQASMRequest,
    ExecuteQASMRequestSchema,
    BatchExecuteRequest,
    BatchExecuteRequestSchema
)

blp = Blueprint(
    "Execute",
    __name__,
    description="execute",
)


@blp.route("/qiskit-service/api/v1.0/execute", methods=["POST"])
@blp.arguments(
    ExecuteURLRequestSchema,
    example=dict(
        url="https://raw.githubusercontent.com/UST-QuAntiL/nisq-analyzer-content/master/example-implementations"
            "/Grover-SAT/grover-fix-sat-qiskit.py",
        qpu_name="ibmq_qasm_simulator",
        impl_language="qiskit",
        token="YOUR-IBMQ-TOKEN"
    )
)
@blp.response(200, ExecuteURLResponseSchema)
def encoding(json: ExecuteURLRequest):
    if json:
        return routes.transpile_circuit()


# @blp.route("/qiskit-service/api/v1.0/execute", methods=["POST"])
# @blp.arguments(
#     ExecuteDataRequestSchema,
#     example=dict(
#         url="https://raw.githubusercontent.com/UST-QuAntiL/nisq-analyzer-content/master/example-implementations"
#             "/Grover-SAT/grover-fix-sat-qiskit.py",
#         qpu_name="ibmq_qasm_simulator",
#         impl_language="qiskit",
#         token="YOUR-IBMQ-TOKEN"
#     )
# )
# @blp.response(200, ExecuteDataResponseSchema)
# def encoding(json: ExecuteDataRequest):
#     if json:
#         return routes.transpile_circuit()
#
#
# @blp.route("/qiskit-service/api/v1.0/execute", methods=["POST"])
# @blp.arguments(
#     ExecuteQASMRequestSchema,
#     example=dict(
#         url="https://raw.githubusercontent.com/UST-QuAntiL/nisq-analyzer-content/master/example-implementations"
#             "/Grover-SAT/grover-fix-sat-qiskit.py",
#         qpu_name="ibmq_qasm_simulator",
#         impl_language="qiskit",
#         token="YOUR-IBMQ-TOKEN"
#     )
# )
# @blp.response(200, ExecuteQASMResponseSchema)
# def encoding(json: ExecuteQASMRequest):
#     if json:
#         return routes.transpile_circuit()
#
#
# @blp.route("/qiskit-service/api/v1.0/execute", methods=["POST"])
# @blp.arguments(
#     BatchExecuteRequestSchema,
#     example=dict(
#         url=["https://raw.githubusercontent.com/UST-QuAntiL/nisq-analyzer-content/master/example-implementations"
#              "/Grover-SAT/grover-fix-sat-qiskit.py",
#              "https://raw.githubusercontent.com/UST-QuAntiL/nisq-analyzer-content/master/example-implementations/Shor"
#              "/shor-general-qiskit.py"],
#         qpu_name="ibmq_qasm_simulator",
#         impl_language="qiskit",
#         input_params={
#             "N": {
#                 "rawValue": "9",
#                 "type": "Integer"
#             },
#             "formula": {
#                 "rawValue": "(~A | B)",
#                 "type": "String"
#             }
#         },
#         token="YOUR-IBMQ-TOKEN"
#     )
# )
# @blp.response(200, BatchExecuteResponseSchema)
# def encoding(json: BatchExecuteRequest):
#     if json:
#         return routes.transpile_circuit()