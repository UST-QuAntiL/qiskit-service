import unittest
import os
from app.config import basedir
from app import app, db
import qiskit
import json


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

    def test_transpile_hadamard_simulator(self):

        # prepare the request
        token = qiskit.IBMQ.stored_account()['token']
        request = {
            'impl-url': "https://raw.githubusercontent.com/PlanQK/qiskit-service/feature/parameter-type/test/data/hadamard.py",
            'qpu-name': "ibmq_qasm_simulator",
            'input-params': {},
            'token': token
        }

        # send the request
        response = self.client.post('/qiskit-service/api/v1.0/transpile',
                                    data=json.dumps(request),
                                    content_type="application/json")

        self.assertEqual(response.status_code, 200)
        json_data = response.get_json()
        self.assertIn("width", json_data)
        self.assertIn("depth", json_data)
        self.assertEqual(json_data['depth'], 2)
        self.assertEqual(json_data['width'], 1)

    def test_transpile_shor_simulator(self):
        # prepare the request
        token = qiskit.IBMQ.stored_account()['token']
        request = {
            'impl-url': "https://raw.githubusercontent.com/PlanQK/qiskit-service/feature/parameter-type/test/data/shor_general_qiskit.py",
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
                                    data=json.dumps(request),
                                    content_type="application/json")

        self.assertEqual(response.status_code, 200)
        json_data = response.get_json()
        self.assertIn("width", json_data)
        self.assertIn("depth", json_data)
        self.assertEqual(json_data['depth'], 15829)
        self.assertEqual(json_data['width'], 18)

    def test_transpile_shor_ibmq16(self):

        # prepare the request
        token = qiskit.IBMQ.stored_account()['token']
        request = {
            'impl-url': "https://raw.githubusercontent.com/PlanQK/qiskit-service/feature/parameter-type/test/data/shor_general_qiskit.py",
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
                                    data=json.dumps(request),
                                    content_type="application/json")

        self.assertEqual(response.status_code, 200)
        json_data = response.get_json()
        self.assertIn("error", json_data)
        self.assertIn("too many qubits", json_data['error'])

if __name__ == "__main__":
    unittest.main()