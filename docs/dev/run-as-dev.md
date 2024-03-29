# Run environment as Dev

Either run the qiskit-service via docker containers or install the requirements locally.

## Setup via Docker
* Update container after implementation changes:
```
docker build -t planqk/qiskit-service:latest .
```

* Start containers:
```
docker-compose up
```
## Local Setup
In PyCharm at _Run > Edit Configurations..._ set  
`Environment variables: FLASK_RUN_PORT=5013`.

### Python Packages
Install packages as listed in [requirements.txt](https://github.com/PlanQK/qiskit-service/blob/master/requirements.txt).
Python 3.9 required.

#### Update requirements
1. Update locally installed requirements
```
pip install -r requirements-unfrozen.txt -U
```
2. Check if all works
   (2.1 delete your local virtual environment, setup a new one and check if all works)
3. Pin all requirements
```
pip freeze > requirements.txt
```

### IBMQ Account
Save your IBMQ token to disk with
```
python
import qiskit
qiskit.IBMQ.save_account(TOKEN)
```

### Test setup
To run the tests store your Qiskit token as environment variable:  
```
QISKIT_TOKEN=***your-qiskit-token***
```

#### PlanQK token
To run PlanQK-related tests store your bearer token as environment variable:
```
BEARER_TOKEN=***your-bearer-token***
```
or like this with quotes if you run it from the command line:
```
export BEARER_TOKEN="***your-bearer-token***"
```

### PlanQK token: Example request with bearer token
If you want to make a request with an impl-url from the PlanQK platform, you need to provide your bearer token like this:
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
    "token": "YOUR-IBMQ-TOKEN",
    "bearer-token": "Bearer YOUR-PLANQK-BEARER-TOKEN"
}
```
### Database
* Install SQLite DB, f.e. as described [here](https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-iv-database)
* create a `data` folder in the `app` folder
* Setup results table (also consider benchmark table) with the following commands:
```
flask db migrate -m "results table"
flask db upgrade
```

To add further tables, run the following commands:  
```
flask db stamp head
flask db migrate
flask db upgrade
```

* To look at the DB:
```
flask shell
from app import db
from app.result_model import Result
Result.query.all()
```

#### Update existing tables:
Find the head using 
```
flask db history
```
Update the version_num field to the head version.  
Run migrate using
```
flask db migrate
```
Upgrade the database 
```
flask db upgrade
```

### Queueing
* Start redis Docker via command line:  
`docker run -p 5040:5040 redis --port 5040`

* Start worker via command line:  
`rq worker --url redis://localhost:5040 qiskit-service_execute`