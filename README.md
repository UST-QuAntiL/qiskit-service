# qiskit-service
Service for supporting transpilation and execution of implementations written in Qiskit.

## Setup
* Clone repository:
```
git clone https://github.com/PlanQK/qiskit-service.git   
git clone git@github.com:PlanQK/qiskit-service.git
```

* Start containers:
```
docker-compose pull
docker-compose up
```

## After implementation changes
* Update container:
```
docker build -t planqk/qiskit-service:latest .
docker push planqk/qiskit-service:latest
```

* Start containers:
```
docker-compose pull
docker-compose up
```

## Transpilation Request
Send implementation, input, QPU information, and your IBM Quantum Experience token to the API to get depth and width of resulting circuit.

`POST /qiskit-service/api/v1.0/transpile`  
```
{  
    "impl-url": "URL-OF-IMPLEMENTATION",
    "qpu-name": "NAME-OF-QPU",
    "input-params": {"PARAM-NAME-1": YOUR-VALUE-1, "PARAM-NAME-2": YOUR-VALUE-2, ...},
    "token": "YOUR-TOKEN"
}  
```

## Execution Request
Send implementation, input, QPU information, and your IBM Quantum Experience token to the API to execute your circuit and get the result.

`POST /qiskit-service/api/v1.0/execute`  
```
{  
    "impl-url": "URL-OF-IMPLEMENTATION",
    "qpu-name": "NAME-OF-QPU",
    "input-params": {"PARAM-NAME-1": YOUR-VALUE-1, "PARAM-NAME-2": YOUR-VALUE-2, ...},
    "token": "YOUR-TOKEN"
}
```

Returns a content location for the result. Access it via `GET`.

## Haftungsausschluss

Dies ist ein Forschungsprototyp.
Die Haftung für entgangenen Gewinn, Produktionsausfall, Betriebsunterbrechung, entgangene Nutzungen, Verlust von Daten und Informationen, Finanzierungsaufwendungen sowie sonstige Vermögens- und Folgeschäden ist, außer in Fällen von grober Fahrlässigkeit, Vorsatz und Personenschäden, ausgeschlossen.

## Disclaimer of Warranty

Unless required by applicable law or agreed to in writing, Licensor provides the Work (and each Contributor provides its Contributions) on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied, including, without limitation, any warranties or conditions of TITLE, NON-INFRINGEMENT, MERCHANTABILITY, or FITNESS FOR A PARTICULAR PURPOSE.
You are solely responsible for determining the appropriateness of using or redistributing the Work and assume any risks associated with Your exercise of permissions under this License.
