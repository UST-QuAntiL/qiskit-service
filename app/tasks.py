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
from qiskit import transpile
from qiskit.transpiler.exceptions import TranspilerError
from rq import get_current_job
from app.result_model import Result
import logging
import json


def execute(impl_url, input_params, token, qpu_name, shots):
    """Create database entry for result. Get implementation code, prepare it, and execute it. Save result in db"""
    job = get_current_job()

    logging.info('Preparing implementation...')
    print(input_params)
    circuit = implementation_handler.prepare_code_from_url(impl_url, input_params)
    if circuit:
        backend = ibmq_handler.get_qpu(token, qpu_name)
        if backend:
            logging.info('Start transpiling...')
            try:
                transpiled_circuit = transpile(circuit, backend=backend, optimization_level=1)
                print("Circuit Depth: {}".format(transpiled_circuit.depth()))
                print("Circuit Width: {}".format(transpiled_circuit.num_qubits))

                logging.info('Start executing...')
                job_result = ibmq_handler.execute_job(transpiled_circuit, shots, backend)
                if job_result:
                    result = Result.query.get(job.get_id())
                    result.result = json.dumps(job_result)
                    result.complete = True
                    db.session.commit()
                else:
                    result = Result.query.get(job.get_id())
                    result.result = json.dumps({'error': 'execution failed'})
                    result.complete = True
                    db.session.commit()
            except TranspilerError:
                result = Result.query.get(job.get_id())
                result.result = json.dumps({'error': 'too many qubits required'})
                result.complete = True
                db.session.commit()
        else:
            result = Result.query.get(job.get_id())
            result.result = json.dumps({'error': 'qpu-name or token wrong'})
            result.complete = True
            db.session.commit()
    else:
        result = Result.query.get(job.get_id())
        result.result = json.dumps({'error': 'URL not found'})
        result.complete = True
        db.session.commit()

    # ibmq_handler.delete_token()


def calculate_calibration_matrix(token, qpu_name, shots):
    """Calculate the current calibration matrix for the given QPU and save the result in db"""
    job = get_current_job()

    backend = ibmq_handler.get_qpu(token, qpu_name)
    if backend:
        job_result = ibmq_handler.calculate_calibration_matrix(token, qpu_name, shots)
        if job_result:
            result = Result.query.get(job.get_id())
            result.result = json.dumps(job_result)
            result.complete = True
            db.session.commit()
    else:
        result = Result.query.get(job.get_id())
        result.result = json.dumps({'error': 'qpu-name or token wrong'})
        result.complete = True
        db.session.commit()
