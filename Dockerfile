FROM python:3.7
LABEL maintainer "Yaowen Chen <achenge07@163.com>"
WORKDIR /code
COPY requirements.txt /code
RUN pip install -r /code/requirements.txt
EXPOSE 8050
CMD GUNICORN_CMD_ARGS='--workers 10 --timeout 300 --threads 10 -b 0.0.0.0:8050 --access-logfile logs/access.log --error-logfile logs/err.log --capture-output' gunicorn server.main:server