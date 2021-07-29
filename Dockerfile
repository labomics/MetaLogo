FROM python:3.7
LABEL maintainer "Yaowen Chen <achenge07@163.com>"
WORKDIR /code
RUN useradd -r metalogo
RUN chown metalogo:metalogo /code
USER metalogo
COPY requirements.txt /code
RUN pip install -r /code/requirements.txt
COPY ./ ./
EXPOSE 8050
CMD [ "gunicorn", "--workers=1", "--threads=1", "-b 0.0.0.0:8050", "server.main:server"]
