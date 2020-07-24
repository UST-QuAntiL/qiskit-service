import os
import tempfile
import pytest

from app import Config, db
from app.result_model import Result
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from redis import Redis
import rq
from flask import Flask


@pytest.fixture(scope='module')
def test_client():

    flask_app = Flask(__name__)
    flask_app.config.from_object(Config)

    flask_app.config['BCRYPT_LOG_ROUNDS'] = 4
    flask_app.config['TESTING'] = True
    flask_app.config['WTF_CSRF_ENABLED'] = False

    db = SQLAlchemy(flask_app)
    migrate = Migrate(flask_app, db)

    flask_app.redis = Redis.from_url(flask_app.config['REDIS_URL'])
    flask_app.execute_queue = rq.Queue('qiskit-service_execute', connection=flask_app.redis, default_timeout=3600)

    test_client = flask_app.test_client()

    context = flask_app.app_context()
    context.push()

    yield test_client

    context.pop()


@pytest.fixture()
def add_dummy_results():

    result = Result(id="0")
    db.session.add(result)
    db.session.commit()


def test_version(test_client):

    response = test_client.get('/qiskit-service/api/v1.0/version')

    assert response.status_code == 200
    assert 'version' in response.data
    assert response.data['version'] == '1.0'


def test_get_result(test_client):

    result_id = "0"
    response = test_client.get('/qiskit-service/api/v1.0/results/%s/' % result_id)

    assert response.status_code == 200



