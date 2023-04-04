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

import json
import unittest
import os
from app.config import basedir
from app import app, db
from app.benchmark_model import Benchmark


class BenchmarksTestCase(unittest.TestCase):

    def setUp(self):

        # setup environment variables for testing
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///" + os.path.join(basedir, 'test.db')

        self.client = app.test_client()
        db.create_all()
        print(f"tables: {list(db.metadata.tables.keys())}")

        self.create_dummy_results()

    @classmethod
    def create_dummy_results(cls):

        # Create incomplete dummy result
        b1 = Benchmark(id="0")
        b2 = Benchmark(id="1")
        db.session.add(b1)
        db.session.add(b2)
        b1.backend = 'ibmq_qasm_simulator'
        b1.benchmark_id = 0
        b2.backend = 'ibmq_athens'
        b2.benchmark_id = 0
        db.session.commit()

        # Create complete dummy result
        b1 = Benchmark(id="2")
        b2 = Benchmark(id="3")
        b3 = Benchmark(id="4")
        db.session.add(b1)
        db.session.add(b2)
        db.session.add(b3)
        b1.shots = 1024
        b1.backend = 'ibmq_qasm_simulator'
        b1.original_depth = 1
        b1.original_width = 1
        b1.original_number_of_multi_qubit_gates = 1
        b1.transpiled_depth = 10
        b1.transpiled_width = 1
        b1.transpiled_number_of_multi_qubit_gates = 1
        b1.benchmark_id = 1
        b1.result = """{"text" : "I am complete !"}"""
        b1.counts = """{"00000": 1024}"""
        b1.complete = True
        b2.shots = 1024
        b2.backend = 'ibmq_athens'
        b2.original_depth = 1
        b2.original_width = 1
        b2.original_number_of_multi_qubit_gates = 1
        b2.transpiled_depth = 10
        b2.transpiled_width = 1
        b2.transpiled_number_of_multi_qubit_gates = 1
        b2.benchmark_id = 1
        b2.result = """{"text" : "I am complete !"}"""
        b2.counts = """{"10000": 1024}"""
        b2.complete = True
        b3.shots = 1024
        b3.backend = 'ibmq_lima'
        b3.original_depth = 1
        b3.original_width = 1
        b3.original_number_of_multi_qubit_gates = 1
        b3.transpiled_depth = 1
        b3.transpiled_width = 1
        b3.transpiled_number_of_multi_qubit_gates = 1
        b3.benchmark_id = 2
        b3.result = """{"text" : "I am complete !"}"""
        b3.counts = """{"00000": 1024}"""
        b3.clifford = True
        b3.complete = True
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_version(self):

        response = self.client.get('/qiskit-service/api/v1.0/version')

        self.assertEqual(response.status_code, 200)
        json_data = response.get_json()
        self.assertTrue("version" in json_data)
        self.assertEqual(json_data['version'], "1.0")

    def test_calc_wd(self):
        response_athens = self.client.get('/qiskit-service/api/v1.0/calc-wd/ibmq_athens')
        self.assertEqual(response_athens.status_code, 200)
        solution_athens = response_athens.get_json()

        response_lima = self.client.get('/qiskit-service/api/v1.0/calc-wd/ibmq_lima')
        self.assertEqual(response_lima.status_code, 200)
        solution_lima = response_lima.get_json()

        self.assertEqual('0', solution_athens[0]['wd'])
        self.assertGreater(int(solution_lima[0]['wd']), 0)

    def test_get_result_incomplete(self):

        benchmark_id = "0"
        response = self.client.get('/qiskit-service/api/v1.0/benchmarks/%s' % benchmark_id)
        self.assertEqual(response.status_code, 200)
        benchmark = response.get_json()
        benchmarking_results = benchmark['benchmarking-results']
        self.assertIn("complete", benchmarking_results[0])
        self.assertEqual(False, benchmarking_results[0]['complete'])
        self.assertIn("complete", benchmarking_results[1])
        self.assertEqual(False, benchmarking_results[1]['complete'])
        self.assertEqual(False, benchmark['benchmarking-complete'])

    def test_get_result_complete(self):

        benchmark_id = "1"
        response = self.client.get('/qiskit-service/api/v1.0/benchmarks/%s' % benchmark_id)
        self.assertEqual(response.status_code, 200)
        benchmark = response.get_json()
        benchmarking_results = benchmark['benchmarking-results']
        self.assertIn("complete", benchmarking_results[0])
        self.assertIn("complete", benchmarking_results[1])
        self.assertEqual("ibmq_qasm_simulator", benchmarking_results[0]['backend'])
        self.assertEqual(1, benchmarking_results[0]['benchmark-id'])
        self.assertEqual({"00000": 1024}, benchmarking_results[0]['counts'])
        self.assertEqual(1, benchmarking_results[0]['original-depth'])
        self.assertEqual(1, benchmarking_results[0]['original-width'])
        self.assertEqual(1, benchmarking_results[0]['original-number-of-multi-qubit-gates'])
        self.assertEqual(10, benchmarking_results[0]['transpiled-depth'])
        self.assertEqual(1, benchmarking_results[0]['transpiled-width'])
        self.assertEqual(1, benchmarking_results[0]['transpiled-number-of-multi-qubit-gates'])
        self.assertEqual(1024, benchmarking_results[0]['shots'])
        self.assertEqual(True, benchmarking_results[0]['complete'])

        self.assertEqual(1, benchmarking_results[1]['benchmark-id'])
        self.assertEqual({"10000": 1024}, benchmarking_results[1]['counts'])
        self.assertEqual(1, benchmarking_results[1]['original-depth'])
        self.assertEqual(1, benchmarking_results[1]['original-width'])
        self.assertEqual(1, benchmarking_results[1]['original-number-of-multi-qubit-gates'])
        self.assertEqual(10, benchmarking_results[1]['transpiled-depth'])
        self.assertEqual(1, benchmarking_results[1]['transpiled-width'])
        self.assertEqual(1, benchmarking_results[1]['transpiled-number-of-multi-qubit-gates'])
        self.assertEqual(1024, benchmarking_results[1]['shots'])
        self.assertEqual(True, benchmarking_results[1]['complete'])


if __name__ == "__main__":
    unittest.main()
