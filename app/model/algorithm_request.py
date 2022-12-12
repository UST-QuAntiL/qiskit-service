import marshmallow as ma


class TranspileRequest:
    def __init__(self, impl_url, impl_language, qpu_name, input_params, token):
        self.impl_url = impl_url
        self.impl_language = impl_language
        self.qpu_name = qpu_name
        self.input_params = input_params
        self.token = token


class TranspileRequestSchema(ma.Schema):
    impl_url = ma.fields.String()
    impl_language = ma.fields.String()
    qpu_name = ma.fields.String()
    input_params = ma.fields.List(ma.fields.String())
    token = ma.fields.String()


class ExecuteRequest:
    def __init__(self, impl_url, impl_language, qpu_name, noise_model, only_measurement_errors, input_params, token):
        self.impl_url = impl_url
        self.impl_language = impl_language
        self.qpu_name = qpu_name
        self.noise_model = noise_model
        self.only_measurement_errors = only_measurement_errors
        self.input_params = input_params
        self.token = token


class ExecuteRequestSchema(ma.Schema):
    impl_url = ma.fields.String()
    impl_language = ma.fields.String()
    qpu_name = ma.fields.String()
    input_params = ma.fields.List(ma.fields.String())
    token = ma.fields.String()
    noise_model = ma.fields.Str(required=False)
    only_measurement_errors = ma.fields.Boolean(required=False)
