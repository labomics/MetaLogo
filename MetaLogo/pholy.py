#!/usr/bin/env python
import os
import uuid
from . import utils

def auto_detect_groups(seqs, seq_fa, group_resolution=1, clustalo='clustalo',uid='', fa_output_dir=''):

    if seq_fa == '':
        if uid == '':
            uid = str(uuid.uuid4())
        seq_fa = f'{fa_output_dir}/server.{uid}.fa'

    if not os.path.exists(seq_fa): 
        utils.save_seqs(seqs, seq_fa)

    msa(seq_fa,clustalo,f'{fa_output_dir}/server.{uid}.msa.fa')

    return

def msa(seq_fa,clustalo,outfile):
    print(f'in msa, {outfile}')
    cmd = f'{clustalo} --auto -i {seq_fa} -o {outfile}'
    print(cmd)
    return os.system(f'{clustalo} --auto -i {seq_fa} -o {outfile}')