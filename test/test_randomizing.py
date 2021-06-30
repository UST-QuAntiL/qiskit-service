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

    def test_randomize_full_request(self):

        # prepare the request
        token = qiskit.IBMQ.stored_account()['token']
        request = {
            'qpu-name': 'ibmq_qasm_simulator',
            'number_of_qubits': 1,
            'min_depth_of_circuit': 1,
            'max_depth_of_circuit': 1,
            'number_of_circuits': 1,
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
        self.assertIn("Result benchmark", json_data[0])
        self.assertIn("Result simulator", json_data[0])
        self.assertIn("Result real backend", json_data[0])


    def test_randomize_no_shots_request(self):

        # prepare the request
        token = qiskit.IBMQ.stored_account()['token']
        request = {
            'qpu-name': 'ibmq_qasm_simulator',
            'number_of_qubits': 1,
            'min_depth_of_circuit': 1,
            'max_depth_of_circuit': 1,
            'number_of_circuits': 1,
            'token': token
        }

        # send the request
        response = self.client.post('/qiskit-service/api/v1.0/randomize', json=request)

        self.assertEqual(response.status_code, 200)
        json_data = response.get_json()
        self.assertEqual(1, len(json_data))
        self.assertEqual(3, len(json_data[0]))
        self.assertIn("Result benchmark", json_data[0])
        self.assertIn("Result simulator", json_data[0])
        self.assertIn("Result real backend", json_data[0])


if __name__ == "__main__":
    unittest.main()