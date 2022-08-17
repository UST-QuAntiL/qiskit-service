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
import datetime

from app import implementation_handler, ibmq_handler, db, app
from qiskit import transpile, QuantumCircuit
from qiskit.transpiler.exceptions import TranspilerError
from rq import get_current_job
from qiskit.providers.ibmq.managed import IBMQJobManager

from app.NumpyEncoder import NumpyEncoder
from app.benchmark_model import Benchmark
from app.result_model import Result
import json
import base64



def execute(impl_url, impl_data, impl_language, transpiled_qasm, input_params, token, qpu_name, optimization_level, shots, bearer_token, qasm_string, **kwargs):
    """Create database entry for result. Get implementation code, prepare it, and execute it. Save result in db"""
    app.logger.info("Starting execute task...")
    job = get_current_job()

    backend = ibmq_handler.get_qpu(token, qpu_name, **kwargs)
    if not backend:
        result = Result.query.get(job.get_id())
        result.result = json.dumps({'error': 'qpu-name or token wrong'})
        result.complete = True
        db.session.commit()

    app.logger.info('Preparing implementation...')
    if transpiled_qasm:
        transpiled_circuits = [QuantumCircuit.from_qasm_str(qasm) for qasm in transpiled_qasm]
    else:
        if qasm_string:
            circuits = implementation_handler.prepare_code_from_qasm(qasm_string)
        elif impl_url:
            if impl_language.lower() == 'openqasm':
                # list of circuits
                circuits = [implementation_handler.prepare_code_from_qasm_url(url, bearer_token) for url in impl_url]
            else:
                circuits = [implementation_handler.prepare_code_from_url(url, input_params, bearer_token) for url in impl_url]
        elif impl_data:
            impl_data = [base64.b64decode(data.encode()).decode() for data in impl_data]
            if impl_language.lower() == 'openqasm':
                circuits = [implementation_handler.prepare_code_from_qasm(data) for data in impl_data]
            else:
                circuits = [implementation_handler.prepare_code_from_data(data, input_params) for data in impl_data]
        if not circuits:
            result = Result.query.get(job.get_id())
            result.result = json.dumps({'error': 'URL not found'})
            result.complete = True
            db.session.commit()
        app.logger.info('Start transpiling...')
        try:
            transpiled_circuits = transpile(circuits, backend=backend, optimization_level=optimization_level)
        except TranspilerError:
            result = Result.query.get(job.get_id())
            result.result = json.dumps({'error': 'too many qubits required'})
            result.complete = True
            db.session.commit()

    app.logger.info('Start executing...')
    job_manager = IBMQJobManager()
    job_result = job_manager.run(transpiled_circuits, backend=backend)
    # job_result = ibmq_handler.execute_job(transpiled_circuit, shots, backend)
    if job_result:
        result = Result.query.get(job.get_id())
        result_counts = []
        for i, circ in enumerate(transpiled_circuits):
            result_counts.append(job_result.results().get_counts(i))
        if len(result_counts) == 1:
            result_counts = result_counts[0]
        result.result = json.dumps(result_counts)
        result.complete = True
        db.session.commit()
    else:
        result = Result.query.get(job.get_id())
        result.result = json.dumps({'error': 'execution failed'})
        result.complete = True
        db.session.commit()

    # ibmq_handler.delete_token()


def convertInSuitableFormat(object):
    """Enables the serialization of the unserializable datetime.datetime format"""
    if isinstance(object, datetime.datetime):
        return object.__str__()


def execute_benchmark(transpiled_qasm, token, qpu_name, shots):
    """Create database entry for result and benchmark. Get implementation code, prepare it, and execute it. Save
    result in db """
    job = get_current_job()

    backend = ibmq_handler.get_qpu(token, qpu_name)
    if not backend:
        result = Result.query.get(job.get_id())
        result.result = json.dumps({'error': 'qpu-name or token wrong'})
        result.complete = True
        db.session.commit()

    app.logger.info('Preparing implementation...')
    transpiled_circuit = QuantumCircuit.from_qasm_str(transpiled_qasm)

    app.logger.info('Start executing...')
    job_result = ibmq_handler.execute_job(transpiled_circuit, shots, backend)
    if job_result:
        # once the job is finished save results in db
        result = Result.query.get(job.get_id())
        result.result = json.dumps(job_result, default=convertInSuitableFormat)
        result.complete = True

        benchmark = Benchmark.query.get(job.get_id())
        benchmark.result = json.dumps(job_result, default=convertInSuitableFormat)
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
