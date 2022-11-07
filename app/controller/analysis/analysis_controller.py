from flask_smorest import Blueprint

from app import routes


blp = Blueprint(
    "Analysis Request",
    __name__,
    description="Request an analysis of all benchmarks in the database that successfully returned a result. For those "
                "benchmarks, the histograms of the simulator's and the quantum computer's result are compared using "
                "the four metrics: Chi-Square-Distance, Correlation, Percentage Error and Histogram Intersection.",
)


@blp.route("/qiskit-service/api/v1.0/analysis", methods=["GET"])
@blp.response(200)
def encoding():
    return routes.analysis

