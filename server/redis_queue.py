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
    q = Queue(queue,connection=redis_conn,default_timeout=3600)
    job = q.enqueue(execute,args=(config_file,),job_timeout=3600,
                    job_id=config['uid'],result_ttl=60*60*24*7,
                    on_success=report_success,on_failure=report_failure)
    return 0

def report_failure(job,connection,type,value,traceback):
    print('failure')
    print('args: ', job.args)
    print('traceback',traceback)
    write_status(job.id,'failed')

def report_success(job,connection,result,*args,**kwargs):
    print('finished: ', job.id)
    print('args: ', job.args)


def check_queue_status(job_id):
    #return if_found, is_failed, exc_info
    ret = []
    redis_conn = Redis()
    q  = Queue(connection=redis_conn)
    job = q.fetch_job(job_id)
    if job is not None:
        return True,job.is_failed,job.exc_info
    else:
        return False,False,''

