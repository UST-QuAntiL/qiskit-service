from flask import request, abort, jsonify
from qiskit import IBMQ, assemble, transpile
from qiskit.circuit.random import random_circuit
from qiskit.providers.jobstatus import JOB_FINAL_STATES
from qiskit.providers import JobError

from app import app, db, parameters, ibmq_handler
from app.benchmark_model import Benchmark
from app.result_model import Result


def run(circuit, backend, token, original_depth, original_width, transpiled_depth, transpiled_width):
    qasm = circuit.qasm()
    job = app.execute_queue.enqueue('app.tasks.execute_benchmark', transpiled_qasm=qasm, qpu_name=backend, token=token,
                                    shots=1024)

    result = Result(id=job.get_id())
    benchmark = Benchmark(id=job.get_id())
    db.session.add(result)
    db.session.add(benchmark)
    benchmark.original_depth = original_depth
    benchmark.original_width = original_width
    benchmark.transpiled_depth = transpiled_depth
    benchmark.transpiled_width = transpiled_width
    #benchmark.benchmark_id = benchmark_id
    db.session.commit()

    content_location = 'qiskit-service/api/v1.0/results/' + result.id
    # response = jsonify({'Location': content_location})
    # response.status_code = 202
    # response.headers['Location'] = content_location
    return content_location


def randomize(qpu_name, num_of_qubits, depth_of_circuit, num_of_circuits, token):
    sim_name = 'ibmq_qasm_simulator'
    backend_sim = ibmq_handler.get_qpu(token, sim_name)
    backend_real = ibmq_handler.get_qpu(token, qpu_name)
    locations = ''

    for i in range(1, depth_of_circuit + 1):
        for j in range(num_of_circuits):
            qx = random_circuit(num_qubits=num_of_qubits, depth=i, measure=True)
            qcircuit_sim = transpile(qx, backend=backend_sim)
            qcircuit_real = transpile(qx, backend=backend_real)
            transpiled_depth_sim = qcircuit_sim.depth()
            transpiled_width_sim = qcircuit_sim.num_qubits
            transpiled_depth_real = qcircuit_real.depth()
            transpiled_width_real = qcircuit_real.num_qubits
            #benchmark_id = benchmark_id + 1

            location_sim = run(circuit=qcircuit_sim, backend=sim_name, token=token, original_depth=i,
                               original_width=num_of_qubits, transpiled_depth=transpiled_depth_sim,
                               transpiled_width=transpiled_width_sim)
            location_real = run(circuit=qcircuit_real, backend=qpu_name, token=token, original_depth=i,
                                original_width=num_of_qubits, transpiled_depth=transpiled_depth_real,
                                transpiled_width=transpiled_width_real)

            locations = locations + 'Result simulator: ' + location_sim + '\nResult real backend: ' + location_real + '\n'

    return locations
