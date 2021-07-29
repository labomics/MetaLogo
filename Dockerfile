FROM python:3.7
LABEL maintainer "Yaowen Chen <achenge07@163.com>"
WORKDIR /code
COPY requirements.txt /code
RUN pip install -r /code/requirements.txt
COPY ./ ./
EXPOSE 8050
CMD [ "gunicorn", "--workers=1", "--threads=1", "-b 0.0.0.0:8050", "main:server"]
