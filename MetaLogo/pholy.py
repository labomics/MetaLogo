#!/usr/bin/env python
import os
import uuid
from . import utils
import pandas as pd

def auto_detect_groups(seqs, seq_fa, group_resolution=1, clustalo='clustalo',uid='', fa_output_dir=''):
    print('enter auto detect')

    if seq_fa == '':
        if uid == '':
            uid = str(uuid.uuid4())
        seq_fa = f'{fa_output_dir}/server.{uid}.fa'

    if not os.path.exists(seq_fa): 
        utils.save_seqs(seqs, seq_fa)

    dep_seq_fa = f'{fa_output_dir}/server.{uid}.dep.fa'
    name_dict, seq_dict = deduplicate(seq_fa,dep_seq_fa)


    msa_dict = msa(dep_seq_fa,clustalo,f'{fa_output_dir}/server.{uid}.msa.fa')

    rate4site(f'{fa_output_dir}/server.{uid}.msa.fa',f'{fa_output_dir}/server.{uid}.rate4site.scores',
                f'{fa_output_dir}/server.{uid}.rate4site.tree',
                f'{fa_output_dir}/server.{uid}.rate4site.unnorm_rates')
    
    treecluster(group_resolution,f'{fa_output_dir}/server.{uid}.rate4site.tree',f'{fa_output_dir}/server.{uid}.rate4site.cluster')

    cluster_df = pd.read_csv(f'{fa_output_dir}/server.{uid}.rate4site.cluster',sep='\t')
    groups_dict = {}
    for index, grp in cluster_df.groupby('ClusterNumber'):
        groups_dict[index] = []
        for seqname in grp['SequenceName']:
            for _seqname in name_dict[seqname]:
                groups_dict[index].append([_seqname,msa_dict[seqname]])
    return groups_dict

def msa(seq_fa,clustalo,outfile):
    print(f'in msa, {outfile}')
    cmd = f'{clustalo} --auto -i {seq_fa} -o {outfile}'
    print(cmd)
    os.system(f'{clustalo} --auto -i {seq_fa} -o {outfile}')
    msa_dict = {}
    with open(outfile,'r') as inpf:
        seqname = ''
        seq = ''
        for line in inpf:
            line = line.strip()
            if line[0] == '>':
                if seq != '':
                    msa_dict[seqname] = seq
                seqname = line[1:]
                seq = ''
            else:
                seq += line
        if seq != '':
            msa_dict[seqname] = seq
    return msa_dict

def rate4site(msa_fa,outfile_score,outfile_tree,outfile_unnorm_rates,rate4site_bin='bins/bin/rate4site'):
    print('in rate4site...')
    cmd = f'{rate4site_bin} -s {msa_fa} -o {outfile_score} -x {outfile_tree} -y {outfile_unnorm_rates}'
    print(cmd)
    return os.system(cmd)

def treecluster(threshold,treefile,outfile):
    print('in tree cluster')
    cmd = f'python /home/achen/anaconda3/envs/dash2/bin/TreeCluster.py -i {treefile} -o {outfile} -t {threshold}'
    print(cmd)
    return os.system(cmd)

def deduplicate(seq_fa,out_fa):
    seq_dict = {}
    name_dict = {}
    seq2seqno = {}
    with open(out_fa,'w') as outpf:
        with open(seq_fa,'r') as inpf:
            seq = ''
            seqname = ''
            seq_no = 0
            for line in inpf:
                line = line.strip()
                if line[0]=='>':
                    if seq != '' and seqname != '':
                        if seq not in seq2seqno:
                            seq_no += 1
                            seq_dict[f'seq-{seq_no}'] = seq
                            name_dict[f'seq-{seq_no}'] = [seqname]
                            outpf.write(f'>seq-{seq_no}\n')
                            outpf.write(f'{seq}\n')
                            seq2seqno[seq] = f'seq-{seq_no}'
                        else:
                            name_dict[f'seq-{seq_no}'].append(seqname)

                    seq = ''
                    seqname = line[1:]
                else:
                    seq += line
            if seq != '' and seqname != '':
                if seq not in seq2seqno:
                    seq_no += 1
                    seq_dict[f'seq-{seq_no}'] = seq
                    name_dict[f'seq-{seq_no}'] = [seqname]
                    outpf.write(f'>seq-{seq_no}\n')
                    outpf.write(f'{seq}\n')
                    seq2seqno[seq] = f'seq-{seq_no}'
                else:
                    name_dict[f'seq-{seq_no}'].append(seqname)
    del seq2seqno 
    return name_dict, seq_dict


