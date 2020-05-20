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
from rq import get_current_job
from app.result_model import Result
import logging
import json


def execute(impl_url, input_params, token, qpu_name, shots):
    job = get_current_job()
    result = Result.query.get(job.get_id())
    logging.info('Preparing implementation...')
    circuit = implementation_handler.prepare_code_from_url(impl_url, input_params)

    backend = ibmq_handler.get_qpu(token, qpu_name)
    logging.info('Start transpiling...')
    transpiled_circuit = transpile(circuit, backend=backend)
    print(transpiled_circuit)
    print("Depth: {}".format(transpiled_circuit.depth()))
    print("Width: {}".format(transpiled_circuit.width()))

    logging.info('Start executing...')
    job_result = ibmq_handler.execute_job(transpiled_circuit, shots, backend)
    result.result = json.dumps(job_result)
    result.complete = True
    db.session.commit()

    # ibmq_handler.delete_token()
