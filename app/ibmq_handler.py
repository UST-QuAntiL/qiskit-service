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
import time
import qiskit
from qiskit import IBMQ, assemble, QiskitError
from qiskit.ignis.mitigation import CompleteMeasFitter, complete_meas_cal
from qiskit.providers.jobstatus import JOB_FINAL_STATES
from qiskit.providers.exceptions import JobError, JobTimeoutError
from qiskit.providers.exceptions import QiskitBackendNotFoundError
from qiskit.providers.ibmq.api.exceptions import RequestsApiError


def get_qpu(token, qpu_name):
    """Load account from token. Get backend."""
    try:
        IBMQ.save_account(token, overwrite=True)
        IBMQ.load_account()
        provider = IBMQ.get_provider(group='open')
        backend = provider.get_backend(qpu_name)
        return backend
    except (QiskitBackendNotFoundError, RequestsApiError):
        return None


def delete_token():
    """Delete account."""
    IBMQ.delete_account()


def execute_job(transpiled_circuit, shots, backend):
    """Genereate qObject from transpiled circuit and execute it. Return result."""

    try:
        qobj = assemble(transpiled_circuit, shots=shots)
        job = backend.run(qobj)

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
    except (JobError, JobTimeoutError):
        return None


def calculate_calibration_matrix(token, qpu_name, shots):
    """Execute the calibration circuits on the given backend and calculate resulting matrix."""
    print("Starting calculation of calibration matrix for QPU: ", qpu_name)

    backend = get_qpu(token, qpu_name)

    # Generate a calibration circuit for each state
    qr = qiskit.QuantumRegister(len(backend.properties().qubits))
    meas_calibs, state_labels = complete_meas_cal(qr=qr, circlabel='mcal')

    # Execute each calibration circuit and store results
    print('Executing ' + str(len(meas_calibs)) + ' circuits to create calibration matrix...')
    cal_results = []
    for circuit in meas_calibs:
        print('Executing circuit ' + circuit.name)
        cal_results.append(execute_calibration_circuit(circuit, shots, backend))

    # Generate calibration matrix out of measurement results
    meas_fitter = CompleteMeasFitter(cal_results, state_labels, circlabel='mcal')
    return meas_fitter.filter


def execute_calibration_circuit(circuit, shots, backend):
    """Execute a calibration circuit on the specified backend"""
    job = qiskit.execute(circuit, backend=backend, shots=shots)

    job_status = job.status()
    while job_status not in JOB_FINAL_STATES:
        print('The execution is still running')
        time.sleep(20)
        job_status = job.status()
    return job.result()
