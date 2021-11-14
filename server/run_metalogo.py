import os
import sys

def execute(config_file):
    cmd = f"/home/achen/anaconda3/envs/dash2/bin/python -m MetaLogo.entry --config {config_file}"
    try:
        print(cmd)
        os.system(cmd)
        return 0
    except Exception as e:
        return e