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