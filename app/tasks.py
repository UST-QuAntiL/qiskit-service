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

from app import implementation_handler, ibmq_handler, db
from qiskit import transpile, QuantumCircuit
from qiskit.transpiler.exceptions import TranspilerError
from rq import get_current_job

from app.NumpyEncoder import NumpyEncoder
from app.benchmark_model import Benchmark
from app.result_model import Result
import logging
import json
import base64


def execute(impl_url, impl_data, impl_language, transpiled_qasm, input_params, token, qpu_name, shots):
    """Create database entry for result. Get implementation code, prepare it, and execute it. Save result in db"""
    job = get_current_job()

    backend = ibmq_handler.get_qpu(token, qpu_name)
    if not backend:
        result = Result.query.get(job.get_id())
        result.result = json.dumps({'error': 'qpu-name or token wrong'})
        result.complete = True
        db.session.commit()

    logging.info('Preparing implementation...')
    if transpiled_qasm:
        transpiled_circuit = QuantumCircuit.from_qasm_str(transpiled_qasm)
    else:
        if impl_url:
            if impl_language.lower() == 'openqasm':
                circuit = implementation_handler.prepare_code_from_qasm_url(impl_url)
            else:
                circuit = implementation_handler.prepare_code_from_url(impl_url, input_params)
        elif impl_data:
            impl_data = base64.b64decode(impl_data.encode()).decode()
            if impl_language.lower() == 'openqasm':
                circuit = implementation_handler.prepare_code_from_qasm(impl_data)
            else:
                circuit = implementation_handler.prepare_code_from_data(impl_data, input_params)
        if not circuit:
            result = Result.query.get(job.get_id())
            result.result = json.dumps({'error': 'URL not found'})
            result.complete = True
            db.session.commit()
        logging.info('Start transpiling...')
        try:
            transpiled_circuit = transpile(circuit, backend=backend, optimization_level=3)
        except TranspilerError:
            result = Result.query.get(job.get_id())
            result.result = json.dumps({'error': 'too many qubits required'})
            result.complete = True
            db.session.commit()

    logging.info('Start executing...')
    job_result = ibmq_handler.execute_job(transpiled_circuit, shots, backend)
    if job_result:
        result = Result.query.get(job.get_id())
        result.result = json.dumps(job_result)
        result.complete = True

        benchmark = Benchmark.query.get(job.get_id())
        benchmark.backend = json.dumps(qpu_name)
        benchmark.result = json.dumps(job_result)
        benchmark.counts = json.dumps(job_result['counts'])
        benchmark.complete = True

        db.session.commit()
    else:
        result = Result.query.get(job.get_id())
        result.result = json.dumps({'error': 'execution failed'})
        result.complete = True
        db.session.commit()

    # ibmq_handler.delete_token()


def execute_benchmark(transpiled_qasm, token, qpu_name, shots):
    """Create database entry for result. Get implementation code, prepare it, and execute it. Save result in db"""
    job = get_current_job()

    backend = ibmq_handler.get_qpu(token, qpu_name)
    if not backend:
        result = Result.query.get(job.get_id())
        result.result = json.dumps({'error': 'qpu-name or token wrong'})
        result.complete = True
        db.session.commit()

    logging.info('Preparing implementation...')
    transpiled_circuit = QuantumCircuit.from_qasm_str(transpiled_qasm)

    logging.info('Start executing...')
    job_result = ibmq_handler.execute_job(transpiled_circuit, shots, backend)
    if job_result:
        result = Result.query.get(job.get_id())
        result.result = json.dumps(job_result)
        result.complete = True

        benchmark = Benchmark.query.get(job.get_id())
        benchmark.backend = json.dumps(qpu_name)
        benchmark.result = json.dumps(job_result)
        benchmark.counts = json.dumps(job_result['counts'])
        benchmark.complete = True

        db.session.commit()
    else:
        result = Result.query.get(job.get_id())
        result.result = json.dumps({'error': 'execution failed'})
        result.complete = True

        benchmark = Benchmark.query.get(job.get_id())
        benchmark.complete = True

        db.session.commit()

    # ibmq_handler.delete_token()


def calculate_calibration_matrix(token, qpu_name, shots):
    """Calculate the current calibration matrix for the given QPU and save the result in db"""
    job = get_current_job()

    backend = ibmq_handler.get_qpu(token, qpu_name)
    if backend:
        job_result = ibmq_handler.get_meas_fitter(token, qpu_name, shots)
        if job_result:
            result = Result.query.get(job.get_id())
            result.result = json.dumps({'matrix': job_result.cal_matrix}, cls=NumpyEncoder)
            result.complete = True
            db.session.commit()
        else:
            result = Result.query.get(job.get_id())
            result.result = json.dumps({'error': 'matrix calculation failed'})
            result.complete = True
            db.session.commit()
    else:
        result = Result.query.get(job.get_id())
        result.result = json.dumps({'error': 'qpu-name or token wrong'})
        result.complete = True
        db.session.commit()
