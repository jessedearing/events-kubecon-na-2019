FROM tiangolo/uwsgi-nginx-flask:python3.7

RUN pip install kubernetes
COPY ./app /app
