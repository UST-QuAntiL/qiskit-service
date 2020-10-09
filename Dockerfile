FROM python:3.7-slim

MAINTAINER Marie Salm "marie.salm@iaas.uni-stuttgart.de"

COPY ./requirements.txt /app/requirements.txt
WORKDIR /app
RUN apt-get update
RUN apt-get install -y gcc python3-dev
RUN pip install -r requirements.txt
COPY . /app

EXPOSE 5000/tcp

ENV FLASK_APP=qiskit-service.py
ENV FLASK_ENV=development
ENV FLASK_DEBUG=0
RUN echo "python -m flask db upgrade" > /app/startup.sh
RUN echo "gunicorn qiskit-service:app -b 0.0.0.0:5000 -w 4 --timeout 500 --log-level info" >> /app/startup.sh
CMD [ "sh", "/app/startup.sh" ]
