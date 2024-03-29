import marshmallow as ma


class CalcCalibrationMatrixRequest:
    def __init__(self, qpu_name, shots, token):
        self.qpu_name = qpu_name
        self.token = token
        self.shots = shots


class CalcCalibrationMatrixRequestSchema(ma.Schema):
    qpu_name = ma.fields.String()
    token = ma.fields.String()
    shots = ma.fields.Int()


class BenchmarkRequest:
    def __init__(self, qpu_name, number_of_qubits, min_depth, max_depth, number_of_circuits, shots, token, clifford):
        self.qpu_name = qpu_name
        self.number_of_qubits = number_of_qubits
        self.min_depth = min_depth
        self.max_depth = max_depth
        self.number_of_circuits = number_of_circuits
        self.token = token
        self.shots = shots
        self.clifford = clifford


class BenchmarkRequestSchema(ma.Schema):
    qpu_name = ma.fields.String()
    number_of_qubits = ma.fields.Int()
    min_depth = ma.fields.Int()
    max_depth = ma.fields.Int()
    number_of_circuits = ma.fields.Int()
    token = ma.fields.String()
    shots = ma.fields.Int()
    clifford = ma.fields.Boolean()


class AnalysisOriginalCircuitRequest:
    def __init__(self, impl_url, impl_language, input_params):
        self.impl_url = impl_url
        self.impl_language = impl_language
        self.input_params = input_params


class AnalysisOriginalCircuitRequestSchema(ma.Schema):
    impl_url = ma.fields.String()
    impl_language = ma.fields.String()
    input_params = ma.fields.List(ma.fields.String())


class ProviderSchema(ma.Schema):
    token = ma.fields.String(required=True)
