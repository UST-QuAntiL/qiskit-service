# Run environment as dev

## Packages
Install packages as listed in [requirements.txt](https://github.com/PlanQK/qiskit-service/blob/master/requirements.txt).
Python 3.7 required.

## Queueing
* Start redis Docker:
`docker run -p 6379:6379 redis`

* Start worker:
`rq worker qiskit-service_execute`

## Database
* Install SQLite DB, f.e. as described [here](https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-iv-database)

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
