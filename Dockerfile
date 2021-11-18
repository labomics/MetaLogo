FROM python:3.7
LABEL maintainer "Yaowen Chen <achenge07@163.com>"
WORKDIR /code
COPY requirements.txt /code/requirements.txt
RUN pip install -r requirements.txt
COPY dependencies /code/
#install clusta omega
RUN chmod a+x clustalo
RUN cp clustalo /usr/bin
#install Fasttree
RUN chmod a+x FastTree
RUN chmod a+x FastTreeMP
RUN cp FastTree /usr/bin
RUN cp FastTreeMP /usr/bin
# "https://redis.io/topics/quickstart"
RUN tar xzvf redis-stable.tar.gz
WORKDIR /code/redis-stable
RUN make
RUN make install
RUN mkdir /etc/redis
RUN mkdir /var/redis
RUN cp utils/redis_init_script /etc/init.d/redis_6379
RUN cp ../6379.conf /etc/redis/6379.conf
RUN mkdir /var/redis/6379
RUN update-rc.d redis_6379 defaults
#RUN /etc/init.d/redis_6379 start
#supervisor configure
WORKDIR /code
RUN cp supervisord.conf /etc/
COPY server.cmd.sh /code/
EXPOSE 8050
CMD sh MetaLogo/server.cmd.sh
