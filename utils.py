#!/usr/bin/python
from numpy.lib.function_base import delete
from .format_utils import process_data
import tempfile
import os
import uuid
import numpy as np


def read_file(filename, filetype, min_length, max_length):

    seq_dict = {}
    seqnames = []
    seqname = None
    seq = None
    ith = 0
    if filetype == 'fasta':
        with open(filename,'r') as inpf:
            for line in inpf:
                line = line.strip()
                if line[0] == '>':
                    ith += 1
                    seqname = f'{line[1:]}-{ith}'
                    seqnames.append(seqname)
                else:
                    seq_dict[seqname]  = seq_dict.get(seqname,'') + line
    elif filetype == 'fastq':
        with open(filename,'r') as inpf:
            num = -1
            for line in inpf:
                line = line.strip()
                num += 1
                if num%4 == 0:
                    assert line[0] == '@'
                    seqname = line[1:]
                    seqnames.append(seqname)
                if num%4 == 1:
                    seq_dict[seqname] = line
    else:
        pass

    return [[seqname,seq_dict[seqname]]  for seqname in seqnames if (len(seq_dict[seqname])>=min_length) and (len(seq_dict[seqname])<=max_length)]

def grouping(seqs,group_by='length',group_file=None):
    groups_dict = {}
    if group_by == 'length':
        for name,seq in seqs:
            #print(name,seq)
            if len(seq) not in groups_dict:
                groups_dict[len(seq)] = []
            groups_dict[len(seq)].append([name,seq])
    #return sorted(groups_dict.items(),key=lambda d:d[0])
    return groups_dict

def write_to_tmp(seqs,tmp_path = './tmp/'):
    if not os.path.exists(tmp_path):
        os.mkdir(tmp_path)

    uid = str(uuid.uuid4())
    f_name = os.path.join(tmp_path,f'{uid}.fa')
    with open(f_name,'w') as outpf:
        for name,seq in seqs:
            outpf.write(f'>{name}\n')
            outpf.write(f'{seq}\n')
    return f_name

        
def compute_bits(groups,tmp_path = './tmp/'):
    ic_table = {}
    for group_id,group in groups.items():
        tmpf_name = write_to_tmp(group,tmp_path)
        _,ic = process_data(tmpf_name,data_type='fasta')
        ic_table[group_id] = ic
    return ic_table

def angle_between(p1, p2=(0,0)):
    ang1 = np.arctan2(*p1[::-1])
    ang2 = np.arctan2(*p2[::-1])
    return (ang1 - ang2) % (2 * np.pi)

def get_coor_by_angle(radius, angle, origin=(0,0)):
    relative_coor =  (radius * np.cos(angle), radius * np.sin(angle))
    return (relative_coor[0]+origin[0],relative_coor[1]+origin[1])


