from flask_smorest import Blueprint
from app.model.calculation_request import ProviderSchema
from app import routes

blp = Blueprint(
    "Get up-to-date data of QPUs",
    __name__,
    description="Get provider Information",
)


@blp.route("/qiskit-service/api/v1.0/providers", methods=["GET"])
@blp.response(200)
def encoding():
    return


@blp.route("/qiskit-service/api/v1.0/providers/f8f0c200-875d-0ff8-0352-1be4666c5829/qpus", methods=["GET"])
@blp.arguments(ProviderSchema, location="headers")
@blp.response(200)
def encoding(token):
    return routes.get_qpus_and_metrics_of_provider("f8f0c200-875d-0ff8-0352-1be4666c5829")
