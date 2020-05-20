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

from flask import make_response, jsonify
from app import app


@app.errorhandler(500)
def internal_server(error):
    return make_response(jsonify({'error': 'Internal Server Error', 'statusCode': '500'}), 500)


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found', 'statusCode': '404'}), 404)


@app.errorhandler(400)
def bad_request(error):
    return make_response(jsonify({'error': 'Bad Request', 'statusCode': '400'}), 400)
