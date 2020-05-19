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

from qiskit import IBMQ, assemble, QiskitError
from qiskit.providers.jobstatus import JOB_FINAL_STATES
from qiskit.providers import JobError
import json


def get_qpu(token, qpu_name):
    IBMQ.save_account(token, overwrite=True)
    IBMQ.load_account()
    provider = IBMQ.get_provider(group='open')
    backend = provider.get_backend(qpu_name)
    return backend


def delete_token(token):
    IBMQ.delete_account()


def get_qObject_in_json(transpiled_circuit, qpu_name, shots):
    qobj = assemble(transpiled_circuit, shots=shots)
    qobj_dict = qobj.to_dict()
    data_dict = {'qObject': qobj_dict, 'backend': {'name': qpu_name}}
    data = json.dumps(data_dict)
    return data


def execute_job(transpiled_circuit, shots, backend):
    qobj = assemble(transpiled_circuit, shots=shots)

    job = backend.run(qobj)

    job_status = job.status()
    while job_status not in JOB_FINAL_STATES:
        print("The job is still running")
        job_status = job.status()

    try:
        job_result = job.result() # It will block until the job finishes.
        print("\nJob result:")
        print(job_result)
        try:
            print("\nState vector:")
            print(job_result.get_statevector())
        except QiskitError:
            print("No statevector available!")
        try:
            print("\nCounts:")
            print(job_result.get_counts())
        except QiskitError:
            print("No counts available!")
        try:
            print("\nUnitary:")
            print(job_result.get_unitary())
        except QiskitError:
            print("No unitary available!")
    except JobError as ex:
        print("Something wrong happened with the result!: {}".format(ex))
