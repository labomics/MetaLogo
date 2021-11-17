import os
import sys
import toml
from ..MetaLogo.entry import run_from_config
from .sqlite3 import write_status

def execute(config_file):

    config = toml.load(config_file)
    try:
        write_status(config['uid'],'running')
        run_from_config(config_file)
        write_status(config['uid'],'finished',config['sqlite3_db'])
        return 0
    except Exception as e:
        print(e)
        write_status(config['uid'],'error',config['sqlite3_db'])
        return e