# ******************************************************************************
#  Copyright (c) 2020 University of Stuttgart
#
#  See the NOTICE file(s) distributed with this work for additional
#  information regarding copyright ownership.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
# ******************************************************************************


class ParameterDictionary(dict):

    """
    Definition of supported parameter types
    """
    __parameter_types = {
        "String" : str,
        "Integer" : int,
        "Float" : float,
        "Unknown" : str
    }

    """
        Converts a given parameter type definition pair to a parameter of the defined type. 
    """
    @classmethod
    def __convert_to_typed_parameter(cls, parameter):

        if not isinstance(parameter, dict):
            return None

        if "rawValue" not in parameter or "type" not in parameter:
            return None

        try:
            t = ParameterDictionary.__parameter_types[parameter['type']]
            value = parameter['rawValue']
            return t(value)
        except:
            return None

    """
        Initializes a typed parameter dictionary from the given raw dictionary
    """
    def __init__(self, other: dict):

        # Convert all the entries to typed entries
        for k, v in other.items():
            typed_value = ParameterDictionary.__convert_to_typed_parameter(v)
            self[k] = typed_value

    """
        Returns the given parameter (case insensitive)
    """
    def __getitem__(self, item):
        return super(ParameterDictionary, self).__getitem__(item.lower())

    """
       Sets the given parameter (case insensitive)
    """
    def __setitem__(self, key, value):

        if isinstance(value, dict):
            t_value = ParameterDictionary.__convert_to_typed_parameter(value)
        else:
            t_value = value

        super(ParameterDictionary, self).__setitem__(key.lower(), t_value)