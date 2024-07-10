from flask_smorest import Blueprint

from app.model.circuit_response import (ResultsResponseSchema)

blp = Blueprint("Results", __name__, description="Get execution results of an executed circuit.", )


@blp.route("/qiskit-service/api/v1.0/results/<id>", methods=["GET"])
@blp.response(200, ResultsResponseSchema)
def encoding(json):
    if json:
        return
