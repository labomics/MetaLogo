# -*- coding: utf-8 -*-
#!/usr/bin/env python

from rq import Connection, Queue
from redis import Redis
from .sqlite3 import write_status
from .run_metalogo import execute
import toml

def enqueue(config_file,queue='default'):

    config = toml.load(config_file)
    write_status(config['uid'],'in-queue')
    redis_conn = Redis()
    q = Queue(queue,connection=redis_conn)
    job = q.enqueue(execute,config_file)
    return 0
