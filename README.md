# qiskit-service
Service for supporting transpilation and execution of implementations written in Qiskit.

### Transpilation Request
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

### Execution Request
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