import os
import sys
import toml
import sys
from .sqlite3 import write_status
from ..MetaLogo.entry import run_from_config


def execute(config_file):
    config = toml.load(config_file)
    try:
        write_status(config['uid'],'running')
        result = run_from_config(config_file)

        if (result is not None) and 'error' in result:
            error = result['error']
            write_status(config['uid'],'error',config['sqlite3_db'])
            write_status(f"{config['uid']}-errinfo",error,config['sqlite3_db'])
        else:
            write_status(config['uid'],'finished',config['sqlite3_db'])

    except Exception as e:
        print('error:',e)
        write_status(config['uid'],'error',config['sqlite3_db'])
        write_status(f"{config['uid']}-errinfo",e,config['sqlite3_db'])
        return e