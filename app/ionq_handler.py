# ******************************************************************************
#  Copyright (c) 2023 University of Stuttgart
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
from qiskit import QiskitError
from qiskit.providers.jobstatus import JOB_FINAL_STATES
from qiskit_ionq import IonQProvider


def get_qpu(token, qpu_name):
    provider = IonQProvider(token)
    if "simulator" not in qpu_name:
        qpu_name = qpu_name.replace(" ", "-").lower()
        ionq_signature = "ionq_qpu."
        qpu_name = ionq_signature + qpu_name
    return provider.get_backend(qpu_name)


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
