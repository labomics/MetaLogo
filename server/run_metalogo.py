import os
import sys

def execute(config_file):
    print('xjfioejqoifejowqpfjewqpo')
    print(sys.path)
    print(sys.executable)
    print(os.getcwd())
    cmd = f"/home/achen/anaconda3/envs/dash2/bin/python -m MetaLogo.entry --config {config_file}"
    try:
        os.system(cmd)
        return 0
    except Exception as e:
        return e