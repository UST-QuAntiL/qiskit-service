import marshmallow as ma
from marshmallow import pre_load, ValidationError
import numpy as np


class BasisEncodingRequest:
    def __init__(self, vector, n_integral_bits, n_fractional_bits):
        self.vector = vector
        self.integral_bits = n_integral_bits
        self.fractional_bits = n_fractional_bits


class BasisEncodingRequestSchema(ma.Schema):
    vector = ma.fields.List(ma.fields.Float())
    integral_bits = ma.fields.Int()
    fractional_bits = ma.fields.Int()
