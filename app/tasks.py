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
import base64
import datetime
import json
import uuid

from qiskit import transpile, QuantumCircuit, Aer
from qiskit.transpiler.exceptions import TranspilerError
from qiskit.utils.measurement_error_mitigation import get_measured_qubits
from qiskit_aer.noise import NoiseModel
from rq import get_current_job

from app import implementation_handler, aws_handler, ibmq_handler, db, app, ionq_handler, circuit_analysis
from app.NumpyEncoder import NumpyEncoder
from app.benchmark_model import Benchmark
from app.generated_circuit_model import Generated_Circuit
from app.post_processing_result_model import Post_Processing_Result
from app.result_model import Result


def generate(impl_url, impl_data, impl_language, input_params, bearer_token):
    app.logger.info("Starting generate task...")
    job = get_current_job()

    generated_circuit_code = None
    if impl_url:
        generated_circuit_code = implementation_handler.prepare_code_from_url(impl_url, input_params, bearer_token)
    elif impl_data:
        generated_circuit_code = implementation_handler.prepare_code_from_data(impl_data, input_params)
    else:
        generated_circuit_object = Generated_Circuit.query.get(job.get_id())
        generated_circuit_object.generated_circuit = json.dumps({'error': 'generating circuit failed'})
        generated_circuit_object.complete = True
        db.session.commit()

    if generated_circuit_code:
        non_transpiled_depth_old = 0
        generated_circuit_object = Generated_Circuit.query.get(job.get_id())
        generated_circuit_object.generated_circuit = generated_circuit_code.qasm()

        non_transpiled_depth = generated_circuit_code.depth()
        while non_transpiled_depth_old < non_transpiled_depth:
            non_transpiled_depth_old = non_transpiled_depth
            generated_circuit_code = generated_circuit_code.decompose()
            non_transpiled_depth = generated_circuit_code.depth()
        generated_circuit_object.original_depth = non_transpiled_depth
        generated_circuit_object.original_width = circuit_analysis.get_width_of_circuit(generated_circuit_code)
        generated_circuit_object.original_total_number_of_operations = generated_circuit_code.size()
        generated_circuit_object.original_number_of_multi_qubit_gates = generated_circuit_code.num_nonlocal_gates()
        generated_circuit_object.original_number_of_measurement_operations = circuit_analysis.get_number_of_measurement_operations(
            generated_circuit_code)
        generated_circuit_object.original_number_of_single_qubit_gates = generated_circuit_object.original_total_number_of_operations - generated_circuit_object.original_number_of_multi_qubit_gates - generated_circuit_object.original_number_of_measurement_operations
        generated_circuit_object.original_multi_qubit_gate_depth, non_transpiled_circuit = circuit_analysis.get_multi_qubit_gate_depth(
            generated_circuit_code)

        generated_circuit_object.input_params = json.dumps(input_params)
        app.logger.info(f"Received input params for circuit generation: {generated_circuit_object.input_params}")
        generated_circuit_object.complete = True
        db.session.commit()


def execute(correlation_id, provider, impl_url, impl_data, impl_language, transpiled_qasm, input_params, token,
            access_key_aws, secret_access_key_aws, qpu_name, optimization_level, noise_model, only_measurement_errors,
            shots, bearer_token, qasm_string, **kwargs):
    """Create database entry for result. Get implementation code, prepare it, and execute it. Save result in db"""
    app.logger.info("Starting execute task...")
    job = get_current_job()

    if provider == 'ibmq':
        backend = ibmq_handler.get_qpu(token, qpu_name, **kwargs)
    elif provider == 'ionq':
        backend = ionq_handler.get_qpu(token, qpu_name)
    elif provider == 'aws':
        backend = aws_handler.get_qpu(access_key=access_key_aws, secret_access_key=secret_access_key_aws,
                                      qpu_name=qpu_name, **kwargs)
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
            circuits = [implementation_handler.prepare_code_from_qasm(qasm) for qasm in qasm_string]
        elif impl_url and not correlation_id:
            if impl_language.lower() == 'openqasm':
                # list of circuits
                circuits = [implementation_handler.prepare_code_from_qasm_url(url, bearer_token) for url in impl_url]
            else:
                circuits = [implementation_handler.prepare_code_from_url(url, input_params, bearer_token) for url in
                            impl_url]
        elif impl_data and not correlation_id:
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

        if noise_model and provider == 'ibmq':
            noisy_qpu = ibmq_handler.get_qpu(token, noise_model, **kwargs)
            noise_model = NoiseModel.from_backend(noisy_qpu)
            properties = noisy_qpu.properties()
            configuration = noisy_qpu.configuration()
            coupling_map = configuration.coupling_map
            basis_gates = noise_model.basis_gates
            try:
                transpiled_circuits = transpile(circuits, noisy_qpu)
            except TranspilerError:
                result = Result.query.get(job.get_id())
                result.result = json.dumps({'error': 'too many qubits required'})
                result.complete = True
                db.session.commit()
            measurement_qubits = get_measurement_qubits_from_transpiled_circuit(transpiled_circuits)

            if only_measurement_errors:
                ro_noise_model = NoiseModel()
                for k, v in noise_model._local_readout_errors.items():
                    ro_noise_model.add_readout_error(v, k)
                noise_model = ro_noise_model

            backend = Aer.get_backend('aer_simulator')

        else:
            try:
                transpiled_circuits = transpile(circuits, backend=backend, optimization_level=optimization_level)
            except TranspilerError:
                result = Result.query.get(job.get_id())
                result.result = json.dumps({'error': 'too many qubits required'})
                result.complete = True
                db.session.commit()

    app.logger.info('Start executing...')
    if provider == 'aws' and not noise_model:
        # Note: AWS cannot handle such a noise model
        job_result = aws_handler.execute_job(transpiled_circuits, shots, backend)
    elif provider == 'ionq' and not noise_model:
        job_result = ionq_handler.execute_job(transpiled_circuits, shots, backend)
    else:
        # If we need a noise model, we have to use IBM Q
        job_result = ibmq_handler.execute_job(transpiled_circuits, shots, backend, noise_model)

    if job_result:
        result = Result.query.get(job.get_id())
        result.result = json.dumps(job_result['counts'])
        result.complete = True
        db.session.commit()

        # implementation contains post processing of execution results that has to be executed
        if correlation_id and (impl_url or impl_data):
            # TODO create new post processing result object
            post_processing_result = Post_Processing_Result(id=str(uuid.uuid4()))
            # prepare input data containing execution results and initial input params for generating the circuit
            generated_circuit = Generated_Circuit.query.get(correlation_id)
            input_params_for_post_processing = generated_circuit.input_params
            input_params_for_post_processing['counts'] = json.dumps(job_result['counts'])

            if impl_url:
                result = implementation_handler.prepare_code_from_url(impl_url,
                                                                      input_params=input_params_for_post_processing,
                                                                      bearer_token=bearer_token, post_processing=True)
            elif impl_data:
                result = implementation_handler.prepare_post_processing_code_from_data(data=impl_data,
                                                                                       input_params=input_params_for_post_processing)  # TODO save result in postprocessing result object

    else:
        result = Result.query.get(job.get_id())
        result.result = json.dumps({'error': 'execution failed'})
        result.complete = True
        db.session.commit()


def get_measurement_qubits_from_transpiled_circuit(transpiled_circuit):
    qubit_index, qubit_mappings = get_measured_qubits([transpiled_circuit])
    measurement_qubits = [int(i) for i in list(qubit_mappings.keys())[0].split("_")]

    return measurement_qubits


def convert_into_suitable_format(object):
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
    job_result = ibmq_handler.execute_job(transpiled_circuit, shots, backend, None)
    if job_result:
        # once the job is finished save results in db
        result = Result.query.get(job.get_id())
        result.result = json.dumps(job_result, default=convert_into_suitable_format)
        result.complete = True

        benchmark = Benchmark.query.get(job.get_id())
        benchmark.result = json.dumps(job_result, default=convert_into_suitable_format)
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
