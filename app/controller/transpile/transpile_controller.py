from flask_smorest import Blueprint

from app import routes
from app.model.algorithm_request import (TranspileRequestSchema, TranspileRequest, )
from app.model.circuit_response import (TranspileResponseSchema, )

blp = Blueprint("Transpile", __name__,
    description="Send implementation, input, QPU information, and your access token to the API to get "
                "analyzed properties of the transpiled circuit and the transpiled OpenQASM circuit itself.", )


@blp.route("/qiskit-service/api/v1.0/transpile", methods=["POST"])
@blp.doc(description="*Note*: \"token\" should either be in \"input-params\" or extra. *Note*: \"url\", \"hub\", "
                     "\"group\", \"project\" are optional such that otherwise the standard values are used.")
@blp.arguments(TranspileRequestSchema, description='''\
                Transpile via URL:
                    \"impl-url\": \"URL-OF-IMPLEMENTATION\" 
                Transpile via data:
                    \"impl-data\": \"BASE64-ENCODED-IMPLEMENTATION\"
                Transpile via OpenQASM-String
                    \"qasm-string\": \"OpenQASM String\"
                the \"input-params\"are of the form:
                    \"input-params\": {
                        \"PARAM-NAME-1\": {
                            \"rawValue\": \"YOUR-VALUE-1\",
                            \"type\": \"Integer\"
                        },
                        \"PARAM-NAME-2\": {
                            \"rawValue\": \"YOUR-VALUE-2\",
                            \"type\": \"String\"
                        },
                        ...
                        \"token\": {
                            \"rawValue\": \"YOUR-IBMQ-TOKEN\",
                            \"type\": \"Unknown\"
                        },
                        \"url\": {
                            \"rawValue\": \"YOUR-IBMQ-AUTHENTICATION-URL\",
                            \"type\": \"Unknown\"
                        },
                        \"hub\": {
                            \"rawValue\": \"YOUR-IBMQ-HUB\",
                            \"type\": \"Unknown\"
                        },
                        \"group\": {
                            \"rawValue\": \"YOUR-IBMQ-GROUP\",
                            \"type\": \"Unknown\"
                        },
                        \"project\": {
                            \"rawValue\": \"YOUR-IBMQ-PROJECT\",
                            \"type\": \"Unknown\"
                        }''', example={
    "impl-url": "https://raw.githubusercontent.com/UST-QuAntiL/nisq-analyzer-content/master/example-implementations"
                "/Grover-SAT/grover-fix-sat-qiskit.py", "qpu-name": "ibmq_qasm_simulator", "impl-language": "qiskit",
    "token": "YOUR-IBMQ-TOKEN", "input-params": {}},

)
@blp.response(200, TranspileResponseSchema)
def encoding(json: TranspileRequest):
    if json:
        return routes.transpile_circuit(json)
