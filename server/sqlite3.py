# -*- coding: utf-8 -*-
#!/usr/bin/env python

from contextlib import closing
import sqlite3
import time
from .config import  SQLITE3_DB

def get_status(uid):
    with closing(sqlite3.connect(SQLITE3_DB)) as connection:
        with closing(connection.cursor()) as cursor:
            cursor.execute("create table if not exists metalogo_server (uid TEXT primary key, status TEXT, created INTEGER, finished INTEGER )")
            rows = cursor.execute(f"SELECT uid, status FROM metalogo_server WHERE uid = '{uid}'").fetchall()
            if len(rows) == 1:
                return rows[0][1]
            else:
                return 'not found'
    

def write_status(uid,status,db=SQLITE3_DB):
    with closing(sqlite3.connect(db)) as connection:
        with closing(connection.cursor()) as cursor:
            cursor.execute("create table if not exists metalogo_server (uid TEXT primary key, status TEXT, created INTEGER, finished INTEGER )")
            rows = cursor.execute(f"SELECT uid, status FROM metalogo_server WHERE uid = '{uid}'").fetchall()
            if len(rows) == 1:
                cursor.execute(f"UPDATE metalogo_server SET status = '{status}' where uid = '{uid}' ")
            else:
                cursor.execute(f"INSERT INTO metalogo_server VALUES ('{uid}','{status}','{round(time.time())}',-1) ")
        connection.commit()