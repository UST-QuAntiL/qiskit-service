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


@blp.route("/qiskit-service/api/v1.0/calculate-calibration-matrix", methods=["GET"])
@blp.arguments(
    CalcCalibrationMatrixRequestSchema,
    example=dict(
        url="https://raw.githubusercontent.com/UST-QuAntiL/nisq-analyzer-content/master/example-implementations"
            "/Grover-SAT/grover-fix-sat-qiskit.py",
        qpu_name="ibmq_qasm_simulator",
        impl_language="qiskit",
        token="YOUR-IBMQ-TOKEN"
    )
)
@blp.response(200, CalcCalibrationMatrixResponseSchema)
def encoding(json: CalcCalibrationMatrixRequest):
    if json:
        return routes.calculate_calibration_matrix(json)
