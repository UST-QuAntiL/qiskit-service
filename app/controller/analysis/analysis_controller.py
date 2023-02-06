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
@blp.doc(description="- Chi-Square-Distance: Large values indicate a strong deviation between the two histogram, "
                     "however it is not normalized and difficult to interpret. \n "
                     "- Correlation: Normalized between -1 and 1, where values close to 1 indicate a strong "
                     "correlation "
                     "between the histograms. "
                     "Since the histograms often have a similar shape even though the counts are erroneous, "
                     "the correlation often suggests success even for bad results. \n"
                     "- Percentage Error: Indicates the error in relation to the ideal value for each count "
                     "separately. This metric does not provide a general view on the quality of the result.\n"
                     "- Histogram Intersection: Returns a value that indicates how much of the histograms overlap."
                     "It is normalized between 0 and 1, where 1 would mean that the two histograms are the same."
                     "Therefore, it is a useful metric to judge the quality of the quantum computer's result.")
@blp.response(200)
def encoding():
    return routes.analysis


@blp.route("/qiskit-service/api/v1.0/analysis/<qpu_name>", methods=["GET"])
@blp.doc(description="- Chi-Square-Distance: Large values indicate a strong deviation between the two histogram, "
                     "however it is not normalized and difficult to interpret. \n "
                     "- Correlation: Normalized between -1 and 1, where values close to 1 indicate a strong "
                     "correlation "
                     "between the histograms. "
                     "Since the histograms often have a similar shape even though the counts are erroneous, "
                     "the correlation often suggests success even for bad results. \n"
                     "- Percentage Error: Indicates the error in relation to the ideal value for each count "
                     "separately. This metric does not provide a general view on the quality of the result.\n"
                     "- Histogram Intersection: Returns a value that indicates how much of the histograms overlap."
                     "It is normalized between 0 and 1, where 1 would mean that the two histograms are the same."
                     "Therefore, it is a useful metric to judge the quality of the quantum computer's result.")
@blp.response(200)
def encoding():
    return routes.analysis
