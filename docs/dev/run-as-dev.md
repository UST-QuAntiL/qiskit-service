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

### Python Packages
Install packages as listed in [requirements.txt](https://github.com/PlanQK/qiskit-service/blob/master/requirements.txt).
Python 3.7 required.

### IBMQ Account
Save your IBMQ token to disk with
```
python
import qiskit
qiskit.IBMQ.save_account(TOKEN)
```

### Database
* Install SQLite DB, f.e. as described [here](https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-iv-database)
* create a `data` folder in the `app` folder
* Setup results table with the following commands:
```
flask db migrate -m "results table"
flask db upgrade
```

* To look at the DB:
```
flask shell
from app import db
from app.result_model import Result
Result.query.all()
```

### Queueing
* Start redis Docker:
`docker run -p 6379:6379 redis`

* Start worker:
`rq worker qiskit-service_execute`