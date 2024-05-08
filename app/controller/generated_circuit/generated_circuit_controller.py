from flask_smorest import Blueprint

from app.model.circuit_response import (GeneratedCircuitsResponseSchema)

blp = Blueprint("Generated-Circuits", __name__, description="", )


@blp.route("/qiskit-service/api/v1.0/generated-circuits/<id>", methods=["GET"])
@blp.response(200, GeneratedCircuitsResponseSchema)
def encoding(json):
    if json:
        return
