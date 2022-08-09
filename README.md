# qiskit-service

This service takes a Qiskit or OpenQASM implementation as data or via a URL and returns either compiled circuit properties and the transpiled OpenQASM String (Transpilation Request) or its results (Execution Request) depending on the input data and selected backend.


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

Now the qiskit-service is available on http://localhost:5013/.

## Transpilation Request
Send implementation, input, QPU information, and your IBM Quantum Experience token to the API to get analyzed properties of the transpiled circuit and the transpiled OpenQASM circuit itself.
*Note*: ``token`` should either be in ``input-params`` or extra. Both variants are combined here for illustration purposes. Furthermore, ``url``,``hub``,``group``,``project`` can be defined in ``input-params``.
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
        "url": {
            "rawValue": "YOUR-IBMQ-AUTHENTICATION-URL",
            "type": "Unknown"
        }
        "hub": {
            "rawValue": "YOUR-IBMQ-HUB",
            "type": "Unknown"
        }
        "group": {
            "rawValue": "YOUR-IBMQ-GROUP",
            "type": "Unknown"
        }
        "project": {
            "rawValue": "YOUR-IBMQ-PROJECT",
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
        },
        "url": {
            "rawValue": "YOUR-IBMQ-AUTHENTICATION-URL",
            "type": "Unknown"
        },
        "hub": {
            "rawValue": "YOUR-IBMQ-HUB",
            "type": "Unknown"
        },
        "group": {
            "rawValue": "YOUR-IBMQ-GROUP",
            "type": "Unknown"
        },
        "project": {
            "rawValue": "YOUR-IBMQ-PROJECT",
            "type": "Unknown"
        }
    },
    "token": "YOUR-IBMQ-TOKEN"
}
```

#### Transpilation as OpenQasm-String
```
{  
    "qasm-string": "OpenQASM String",
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
        },
        "url": {
            "rawValue": "YOUR-IBMQ-AUTHENTICATION-URL",
            "type": "Unknown"
        },
        "hub": {
            "rawValue": "YOUR-IBMQ-HUB",
            "type": "Unknown"
        },
        "group": {
            "rawValue": "YOUR-IBMQ-GROUP",
            "type": "Unknown"
        },
        "project": {
            "rawValue": "YOUR-IBMQ-PROJECT",
            "type": "Unknown"
        }
    },
    "token": "YOUR-IBMQ-TOKEN"
}
```


## Execution Request
Send implementation, input, QPU information, and your IBM Quantum Experience token to the API to execute your circuit and get the result.
*Note*: ``token`` should either be in ``input-params`` or extra. Both variants are combined here for illustration purposes. Furthermore, ``url``,``hub``,``group``,``project`` can be defined in ``input-params``.

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
        },
        "url": {
            "rawValue": "YOUR-IBMQ-AUTHENTICATION-URL",
            "type": "Unknown"
        },
        "hub": {
            "rawValue": "YOUR-IBMQ-HUB",
            "type": "Unknown"
        },
        "group": {
            "rawValue": "YOUR-IBMQ-GROUP",
            "type": "Unknown"
        },
        "project": {
            "rawValue": "YOUR-IBMQ-PROJECT",
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
        },
        "url": {
            "rawValue": "YOUR-IBMQ-AUTHENTICATION-URL",
            "type": "Unknown"
        },
        "hub": {
            "rawValue": "YOUR-IBMQ-HUB",
            "type": "Unknown"
        },
        "group": {
            "rawValue": "YOUR-IBMQ-GROUP",
            "type": "Unknown"
        },
        "project": {
            "rawValue": "YOUR-IBMQ-PROJECT",
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
        },
        "url": {
            "rawValue": "YOUR-IBMQ-AUTHENTICATION-URL",
            "type": "Unknown"
        },
        "hub": {
            "rawValue": "YOUR-IBMQ-HUB",
            "type": "Unknown"
        },
        "group": {
            "rawValue": "YOUR-IBMQ-GROUP",
            "type": "Unknown"
        },
        "project": {
            "rawValue": "YOUR-IBMQ-PROJECT",
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

## Benchmark Request
Send QPU information, the width and depth of the circuit, the number of circuits you want to create, the number of shots
and your IBM Quantum Experience token to the API to get the result on the IBM Quantum Simulator, and the stated QPU.
The response also contains a link to the summary of the benchmark.

`POST /qiskit-service/api/v1.0/randomize`

```
{  
    "qpu-name": "NAME-OF-QPU",
    "number-of-qubits": "NUMBER-OF-QUBITS",
    "min-depth-of-circuit": "MIN-DEPTH-OF-THE-RANDOMIZED-CIRCUIT",
    "max-depth-of-circuit": "MAX-DEPTH-OF-THE-RANDOMIZED-CIRCUIT",
    "number-of-circuits": "NUMBER-OF-CIRCUITS",
    "shots": "NUMBER-OF-SHOTS",
    "token": "YOUR-IBMQ-TOKEN"
}
```

Please make sure that ```number-of-qubits```, ```number-of-circuits``` and ```min-depth-of-circuit``` are greater than 0.
Also, ```max-depth-of-cicuit``` has to be greater or equal to ```min-depth-of-circuit```.

Returns a list of links to the results on both backends, and a link to the benchmark result which returns corresponding
executions on simulator and real quantum computer.
Access those via `GET /qiskit-service/api/v1.0/benchmarks/<benchmark_id>`.`

## Analysis Request
Request an analysis of all benchmarks in the database that successfully returned a result.
For those benchmarks, the histograms of the simulator's and the quantum computer's result are compared using the four metrics:
Chi-Square-Distance, Correlation, Percentage Error and Histogram Intersection.
- Chi-Square-Distance: Large values indicate a strong deviation between the two histogram, however it is not normalized and difficult to interpret.
- Correlation: Normalized between -1 and 1, where values close to 1 indicate a strong correlation between the histograms.
  Since the histograms often have a similar shape even though the counts are erroneous, the correlation often suggests success even for bad results.
- Percentage Error: Indicates the error in relation to the ideal value for each count separately.
  This metric does not provide a general view on the quality of the result.
- Histogram Intersection: Returns a value that indicates how much of the histograms overlap.
  It is normalized between 0 and 1, where 1 would mean that the two histograms are the same.
  Therefore, it is a useful metric to judge the quality of the quantum computer's result.
  
The reponse also includes the counts of simulator and quantum computer as well as the size of the transpiled circuit.

`GET /qiskit-service/api/v1.0/analysis`

## Sample Implementations for Transpilation and Execution
Sample implementations can be found [here](https://github.com/UST-QuAntiL/nisq-analyzer-content/tree/master/example-implementations).
Please use the raw GitHub URL as `impl-url` value (see [example](https://raw.githubusercontent.com/UST-QuAntiL/nisq-analyzer-content/master/example-implementations/Shor/shor-general-qiskit.py)).

## Get up-to-date data of QPUs
Get provider information:  
`GET /qiskit-service/api/v1.0/providers` 

Get up-to-date information about QPUs of IBMQ:  
`GET /qiskit-service/api/v1.0/providers/f8f0c200-875d-0ff8-0352-1be4666c5829/qpus`   
For the request, add your Qiskit token as header:  
`token: <YOUR-IBMQ-TOKEN>` 

## Haftungsausschluss

Dies ist ein Forschungsprototyp.
Die Haftung für entgangenen Gewinn, Produktionsausfall, Betriebsunterbrechung, entgangene Nutzungen, Verlust von Daten und Informationen, Finanzierungsaufwendungen sowie sonstige Vermögens- und Folgeschäden ist, außer in Fällen von grober Fahrlässigkeit, Vorsatz und Personenschäden, ausgeschlossen.

## Disclaimer of Warranty

Unless required by applicable law or agreed to in writing, Licensor provides the Work (and each Contributor provides its Contributions) on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied, including, without limitation, any warranties or conditions of TITLE, NON-INFRINGEMENT, MERCHANTABILITY, or FITNESS FOR A PARTICULAR PURPOSE.
You are solely responsible for determining the appropriateness of using or redistributing the Work and assume any risks associated with Your exercise of permissions under this License.
