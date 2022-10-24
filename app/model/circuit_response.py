from datetime import datetime
import marshmallow as ma


from app.model.algorithm_request import (
    TranspileURLRequestSchema,
    TranspileDataRequestSchema,
    TranspileQASMRequestSchema,
    ExecuteDataRequestSchema,
    ExecuteURLRequestSchema,
    ExecuteQASMRequestSchema,
    BatchExecuteRequestSchema,
)

from app.model.calculation_request import (
    CalcCalibrationMatrixRequestSchema,
    BenchmarkRequestSchema
)


class CircuitResponse:
    def __init__(self, circuit, circuit_type, n_qubits, depth, input):
        super().__init__()
        self.circuit = circuit
        self.circuit_type = circuit_type
        self.n_qubits = n_qubits
        self.depth = depth
        self.input = input
        self.timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    def to_json(self):
        json_circuit_response = {
            "circuit": self.circuit,
            "circuit_type": self.circuit_type,
            "n_qubits": self.n_qubits,
            "depth": self.depth,
            "timestamp": self.timestamp,
            "input": self.input,
        }
        return json_circuit_response


class CircuitResponseSchema(ma.Schema):
    circuit = ma.fields.String()
    circuit_type = ma.fields.String()
    n_qubits = ma.fields.Int()
    depth = ma.fields.Int()
    timestamp = ma.fields.String()

    @property
    def input(self):
        raise NotImplementedError


class TranspileURLResponseSchema(CircuitResponseSchema):
    input = ma.fields.Nested(TranspileURLRequestSchema)


class TranspileDataResponseSchema(CircuitResponseSchema):
    input = ma.fields.Nested(TranspileDataRequestSchema)


class TranspileQASMResponseSchema(CircuitResponseSchema):
    input = ma.fields.Nested(TranspileQASMRequestSchema)


class ExecuteURLResponseSchema(CircuitResponseSchema):
    input = ma.fields.Nested(ExecuteURLRequestSchema)


class ExecuteDataResponseSchema(CircuitResponseSchema):
    input = ma.fields.Nested(ExecuteDataRequestSchema)


class ExecuteQASMResponseSchema(CircuitResponseSchema):
    input = ma.fields.Nested(ExecuteQASMRequestSchema)


class BatchExecuteResponseSchema(CircuitResponseSchema):
    input = ma.fields.Nested(BatchExecuteRequestSchema)


class CalcCalibrationMatrixResponseSchema(CircuitResponseSchema):
    input = ma.fields.Nested(CalcCalibrationMatrixRequestSchema)


class BenchmarkResponseSchema(CircuitResponseSchema):
    input = ma.fields.Nested(BenchmarkRequestSchema)
