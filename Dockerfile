FROM python:3.7
LABEL maintainer "Yaowen Chen <achenge07@163.com>"
WORKDIR /code
COPY requirements.txt /code/requirements.txt
RUN pip install -r requirements.txt
COPY dependencies /code/ 
RUN cd /code/dependencies
#install clusta omega
RUN chmod a+x clustalo
RUN cp clustalo /usr/bin
#install Fasttree
RUN chmod a+x FastTree
RUN cp FastTree /usr/bin
# "https://redis.io/topics/quickstart"
RUN tar xzvf redis-stable.tar.gz 
RUN cd redis-stable 
RUN make
RUN makdir /etc/redis
RUN mkdir /var/redis
RUN cp utils/redis_init_script /etc/init.d/redis_6379
RUN cp ../6379.conf /etc/redis/6379.conf
RUN mkdir /var/redis/6379
RUN update-rc.d redis_6379 defaults
#RUN /etc/init.d/redis_6379 start
#supervisor configure
RUN cd ..
RUN cp supervisord.conf /etc/
WORKDIR /code
EXPOSE 8050
CMD supervisord -c /etc/supervisord; GUNICORN_CMD_ARGS='--workers 10 --timeout 300 --threads 10 -b 0.0.0.0:8050 --access-logfile logs/access.log --error-logfile logs/err.log --capture-output --access-logformat "%({X-Forwarded-For}i)s %(l)s %(u)s %(t)s \"%(r)s\" %(s)s %(b)s \"%(f)s\" \"%(a)s\"" ' gunicorn MetaLogo.server.index:server