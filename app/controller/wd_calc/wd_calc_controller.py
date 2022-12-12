from flask_smorest import Blueprint


blp = Blueprint(
    "Wd Request",
    __name__,
    description="Request the wd-value of a specific Quantum Computer based on the clifford gate circuit data in your database",
)


@blp.route("/qiskit-service/api/v1.0/calc-wd/<qpu_name>", methods=["GET"])
@blp.response(200, description="There needs to be at least 10 data points for each number of qubits and depth to get a meaningful result.")
def encoding():
    return


