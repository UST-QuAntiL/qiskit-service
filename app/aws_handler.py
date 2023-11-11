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
from qiskit_braket_provider import AWSBraketProvider
from braket.aws.aws_session import AwsSession
import boto3
from qiskit.providers.jobstatus import JOB_FINAL_STATES
from qiskit import QiskitError


def get_qpu(access_key, secret_access_key, qpu_name):
    boto_session = boto3.Session(
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_access_key
    )
    session = AwsSession(boto_session)
    provider = AWSBraketProvider()
    backend = provider.get_backend(qpu_name, aws_session=session)
    return backend


def execute_job(transpiled_circuit, shots, backend):
    """Generate qObject from transpiled circuit and execute it. Return result."""

    try:
        job = backend.run(transpiled_circuit, shots=shots)

        job_status = job.status()
        while job_status not in JOB_FINAL_STATES:
            print("The job is still running")
            job_status = job.status()

        job_result = job.result()
        print("\nJob result:")
        print(job_result)
        job_result_dict = job_result.to_dict()
        print(job_result_dict)

        try:
            statevector = job_result.get_statevector()
            print("\nState vector:")
            print(statevector)
        except QiskitError:
            statevector = None
            print("No statevector available!")
        try:
            counts = job_result.get_counts()
            print("\nCounts:")
            print(counts)
        except QiskitError:
            counts = None
            print("No counts available!")
        try:
            unitary = job_result.get_unitary()
            print("\nUnitary:")
            print(unitary)
        except QiskitError:
            unitary = None
            print("No unitary available!")
        return {'job_result_raw': job_result_dict, 'statevector': statevector, 'counts': counts, 'unitary': unitary}
    except Exception:
        return None
