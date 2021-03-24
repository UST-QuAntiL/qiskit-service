from flask import request, abort, jsonify
from qiskit import IBMQ, assemble, transpile
from qiskit.circuit.random import random_circuit
from qiskit.providers.jobstatus import JOB_FINAL_STATES
from qiskit.providers import JobError

from app import app, db
from app.result_model import Result


def run(qasm, backend, token):
    # job_status = job.status()
    # while job_status not in JOB_FINAL_STATES:
     #   print("The job is still running")
     #   job_status = job.status()

    # try:
     #   job_result = job.result()
     #   print("The job finished with result {}".format(job_result))
     #   print(job_result)
     #   print("\n")
     #   print(job_result.get_counts())
    # except JobError as ex:
     #   print("Something wrong happened!: {}".format(ex))

    job = app.execute_queue.enqueue('app.tasks.execute', transpiled_qasm=qasm, qpu_name=backend, token=token, shot=1024)

    result = Result(id=job.get_id())
    db.session.add(result)
    db.session.commit()

    content_location = 'qiskit-service/api/v1.0/results/' + result.id
    response = jsonify({'Location': content_location})
    response.status_code = 202
    response.headers['Location'] = content_location
    return response


#IBMQ.load_account()


@app.route('/qiskit-service/api/v1.0/randomize', methods=['POST'])
def randomize_circuits():
    if not request.json:
        abort(400)

    provider = IBMQ.get_provider(group='open')
    backend_sim = provider.get_backend('ibmq_qasm_simulator')

    backend_real = request.json('qpu-name')
    num_of_qubits = request.json('number_of_qubits')
    depth_of_circuit = request.json('depth_of_circuit')
    num_of_circuits = request.json('num_of_circuits')
    token = request.json('token')


    for i in range(num_of_circuits):
        qx = random_circuit(num_qubits=num_of_qubits, depth=depth_of_circuit, measure=True)
        qcircuit_sim = transpile(qx, backend=backend_sim)
        # qobj_sim = assemble(qcircuit_sim, backend=backend_sim)
        qcircuit_real = transpile(qx, backend=backend_real)
        # obj_real = assemble(qcircuit_real, backend=backend_real)
        print("Depth of circuit:")
        print(qcircuit_real.depth())
        print("\n")
        print("Width of circuit:")
        print(qcircuit_real.num_qubits)

        location_sim = run(qasm=qcircuit_sim.qasm(), backend=backend_sim, token=token)
        location_real = run(qasm=qcircuit_real.qasm(), backend=backend_real, token=token)

        locations = 'Result simulator: ' + location_sim + '\nResult real backend: ' + location_real
        return locations
        # job_sim = app.execute_queue.enqueue('app.tasks.execute', transpiled_qasm=qcircuit_sim.qasm(), qpu_name=backend_sim, token=token, shots=1024)
        # run(job_sim)
        #     #run(job_real)
