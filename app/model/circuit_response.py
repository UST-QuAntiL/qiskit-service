import marshmallow as ma


class CircuitResponseSchema(ma.Schema):
    circuit = ma.fields.String()
    circuit_type = ma.fields.String()
    n_qubits = ma.fields.Int()
    depth = ma.fields.Int()
    timestamp = ma.fields.String()

    @property
    def input(self):
        raise NotImplementedError


class TranspileResponse:
    def __init__(self, depth, multi_qubit_gate_depth, number_of_measurement_operations, number_of_multi_qubit_gates, number_of_single_qubit_gates, total_number_of_operations, transpiled_qasm, width):
        super().__init__()
        self.depth = depth
        self.multi_qubit_gate_depth = multi_qubit_gate_depth
        self.number_of_measurement_operations = number_of_measurement_operations
        self.number_of_multi_qubit_gates = number_of_multi_qubit_gates
        self.number_of_single_qubit_gates = number_of_single_qubit_gates
        self.total_number_of_operations = total_number_of_operations
        self.transpiled_qasm = transpiled_qasm
        self.width = width

    def to_json(self):
        json_transpile_response = {
             "depth": self.depth,
             "multi_qubit_gate_depth": self.multi_qubit_gate_depth,
             "number_of_measurement_operations": self.number_of_measurement_operations,
             "number_of_multi_qubit_gates": self.number_of_multi_qubit_gates,
             "number_of_single_qubit_gates": self.number_of_single_qubit_gates,
             "total_number_of_operations": self.total_number_of_operations,
             "transpiled_qasm": self.transpiled_qasm,
             "width": self.width,
        }
        return json_transpile_response


class TranspileResponseSchema(ma.Schema):
    depth = ma.fields.Int()
    multi_qubit_gate_depth = ma.fields.Int()
    number_of_measurement_operations = ma.fields.Int()
    number_of_multi_qubit_gates = ma.fields.Int()
    number_of_single_qubit_gates = ma.fields.Int()
    total_number_of_operations = ma.fields.Int()
    transpiled_qasm = ma.fields.String()
    width = ma.fields.Int()

    @property
    def input(self):
        raise NotImplementedError


class ExecuteResponseSchema(ma.Schema):
    location = ma.fields.String()

    @property
    def input(self):
        raise NotImplementedError


class CalcCalibrationMatrixResponseSchema(ma.Schema):
    location = ma.fields.String()


class BenchmarkResponseSchema(ma.Schema):
    list = ma.fields.List(ma.fields.String())
