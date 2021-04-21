import unittest
import os
from app.config import basedir
from app import app, db
import qiskit
import json
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

        r = self.client.post('/qiskit-service/api/v1.0/execute', json=request)
        self.assertEqual(r.status_code, 202)
        print(r.headers.get("Location"))

    def test_transpile_shor_yorktown_file(self):

        # prepare the request
        token = qiskit.IBMQ.stored_account()['token']
        with open('data/shor-fix-15.py', 'rb') as f:
            impl_data = base64.b64encode(f.read()).decode()
        request = {
            'impl-data': impl_data,
            'impl-language': 'Qiskit',
            'qpu-name': "ibmq_5_yorktown",
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
        self.assertLessEqual(json_data['depth'], 8)
        self.assertEqual(json_data['width'], 3)

        r = self.client.post('/qiskit-service/api/v1.0/execute', json=request)
        self.assertEqual(r.status_code, 202)
        print(r.headers.get("Location"))

    def test_transpile_shor_yorktown_url_qasm(self):

        # prepare the request
        token = qiskit.IBMQ.stored_account()['token']
        request = {
            'impl-url': 'https://quantum-circuit.com/api/get/circuit/KzG7MxH6hpBpM9pCt?format=qasm',
            'impl-language': 'OpenQASM',
            'qpu-name': "ibmq_5_yorktown",
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
        self.assertLessEqual(json_data['depth'], 8)
        self.assertEqual(json_data['width'], 3)
        self.assertIn('transpiled-qasm', json_data)
        self.assertIsNotNone(json_data.get('transpiled-qasm'))

        r = self.client.post('/qiskit-service/api/v1.0/execute', json=request)
        self.assertEqual(r.status_code, 202)
        print(r.headers.get("Location"))

    def test_transpile_shor_yorktown_file_qasm(self):

        # prepare the request
        token = qiskit.IBMQ.stored_account()['token']
        with open('data/shor-fix-15.qasm', 'rb') as f:
            impl_data = base64.b64encode(f.read()).decode()
        request = {
            'impl-data': impl_data,
            'impl-language': 'OpenQASM',
            'qpu-name': "ibmq_5_yorktown",
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
        self.assertLessEqual(json_data['depth'], 8)
        self.assertEqual(json_data['width'], 3)

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

        r = self.client.post('/qiskit-service/api/v1.0/execute', json=request)
        self.assertEqual(r.status_code, 202)
        print(r.headers.get("Location"))

    def test_transpile_shor_ibmq16(self):

        # prepare the request
        token = qiskit.IBMQ.stored_account()['token']
        request = {
            'impl-url': "https://raw.githubusercontent.com/PlanQK/qiskit-service/master/test/data/shor_general_qiskit.py",
            'qpu-name': "ibmq_16_melbourne",
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

if __name__ == "__main__":
    unittest.main()