FROM python:3.7
LABEL maintainer "Yaowen Chen <achenge07@163.com>"
WORKDIR /code
RUN pip install -r requirements.txt
RUN mkdir MetaLogo/bins
WORKDIR /code/MetaLogo/dependencies
RUN chmod a+x clustalo
RUN tar xzvf rate4site-3.0.0.tar.gz
WORKDIR /MetaLogo/dependencies/rate4site-3.0.0/
EXPOSE 8050
CMD GUNICORN_CMD_ARGS='--workers 10 --timeout 300 --threads 10 -b 0.0.0.0:8050 --access-logfile logs/access.log --error-logfile logs/err.log --capture-output --access-logformat "%({X-Forwarded-For}i)s %(l)s %(u)s %(t)s \"%(r)s\" %(s)s %(b)s \"%(f)s\" \"%(a)s\"" ' gunicorn server.main:server