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
    def __init__(self, qpu_name, number_of_qubits, min_depth, max_depth, number_of_circuits, shots, token):
        self.qpu_name = qpu_name
        self.number_of_qubits = number_of_qubits
        self.min_depth = min_depth
        self.max_depth = max_depth
        self.number_of_circuits = number_of_circuits
        self.token = token
        self.shots = shots


class BenchmarkRequestSchema(ma.Schema):
    qpu_name = ma.fields.String()
    number_of_qubits = ma.fields.Int()
    min_depth = ma.fields.Int()
    max_depth = ma.fields.Int()
    number_of_circuits = ma.fields.Int()
    token = ma.fields.String()
    shots = ma.fields.Int()


