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
## API Documentation
The qiskit-service provides a Swagger UI, specifying the request schemas and showcasing exemplary requests for all API endpoints.
* http://localhost:5013/api/swagger-ui

_Note_: To run the setup as a developer, see [here](./docs/dev/run-as-dev.md).

## Using AWS Braket QPUs
To execute quantum circuits on AWS Braket QPUs via the qiskit service, an AWS IAM account with the Braket Group membership is required.
The AWS access key and the AWS secret access key have to be provided in the request json body to transpile or execute quantum circuits for/on AWS Braket QPUs.

_Note_: The default region for this request is `eu-west-2` (Europe London) but can also be changed by providing the region under the `region` key within the `input_params` in the request json body.
Do note though that the region has to be selected depending on the QPU to use. For more details, see [here](https://docs.aws.amazon.com/braket/latest/developerguide/braket-regions.html).

## Sample Implementations for Transpilation and Execution
Sample implementations can be found [here](https://github.com/UST-QuAntiL/nisq-analyzer-content/tree/master/example-implementations).
Please use the raw GitHub URL as `impl-url` value (see [example](https://raw.githubusercontent.com/UST-QuAntiL/nisq-analyzer-content/master/example-implementations/Shor/shor-general-qiskit.py)).

## Haftungsausschluss

Dies ist ein Forschungsprototyp.
Die Haftung für entgangenen Gewinn, Produktionsausfall, Betriebsunterbrechung, entgangene Nutzungen, Verlust von Daten und Informationen, Finanzierungsaufwendungen sowie sonstige Vermögens- und Folgeschäden ist, außer in Fällen von grober Fahrlässigkeit, Vorsatz und Personenschäden, ausgeschlossen.

## Disclaimer of Warranty

Unless required by applicable law or agreed to in writing, Licensor provides the Work (and each Contributor provides its Contributions) on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied, including, without limitation, any warranties or conditions of TITLE, NON-INFRINGEMENT, MERCHANTABILITY, or FITNESS FOR A PARTICULAR PURPOSE.
You are solely responsible for determining the appropriateness of using or redistributing the Work and assume any risks associated with Your exercise of permissions under this License.
