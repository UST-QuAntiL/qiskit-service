from flask_smorest import Blueprint

from app import routes
from app.model.circuit_response import (
    CalcCalibrationMatrixResponseSchema
)
from app.model.calculation_request import (
    CalcCalibrationMatrixRequest,
    CalcCalibrationMatrixRequestSchema
)

blp = Blueprint(
    "Calibrate Matrix Calculation",
    __name__,
    description="Send QPU information, optional shots, and your IBM Quantum Experience token to the API to calculate "
                "the calibration matrix for the given QPU.",
)


@blp.route("/qiskit-service/api/v1.0/calculate-calibration-matrix", methods=["POST"])
@blp.arguments(
    CalcCalibrationMatrixRequestSchema,
    example={
        "qpu-name": "ibmq_qasm_simulator",
        "shots": 1024,
        "token": "YOUR-IBMQ-TOKEN"
    }
)
@blp.response(200, CalcCalibrationMatrixResponseSchema)
def encoding(json: CalcCalibrationMatrixRequest):
    if json:
        return routes.calculate_calibration_matrix(json)
