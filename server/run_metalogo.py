import os
import sys
import toml
import sys
from .sqlite3 import write_status
from ..MetaLogo.entry import run_from_config


def execute(config_file):
    print('enter execute')
    config = toml.load(config_file)
    try:
        write_status(config['uid'],'running')
        run_from_config(config_file)
        write_status(config['uid'],'finished',config['sqlite3_db'])
    except Exception as e:
        print(e)
        write_status(config['uid'],'error',config['sqlite3_db'])
        return e

#def execute(config_file):
#    config = toml.load(config_file)
#    cmd = f"/home/achen/anaconda3/envs/dash2/bin/python -m MetaLogo.entry --config {config_file}"
#    try:
#        print(cmd)
#        write_status(config['uid'],'running')
#        res = os.system(cmd)
#        if res == -1
#        return 0
#    except Exception as e:
#        return e
#