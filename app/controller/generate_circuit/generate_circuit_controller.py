from flask_smorest import Blueprint

from app import routes
from app.model.algorithm_request import (GenerateCircuitRequest, GenerateCircuitRequestSchema)
from app.model.circuit_response import (GenerateCircuitResponseSchema)

blp = Blueprint("Generate Circuit", __name__, description="Send implementation and input parameters to the API to "
                                                          "generate your circuit and get its properties.", )


@blp.route("/qiskit-service/api/v1.0/generate-circuit", methods=["POST"])
@blp.arguments(GenerateCircuitRequestSchema, description='''\
                Generation via URL:
                    \"impl-url\": \"URL-OF-IMPLEMENTATION\" 
                Generation via data:
                    \"impl-data\": \"BASE64-ENCODED-IMPLEMENTATION\"
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
                        ''', example={
    "impl-url": "https://raw.githubusercontent.com/UST-QuAntiL/nisq-analyzer-content/master/example-implementations"
                "/Grover-SAT/grover-fix-sat-qiskit.py", "impl-language": "qiskit", "input-params": {}})
@blp.response(200, GenerateCircuitResponseSchema,
              description="Returns a content location for the generated circuit and its properties. Access it via GET")
def encoding(json: GenerateCircuitRequest):
    if json:
        return routes.generate_circuit()
