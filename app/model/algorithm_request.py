import marshmallow as ma
from marshmallow import pre_load, ValidationError
import numpy as np


class TranspileURLRequest:
    def __init__(self, url, impl_language, qpu_name, input_params, token):
        self.url = url
        self.impl_language = impl_language
        self.qpu_name = qpu_name
        self.input_params = input_params
        self.token = token


class TranspileURLRequestSchema(ma.Schema):
    url = ma.fields.String()
    impl_language = ma.fields.String()
    qpu_name = ma.fields.String()
    input_params = ma.fields.List(ma.fields.String())
    token = ma.fields.String()


class TranspileDataRequest:
    def __init__(self, url, impl_language, qpu_name, input_params, token):
        self.url = url
        self.impl_language = impl_language
        self.qpu_name = qpu_name
        self.input_params = input_params
        self.token = token


class TranspileDataRequestSchema(ma.Schema):
    data = ma.fields.String()
    impl_language = ma.fields.String()
    qpu_name = ma.fields.String()
    input_params = ma.fields.List(ma.fields.String())
    token = ma.fields.String()


class TranspileQASMRequest:
    def __init__(self, url, impl_language, qpu_name, input_params, token):
        self.url = url
        self.impl_language = impl_language
        self.qpu_name = qpu_name
        self.input_params = input_params
        self.token = token


class TranspileQASMRequestSchema(ma.Schema):
    qasm = ma.fields.String()
    impl_language = ma.fields.String()
    qpu_name = ma.fields.String()
    input_params = ma.fields.List(ma.fields.String())
    token = ma.fields.String()


class ExecuteURLRequest:
    def __init__(self, url, impl_language, qpu_name, input_params, token):
        self.url = url
        self.impl_language = impl_language
        self.qpu_name = qpu_name
        self.input_params = input_params
        self.token = token


class ExecuteURLRequestSchema(ma.Schema):
    url = ma.fields.String()
    impl_language = ma.fields.String()
    qpu_name = ma.fields.String()
    input_params = ma.fields.List(ma.fields.String())
    token = ma.fields.String()


class ExecuteDataRequest:
    def __init__(self, url, impl_language, qpu_name, input_params, token):
        self.url = url
        self.impl_language = impl_language
        self.qpu_name = qpu_name
        self.input_params = input_params
        self.token = token


class ExecuteDataRequestSchema(ma.Schema):
    data = ma.fields.String()
    impl_language = ma.fields.String()
    qpu_name = ma.fields.String()
    input_params = ma.fields.List(ma.fields.String())
    token = ma.fields.String()


class ExecuteQASMRequest:
    def __init__(self, url, impl_language, qpu_name, input_params, token):
        self.url = url
        self.impl_language = impl_language
        self.qpu_name = qpu_name
        self.input_params = input_params
        self.token = token


class ExecuteQASMRequestSchema(ma.Schema):
    qasm = ma.fields.String()
    impl_language = ma.fields.String()
    qpu_name = ma.fields.String()
    input_params = ma.fields.List(ma.fields.String())
    token = ma.fields.String()


class BatchExecuteRequest:
    def __init__(self, url, impl_language, qpu_name, input_params, token):
        self.url = url
        self.impl_language = impl_language
        self.qpu_name = qpu_name
        self.input_params = input_params
        self.token = token


class BatchExecuteRequestSchema(ma.Schema):
    url = ma.fields.List(ma.fields.String())
    impl_language = ma.fields.String()
    qpu_name = ma.fields.String()
    input_params = ma.fields.List(ma.fields.String())
    token = ma.fields.String()
