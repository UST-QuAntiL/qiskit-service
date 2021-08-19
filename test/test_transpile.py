# ******************************************************************************
#  Copyright (c) 2020-2021 University of Stuttgart
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
import base64


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

    def test_transpile_hadamard_simulator_url(self):

        # prepare the request
        token = qiskit.IBMQ.stored_account()['token']
        request = {
            'impl-url': "https://raw.githubusercontent.com/PlanQK/qiskit-service/master/test/data/hadamard.py",
            'impl-language': 'Qiskit',
            'qpu-name': "ibmq_qasm_simulator",
            'input-params': {},
            'token': token
        }

        # send the request
        response = self.client.post('/qiskit-service/api/v1.0/transpile',
                                    json=request)

        self.assertEqual(response.status_code, 200)
        json_data = response.get_json()
        self.assertIn("width", json_data)
        self.assertIn("depth", json_data)
        self.assertEqual(json_data['depth'], 2)
        self.assertEqual(json_data['width'], 1)
        self.assertIn('transpiled-qasm', json_data)
        self.assertIn("number-of-gates", json_data)
        self.assertIn("number-of-multi-qubit-gates", json_data)
        self.assertIn("multi-qubit-gate-depth", json_data)
        self.assertGreaterEqual(json_data["number-of-gates"], 2)
        self.assertEqual(json_data["number-of-multi-qubit-gates"], 0)
        self.assertEqual(json_data["multi-qubit-gate-depth"], 0)
        self.assertIsNotNone(json_data.get('transpiled-qasm'))

        r = self.client.post('/qiskit-service/api/v1.0/execute', json=request)
        self.assertEqual(r.status_code, 202)
        print(r.headers.get("Location"))

    def test_transpile_hadamard_simulator_file(self):

        # prepare the request
        token = qiskit.IBMQ.stored_account()['token']
        with open('data/hadamard.py', 'rb') as f:
            impl_data = base64.b64encode(f.read()).decode()
        request = {
            'impl-data': impl_data,
            'impl-language': 'Qiskit',
            'qpu-name': "ibmq_qasm_simulator",
            'input-params': {},
            'token': token
        }

        # send the request
        response = self.client.post('/qiskit-service/api/v1.0/transpile',
                                    json=request)

        self.assertEqual(response.status_code, 200)
        json_data = response.get_json()
        self.assertIn("width", json_data)
        self.assertIn("depth", json_data)
        self.assertEqual(json_data['depth'], 2)
        self.assertEqual(json_data['width'], 1)
        self.assertIn('transpiled-qasm', json_data)
        self.assertIn("number-of-gates", json_data)
        self.assertIn("number-of-multi-qubit-gates", json_data)
        self.assertIn("multi-qubit-gate-depth", json_data)
        self.assertGreaterEqual(json_data["number-of-gates"], 2)
        self.assertEqual(json_data["number-of-multi-qubit-gates"], 0)
        self.assertEqual(json_data["multi-qubit-gate-depth"], 0)
        self.assertIsNotNone(json_data.get('transpiled-qasm'))

        r = self.client.post('/qiskit-service/api/v1.0/execute', json=request)
        self.assertEqual(r.status_code, 202)
        print(r.headers.get("Location"))

    def test_transpile_shor_lima_file(self):

        # prepare the request
        token = qiskit.IBMQ.stored_account()['token']
        with open('data/shor-fix-15.py', 'rb') as f:
            impl_data = base64.b64encode(f.read()).decode()
        request = {
            'impl-data': impl_data,
            'impl-language': 'Qiskit',
            'qpu-name': "ibmq_lima",
            'input-params': {},
            'token': token
        }

        # send the request
        response = self.client.post('/qiskit-service/api/v1.0/transpile',
                                    json=request)

        self.assertEqual(response.status_code, 200)
        json_data = response.get_json()
        self.assertIn("width", json_data)
        self.assertIn("depth", json_data)
        self.assertGreaterEqual(json_data['depth'], 8)
        self.assertGreaterEqual(json_data['width'], 3)
        self.assertIn('transpiled-qasm', json_data)
        self.assertIn("number-of-gates", json_data)
        self.assertIn("number-of-multi-qubit-gates", json_data)
        self.assertIn("multi-qubit-gate-depth", json_data)
        self.assertGreaterEqual(json_data["number-of-gates"], 10)
        self.assertGreaterEqual(json_data["number-of-multi-qubit-gates"], 6)
        self.assertGreaterEqual(json_data["multi-qubit-gate-depth"], 6)
        self.assertIsNotNone(json_data.get('transpiled-qasm'))

        r = self.client.post('/qiskit-service/api/v1.0/execute', json=request)
        self.assertEqual(r.status_code, 202)
        print(r.headers.get("Location"))

    def test_transpile_shor_lima_url_qasm(self):

        # prepare the request
        token = qiskit.IBMQ.stored_account()['token']
        request = {
            'impl-url': 'https://quantum-circuit.com/api/get/circuit/KzG7MxH6hpBpM9pCt?format=qasm',
            'impl-language': 'OpenQASM',
            'qpu-name': "ibmq_lima",
            'input-params': {},
            'token': token
        }

        # send the request
        response = self.client.post('/qiskit-service/api/v1.0/transpile',
                                    json=request)

        self.assertEqual(response.status_code, 200)
        json_data = response.get_json()
        self.assertIn("width", json_data)
        self.assertIn("depth", json_data)
        self.assertGreaterEqual(json_data['depth'], 8)
        self.assertGreaterEqual(json_data['width'], 4)
        self.assertIn('transpiled-qasm', json_data)
        self.assertIn("number-of-gates", json_data)
        self.assertIn("number-of-multi-qubit-gates", json_data)
        self.assertIn("multi-qubit-gate-depth", json_data)
        self.assertIsNotNone(json_data["number-of-gates"])
        self.assertIsNotNone(json_data["number-of-multi-qubit-gates"])
        self.assertIsNotNone(json_data["multi-qubit-gate-depth"])
        self.assertIsNotNone(json_data.get('transpiled-qasm'))

        r = self.client.post('/qiskit-service/api/v1.0/execute', json=request)
        self.assertEqual(r.status_code, 202)
        print(r.headers.get("Location"))

    def test_transpile_shor_santiago_file_qasm(self):

        # prepare the request
        token = qiskit.IBMQ.stored_account()['token']
        with open('data/shor-fix-15.qasm', 'rb') as f:
            impl_data = base64.b64encode(f.read()).decode()
        request = {
            'impl-data': impl_data,
            'impl-language': 'OpenQASM',
            'qpu-name': "ibmq_santiago",
            'input-params': {},
            'token': token
        }

        # send the request
        response = self.client.post('/qiskit-service/api/v1.0/transpile',
                                    json=request)

        self.assertEqual(response.status_code, 200)
        json_data = response.get_json()
        self.assertIn("width", json_data)
        self.assertIn("depth", json_data)
        self.assertLessEqual(json_data['depth'], 18)
        self.assertLessEqual(json_data['width'], 7)
        self.assertIn('transpiled-qasm', json_data)
        self.assertIn("number-of-gates", json_data)
        self.assertIn("number-of-multi-qubit-gates", json_data)
        self.assertIn("multi-qubit-gate-depth", json_data)
        self.assertIsNotNone(json_data["number-of-gates"])
        self.assertIsNotNone(json_data["number-of-multi-qubit-gates"])
        self.assertIsNotNone(json_data["multi-qubit-gate-depth"])
        self.assertIsNotNone(json_data.get('transpiled-qasm'))

        r = self.client.post('/qiskit-service/api/v1.0/execute', json=request)
        self.assertEqual(r.status_code, 202)
        print(r.headers.get("Location"))

    def test_transpile_shor_simulator(self):
        # prepare the request
        token = qiskit.IBMQ.stored_account()['token']
        request = {
            'impl-url': "https://raw.githubusercontent.com/PlanQK/qiskit-service/master/test/data/shor_general_qiskit.py",
            'qpu-name': "ibmq_qasm_simulator",
            'input-params': {
                'N': {
                    'rawValue': "9",
                    'type': 'Integer'
                }
            },
            'token': token
        }

        # send the request
        response = self.client.post('/qiskit-service/api/v1.0/transpile',
                                    json=request)

        self.assertEqual(response.status_code, 200)
        json_data = response.get_json()
        self.assertIn("width", json_data)
        self.assertIn("depth", json_data)
        self.assertGreater(json_data['depth'], 3000)
        self.assertEqual(json_data['width'], 18)
        self.assertIn('transpiled-qasm', json_data)
        self.assertIn("number-of-gates", json_data)
        self.assertIn("number-of-multi-qubit-gates", json_data)
        self.assertIn("multi-qubit-gate-depth", json_data)
        self.assertIsNotNone(json_data["number-of-gates"])
        self.assertIsNotNone(json_data["number-of-multi-qubit-gates"])
        self.assertIsNotNone(json_data["multi-qubit-gate-depth"])
        self.assertIsNotNone(json_data.get('transpiled-qasm'))

        r = self.client.post('/qiskit-service/api/v1.0/execute', json=request)
        self.assertEqual(r.status_code, 202)
        print(r.headers.get("Location"))

    def test_transpile_shor_santiago(self):

        # prepare the request
        token = qiskit.IBMQ.stored_account()['token']
        request = {
            'impl-url': "https://raw.githubusercontent.com/PlanQK/qiskit-service/master/test/data/shor_general_qiskit.py",
            'qpu-name': "ibmq_santiago",
            'input-params': {
                'N': {
                    'rawValue': "9",
                    'type': 'Integer'
                }
            },
            'token': token
        }

        # send the request
        response = self.client.post('/qiskit-service/api/v1.0/transpile',
                                    json=request)

        self.assertEqual(response.status_code, 200)
        json_data = response.get_json()
        self.assertIn("error", json_data)
        self.assertIn("too many qubits", json_data['error'])

    def test_transpile_shor_simulator_planqk_url(self):
        # prepare the request
        token = qiskit.IBMQ.stored_account()['token']
        request = {
            'impl-url': "https://platform.planqk.de/qc-catalog/algorithms/e7413acf-c25e-4de8-ab78-75bfc836a839/implementations/1207510f-9007-48b3-93b8-ea51359c0ced/files/1d827208-1976-487e-819b-64df6e990bf3/content",
            'impl-language': 'Qiskit',
            'qpu-name': "ibmq_qasm_simulator",
            'input-params': {},
            'token': token,
            "bearer-token": os.environ["BEARER_TOKEN"]
        }

        # send the request
        response = self.client.post('/qiskit-service/api/v1.0/transpile',
                                    json=request)

        self.assertEqual(response.status_code, 200)
        json_data = response.get_json()
        self.assertIn("width", json_data)
        self.assertIn("depth", json_data)
        self.assertEqual(json_data['depth'], 7)
        self.assertEqual(json_data['width'], 5)
        self.assertIn('transpiled-qasm', json_data)
        self.assertIn("number-of-gates", json_data)
        self.assertIn("number-of-multi-qubit-gates", json_data)
        self.assertIn("multi-qubit-gate-depth", json_data)
        self.assertIsNotNone(json_data["number-of-gates"])
        self.assertIsNotNone(json_data["number-of-multi-qubit-gates"])
        self.assertIsNotNone(json_data["multi-qubit-gate-depth"])
        self.assertIsNotNone(json_data.get('transpiled-qasm'))

        r = self.client.post('/qiskit-service/api/v1.0/execute', json=request)
        self.assertEqual(r.status_code, 202)
        print(r.headers.get("Location"))


if __name__ == "__main__":
    unittest.main()
