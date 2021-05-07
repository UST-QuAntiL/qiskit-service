# qiskit-service

This service takes a Qiskit or OpenQASM implementation as data or via an URL and returns either its depth, width and the transpiled OpenQASM String (Transpilation Request) or its results (Execution Request) depending on the input data and selected backend.


[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

## Setup
* Clone repository:
```
git clone https://github.com/UST-QuAntiL/qiskit-service.git 
git clone git@github.com:UST-QuAntiL/qiskit-service.git
```

* Start containers:
```
docker-compose pull
docker-compose up
```

Now the qiskit-service is available on http://localhost:5000/.

## Transpilation Request
Send implementation, input, QPU information, and your IBM Quantum Experience token to the API to get depth and width of the transpiled circuit and the transpiled OpenQASM circuit itself.
*Note*: ``token`` should either be in ``input-params`` or extra. Both variants are combined here or illustration purposes.
`POST /qiskit-service/api/v1.0/transpile`  

#### Transpilation via URL
```
{  
    "impl-url": "URL-OF-IMPLEMENTATION",
    "impl-language": "Qiskit"/"OpenQASM",
    "qpu-name": "NAME-OF-QPU",
    "input-params": {
        "PARAM-NAME-1": {
            "rawValue": "YOUR-VALUE-1",
            "type": "Integer"
        },
        "PARAM-NAME-2": {
            "rawValue": "YOUR-VALUE-2",
            "type": "String"
        },
        ...
        "token": {
            "rawValue": "YOUR-IBMQ-TOKEN",
            "type": "Unknown"
        }
    },
    "token": "YOUR-IBMQ-TOKEN"
}
```
#### Transpilation via data
```
{  
    "impl-data": "BASE64-ENCODED-IMPLEMENTATION",
    "impl-language": "Qiskit"/"OpenQASM",
    "qpu-name": "NAME-OF-QPU",
    "input-params": {
        "PARAM-NAME-1": {
            "rawValue": "YOUR-VALUE-1",
            "type": "Integer"
        },
        "PARAM-NAME-2": {
            "rawValue": "YOUR-VALUE-2",
            "type": "String"
        },
        ...
        "token": {
            "rawValue": "YOUR-IBMQ-TOKEN",
            "type": "Unknown"
        }
    },
    "token": "YOUR-IBMQ-TOKEN"
}
```

## Execution Request
Send implementation, input, QPU information, and your IBM Quantum Experience token to the API to execute your circuit and get the result.
*Note*: ``token`` should either be in ``input-params`` or extra. Both variants are combined here for illustration purposes.

`POST /qiskit-service/api/v1.0/execute`  
#### Execution via URL
```
{  
    "impl-url": "URL-OF-IMPLEMENTATION",
    "impl-language": "Qiskit"/"OpenQASM",
    "qpu-name": "NAME-OF-QPU",
    "input-params": {
        "PARAM-NAME-1": {
            "rawValue": "YOUR-VALUE-1",
            "type": "Integer"
        },
        "PARAM-NAME-2": {
            "rawValue": "YOUR-VALUE-2",
            "type": "String"
        },
        ...
        "token": {
            "rawValue": "YOUR-IBMQ-TOKEN",
            "type": "Unknown"
        }
    },
    "token": "YOUR-IBMQ-TOKEN"
}
```
#### Execution via data
```
{  
    "impl-data": "BASE64-ENCODED-IMPLEMENTATION",
    "impl-language": "Qiskit"/"OpenQASM",
    "qpu-name": "NAME-OF-QPU",
    "input-params": {
        "PARAM-NAME-1": {
            "rawValue": "YOUR-VALUE-1",
            "type": "Integer"
        },
        "PARAM-NAME-2": {
            "rawValue": "YOUR-VALUE-2",
            "type": "String"
        },
        ...
        "token": {
            "rawValue": "YOUR-IBMQ-TOKEN",
            "type": "Unknown"
        }
    },
    "token": "YOUR-IBMQ-TOKEN"
}
```
#### Execution via transpiled OpenQASM String
```
{  
    "transpiled-qasm": "TRANSPILED-QASM-STRING",
    "qpu-name": "NAME-OF-QPU",
    "input-params": {
        "token": {
            "rawValue": "YOUR-IBMQ-TOKEN",
            "type": "Unknown"
        }
    },
    "token": "YOUR-IBMQ-TOKEN"
}
```

Returns a content location for the result. Access it via `GET`.

## Calibration Matrix Calculation Request
Send QPU information, optional shots, and your IBM Quantum Experience token to the API to calculate the calibration matrix for the given QPU.

`POST /qiskit-service/api/v1.0/calculate-calibration-matrix`
```
{
    "qpu-name": "NAME-OF-QPU",
    "token": "YOUR-IBMQ-TOKEN",
    "shots": "NUMBER-OF-SHOTS"
}
```

Returns a content location for the result. Access it via `GET`.

## Sample Implementations for Transpilation and Execution
Sample implementations can be found [here](https://github.com/UST-QuAntiL/nisq-analyzer-content/tree/master/example-implementations).
Please use the raw GitHub URL as `impl-url` value (see [example](https://raw.githubusercontent.com/UST-QuAntiL/nisq-analyzer-content/master/example-implementations/Shor/shor-general-qiskit.py)).

## Haftungsausschluss

Dies ist ein Forschungsprototyp.
Die Haftung für entgangenen Gewinn, Produktionsausfall, Betriebsunterbrechung, entgangene Nutzungen, Verlust von Daten und Informationen, Finanzierungsaufwendungen sowie sonstige Vermögens- und Folgeschäden ist, außer in Fällen von grober Fahrlässigkeit, Vorsatz und Personenschäden, ausgeschlossen.

## Disclaimer of Warranty

Unless required by applicable law or agreed to in writing, Licensor provides the Work (and each Contributor provides its Contributions) on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied, including, without limitation, any warranties or conditions of TITLE, NON-INFRINGEMENT, MERCHANTABILITY, or FITNESS FOR A PARTICULAR PURPOSE.
You are solely responsible for determining the appropriateness of using or redistributing the Work and assume any risks associated with Your exercise of permissions under this License.
