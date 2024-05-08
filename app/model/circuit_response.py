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


class GeneratedCircuitsResponse:
    def __init__(self, original_depth, original_multi_qubit_gate_depth, original_number_of_measurement_operations,
                 original_number_of_multi_qubit_gates, original_number_of_single_qubit_gates,
                 original_total_number_of_operations, generated_circuit, original_width):
        super().__init__()
        self.original_depth = original_depth
        self.original_multi_qubit_gate_depth = original_multi_qubit_gate_depth
        self.original_number_of_measurement_operations = original_number_of_measurement_operations
        self.original_number_of_multi_qubit_gates = original_number_of_multi_qubit_gates
        self.original_number_of_single_qubit_gates = original_number_of_single_qubit_gates
        self.original_total_number_of_operations = original_total_number_of_operations
        self.generated_circuit = generated_circuit
        self.original_width = original_width

    def to_json(self):
        json_generate_circuit_response = {"original-depth": self.original_depth,
                                          "original-multi-qubit-gate-depth": self.original_multi_qubit_gate_depth,
                                          "original-number-of-measurement-operations": self.original_number_of_measurement_operations,
                                          "original-number-of-multi_qubit-gates": self.original_number_of_multi_qubit_gates,
                                          "original-number-of-single-qubit-gates": self.original_number_of_single_qubit_gates,
                                          "original-total-number-of-operations": self.original_total_number_of_operations,
                                          "generated-circuit": self.generated_circuit,
                                          "original-width": self.original_width, }
        return json_generate_circuit_response


class GeneratedCircuitsResponseSchema(ma.Schema):
    original_depth = ma.fields.Int()
    original_multi_qubit_gate_depth = ma.fields.Int()
    original_number_of_measurement_operations = ma.fields.Int()
    original_number_of_multi_qubit_gates = ma.fields.Int()
    original_number_of_single_qubit_gates = ma.fields.Int()
    original_total_number_of_operations = ma.fields.Int()
    generated_circuit = ma.fields.String()
    original_width = ma.fields.Int()

    @property
    def input(self):
        raise NotImplementedError


class TranspileResponse:
    def __init__(self, depth, multi_qubit_gate_depth, number_of_measurement_operations, number_of_multi_qubit_gates,
                 number_of_single_qubit_gates, total_number_of_operations, transpiled_qasm, width):
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
        json_transpile_response = {"depth": self.depth, "multi_qubit_gate_depth": self.multi_qubit_gate_depth,
                                   "number_of_measurement_operations": self.number_of_measurement_operations,
                                   "number_of_multi_qubit_gates": self.number_of_multi_qubit_gates,
                                   "number_of_single_qubit_gates": self.number_of_single_qubit_gates,
                                   "total_number_of_operations": self.total_number_of_operations,
                                   "transpiled_qasm": self.transpiled_qasm, "width": self.width, }
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


class GenerateCircuitResponseSchema(ma.Schema):
    location = ma.fields.String()


class BenchmarkResponseSchema(ma.Schema):
    list = ma.fields.List(ma.fields.String())


class ResultsResponseSchema(ma.Schema):
    result = ma.fields.List(ma.fields.String())


class AnalysisOriginalCircuitResponse:
    def __init__(self, original_depth, original_multi_qubit_gate_depth, original_number_of_measurement_operations,
                 original_number_of_multi_qubit_gates, original_number_of_single_qubit_gates,
                 original_total_number_of_operations, original_width):
        super().__init__()
        self.original_depth = original_depth
        self.original_multi_qubit_gate_depth = original_multi_qubit_gate_depth
        self.original_number_of_measurement_operations = original_number_of_measurement_operations
        self.original_number_of_multi_qubit_gates = original_number_of_multi_qubit_gates
        self.original_number_of_single_qubit_gates = original_number_of_single_qubit_gates
        self.original_total_number_of_operations = original_total_number_of_operations
        self.original_width = original_width

    def to_json(self):
        json_generate_circuit_response = {"original-depth": self.original_depth,
                                          "original-multi-qubit-gate-depth": self.original_multi_qubit_gate_depth,
                                          "original-number-of-measurement-operations": self.original_number_of_measurement_operations,
                                          "original-number-of-multi_qubit-gates": self.original_number_of_multi_qubit_gates,
                                          "original-number-of-single-qubit-gates": self.original_number_of_single_qubit_gates,
                                          "original-total-number-of-operations": self.original_total_number_of_operations,
                                          "original-width": self.original_width, }
        return json_generate_circuit_response


class AnalysisOriginalCircuitResponseSchema(ma.Schema):
    original_depth = ma.fields.Int()
    original_multi_qubit_gate_depth = ma.fields.Int()
    original_number_of_measurement_operations = ma.fields.Int()
    original_number_of_multi_qubit_gates = ma.fields.Int()
    original_number_of_single_qubit_gates = ma.fields.Int()
    original_total_number_of_operations = ma.fields.Int()
    original_width = ma.fields.Int()

    @property
    def input(self):
        raise NotImplementedError
