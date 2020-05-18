from qiskit import IBMQ, assemble
from qiskit.providers.jobstatus import JobStatus
from qiskit.providers.ibmq.job import IBMQJobApiError, IBMQJobError
from qiskit.providers import JobError
import json
import asyncio

from qiskit.providers.ibmq.api.rest import job, backend



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

async def run_job(transpiled_circuit, shots):
    qobj = assemble(transpiled_circuit, shots=shots)
    job = backend.run(qobj)

    try:
        job_status = job.status()
        if job_status is JobStatus.RUNNING:
            print("The job is still running")
    except IBMQJobApiError as ex:
        print("Something wrong happend!: {}".format(ex))

    try:
        job_result = job.result()  # It will block until the job finishes.
        print("The job finished with result {}".format(job_result))
    except JobError as ex:
        print("Something wrong happened!: {}".format(ex))