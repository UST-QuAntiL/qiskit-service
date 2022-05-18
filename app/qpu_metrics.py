from datetime import datetime
from hashlib import sha256
from typing import List
from uuid import UUID

from qiskit.providers.ibmq import IBMQ, IBMQBackend
from marshmallow import Schema, fields
from qiskit.providers.ibmq.ibmqbackend import IBMQSimulator


class Qpu:
	def __init__(
			self, id: str, name: str, version: str, last_updated: str, last_calibrated: str, max_shots: int, queue_size: int,
			number_of_qubits: int, avg_t1_time: float, avg_t2_time: float, avg_readout_error: float,
			avg_single_qubit_gate_error: float, avg_multi_qubit_gate_error: float, avg_single_qubit_gate_time: float,
			avg_multi_qubit_gate_time: float, max_gate_time: float, simulator: bool):
		self.id = id
		self.name = name
		self.version = version
		self.last_updated = last_updated
		self.last_calibrated = last_calibrated
		self.max_shots = max_shots
		self.queue_size = queue_size
		self.number_of_qubits = number_of_qubits
		self.avg_t1_time = avg_t1_time
		self.avg_t2_time = avg_t2_time
		self.avg_readout_error = avg_readout_error
		self.avg_single_qubit_gate_error = avg_single_qubit_gate_error
		self.avg_multi_qubit_gate_error = avg_multi_qubit_gate_error
		self.avg_single_qubit_gate_time = avg_single_qubit_gate_time
		self.avg_multi_qubit_gate_time = avg_multi_qubit_gate_time
		self.max_gate_time = max_gate_time
		self.simulator = simulator


class QpuSchema(Schema):
	id = fields.UUID()
	name = fields.Str()
	version = fields.Str()
	last_updated = fields.Str(data_key="lastUpdated")
	last_calibrated = fields.Str(data_key="lastCalibrated")
	max_shots = fields.Int(data_key="maxShots")
	queue_size = fields.Int(data_key="queueSize")
	number_of_qubits = fields.Int(data_key="numberOfQubits")
	avg_t1_time = fields.Float(data_key="avgT1Time")
	avg_t2_time = fields.Float(data_key="avgT2Time")
	avg_readout_error = fields.Float(data_key="avgReadoutError")
	avg_single_qubit_gate_error = fields.Float(data_key="avgSingleQubitGateError")
	avg_multi_qubit_gate_error = fields.Float(data_key="avgMultiQubitGateError")
	avg_single_qubit_gate_time = fields.Float(data_key="avgSingleQubitGateTime")
	avg_multi_qubit_gate_time = fields.Float(data_key="avgMultiQubitGateTime")
	max_gate_time = fields.Float(data_key="maxGateTime")
	simulator = fields.Bool()


class QpuList:
	def __init__(self, qpus: List[Qpu]):
		self.qpu_dtoes = qpus


class QpuListSchema(Schema):
	qpu_dtoes = fields.List(fields.Nested(QpuSchema), data_key="qpuDtoes")


class QpuListEmbedded:
	def __init__(self, qpu_list: QpuList):
		self.embedded = qpu_list


class QpuListEmbeddedSchema(Schema):
	embedded = fields.Nested(QpuListSchema, data_key="_embedded")


def generate_deterministic_uuid(namespace: str, name: str) -> UUID:
	digest = sha256(sha256(bytes(namespace, "utf-8")).digest() + sha256(bytes(name, "utf-8")).digest()).digest()

	return UUID(bytes=digest[0:16])


def backend_to_dto(backend: IBMQBackend) -> Qpu:
	properties = backend.properties()
	status = backend.status()

	backend_name = status.backend_name
	backend_version = status.backend_version
	queue_size = status.pending_jobs
	max_shots = backend.configuration().max_shots
	number_of_qubits = backend.configuration().n_qubits

	qpu_id = generate_deterministic_uuid("ibmq.qpu", backend_name)
	last_updated_utc = datetime.utcnow().isoformat()

	if isinstance(backend, IBMQSimulator):
		return Qpu(
			id=str(qpu_id), name=backend_name, version=backend_version, last_updated=last_updated_utc, last_calibrated="",
			max_shots=max_shots, queue_size=queue_size, number_of_qubits=number_of_qubits, avg_t1_time=0,
			avg_t2_time=0, avg_readout_error=0, avg_single_qubit_gate_error=0, avg_multi_qubit_gate_error=0,
			avg_single_qubit_gate_time=0, avg_multi_qubit_gate_time=0, max_gate_time=0, simulator=True)
	else:
		number_of_qubits = len(properties.qubits)
		sum_t1 = 0
		sum_t2 = 0
		sum_readout_error = 0

		for q in range(number_of_qubits):
			sum_t1 += properties.t1(q)
			sum_t2 += properties.t2(q)
			sum_readout_error += properties.readout_error(q)

		avg_t1 = sum_t1 / number_of_qubits
		avg_t2 = sum_t2 / number_of_qubits
		avg_readout_error = sum_readout_error / number_of_qubits

		sum_single_qubit_gate_error = 0
		sum_single_qubit_gate_time = 0
		single_qubit_gate_cnt = 0
		sum_multi_qubit_gate_error = 0
		sum_multi_qubit_gate_time = 0
		multi_qubit_gate_cnt = 0
		max_gate_time = 0

		for gate in properties.gates:
			if len(gate.qubits) == 1:
				for param in gate.parameters:
					if param.name == "gate_error":
						sum_single_qubit_gate_error += param.value
						max_gate_time = max(max_gate_time, param.value)
					if param.name == "gate_length":
						sum_single_qubit_gate_time += param.value
				single_qubit_gate_cnt += 1
			if len(gate.qubits) == 2:
				for param in gate.parameters:
					if param.name == "gate_error":
						sum_multi_qubit_gate_error += param.value
						max_gate_time = max(max_gate_time, param.value)
					if param.name == "gate_length":
						sum_multi_qubit_gate_time += param.value
				multi_qubit_gate_cnt += 1

		avg_single_qubit_gate_error = sum_single_qubit_gate_error / single_qubit_gate_cnt
		avg_single_qubit_gate_time = sum_single_qubit_gate_time / single_qubit_gate_cnt
		avg_multi_qubit_gate_error = 0

		if multi_qubit_gate_cnt != 0:
			avg_multi_qubit_gate_error = sum_multi_qubit_gate_error / multi_qubit_gate_cnt

		avg_multi_qubit_gate_time = 0

		if multi_qubit_gate_cnt != 0:
			avg_multi_qubit_gate_time = sum_multi_qubit_gate_time / multi_qubit_gate_cnt

		last_calibrated_with_timezone: datetime = properties.last_update_date
		last_calibrated_utc = datetime.utcfromtimestamp(last_calibrated_with_timezone.timestamp()).isoformat()

		return Qpu(
			id=str(qpu_id), name=backend_name, version=backend_version, last_updated=last_updated_utc,
			last_calibrated=last_calibrated_utc, max_shots=max_shots, queue_size=queue_size, number_of_qubits=number_of_qubits,
			avg_t1_time=avg_t1, avg_t2_time=avg_t2, avg_readout_error=avg_readout_error,
			avg_single_qubit_gate_error=avg_single_qubit_gate_error, avg_multi_qubit_gate_error=avg_multi_qubit_gate_error,
			avg_single_qubit_gate_time=avg_single_qubit_gate_time, avg_multi_qubit_gate_time=avg_multi_qubit_gate_time,
			max_gate_time=max_gate_time, simulator=False)


def get_all_qpus_and_metrics_as_json_str(token: str):
	try:
		IBMQ.disable_account()
	except:
		pass

	account_provider = IBMQ.enable_account(token)
	backends = account_provider.backends()
	qpu_dtoes = []

	for backend in backends:
		qpu_dtoes.append(backend_to_dto(backend))

	result = QpuListEmbedded(QpuList(qpu_dtoes))

	return QpuListEmbeddedSchema().dump(result)
