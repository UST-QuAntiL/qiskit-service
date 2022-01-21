# ******************************************************************************
#  Copyright (c) 2021 University of Stuttgart
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

import unittest
import os
from app.config import basedir
from app import app, db
import qiskit


class TranspileTestCase(unittest.TestCase):

    def setUp(self):

        # setup environment variables for testing
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///" + os.path.join(basedir, 'test.db')

        self.client = app.test_client()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_version(self):

        response = self.client.get('/qiskit-service/api/v1.0/version')

        self.assertEqual(response.status_code, 200)
        json_data = response.get_json()
        self.assertTrue("version" in json_data)
        self.assertEqual(json_data['version'], "1.0")

    def test_randomize_full_request(self):

        # prepare the request
        token = qiskit.IBMQ.stored_account()['token']
        request = {
            'qpu-name': 'ibmq_qasm_simulator',
            'number-of-qubits': 1,
            'min-depth-of-circuit': 1,
            'max-depth-of-circuit': 1,
            'number-of-circuits': 1,
            'shots': 1024,
            'token': token
        }

        # send the request
        response = self.client.post('/qiskit-service/api/v1.0/randomize', json=request)

        self.assertEqual(response.status_code, 200)
        json_data = response.get_json()
        self.assertEqual(1, len(json_data))
        self.assertEqual(3, len(json_data[0]))
        print(json_data[0])
        self.assertIn("result-benchmark", json_data[0])
        self.assertIn("result-simulator", json_data[0])
        self.assertIn("result-real-backend", json_data[0])


    def test_randomize_no_shots_request(self):

        # prepare the request
        token = qiskit.IBMQ.stored_account()['token']
        request = {
            'qpu-name': 'ibmq_qasm_simulator',
            'number-of-qubits': 1,
            'min-depth-of-circuit': 1,
            'max-depth-of-circuit': 1,
            'number-of-circuits': 1,
            'token': token
        }

        # send the request
        response = self.client.post('/qiskit-service/api/v1.0/randomize', json=request)

        self.assertEqual(response.status_code, 200)
        json_data = response.get_json()
        self.assertEqual(1, len(json_data))
        self.assertEqual(3, len(json_data[0]))
        self.assertIn("result-benchmark", json_data[0])
        self.assertIn("result-simulator", json_data[0])
        self.assertIn("result-real-backend", json_data[0])


if __name__ == "__main__":
    unittest.main()