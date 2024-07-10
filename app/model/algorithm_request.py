import marshmallow as ma


class GenerateCircuitRequest:
    def __init__(self, impl_url, impl_language, input_params):
        self.impl_url = impl_url
        self.impl_language = impl_language
        self.input_params = input_params


class GenerateCircuitRequestSchema(ma.Schema):
    impl_url = ma.fields.String()
    impl_language = ma.fields.String()
    input_params = ma.fields.List(ma.fields.String())


class TranspileRequest:
    def __init__(self, impl_url, impl_language, qasm_string, qpu_name, provider, input_params, token):
        self.impl_url = impl_url
        self.impl_language = impl_language
        self.qasm_string = qasm_string
        self.qpu_name = qpu_name
        self.provider = provider
        self.input_params = input_params
        self.token = token


class TranspileRequestSchema(ma.Schema):
    impl_url = ma.fields.String()
    impl_language = ma.fields.String()
    qasm_string = ma.fields.String()
    qpu_name = ma.fields.String()
    provider = ma.fields.String()
    input_params = ma.fields.List(ma.fields.String())
    token = ma.fields.String()


class ExecuteRequest:
    def __init__(self, impl_url, impl_language, qpu_name, provider, noise_model, only_measurement_errors, input_params,
                 token, correlation_id, post_processing_result):
        self.impl_url = impl_url
        self.impl_language = impl_language
        self.qpu_name = qpu_name
        self.provider = provider
        self.noise_model = noise_model
        self.only_measurement_errors = only_measurement_errors
        self.input_params = input_params
        self.token = token
        self.correlation_id = correlation_id


class ExecuteRequestSchema(ma.Schema):
    impl_url = ma.fields.String()
    impl_language = ma.fields.String()
    qpu_name = ma.fields.String()
    provider = ma.fields.String()
    input_params = ma.fields.List(ma.fields.String())
    token = ma.fields.String()
    noise_model = ma.fields.Str(required=False)
    only_measurement_errors = ma.fields.Boolean(required=False)
    correlation_id = ma.fields.String()
