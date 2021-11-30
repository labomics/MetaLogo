#!/usr/bin/env python
from collections import namedtuple
import os
import uuid
import pandas as pd
import re
import dendropy
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns
from Bio import Phylo
from ete3 import Tree

def get_distance_range(tree_file):
    tree = dendropy.Tree.get(path=tree_file,schema='newick')
    pdc = tree.phylogenetic_distance_matrix()
    dists = pdc.distances()
    return dists

def get_distance_range_lessmem(tree_file):
    tree = Tree(tree_file)
    dists = []
    for node in tree:
        dists.append(node.get_farthest_node()[1])
    return dists


def get_score_df(score_f):
    arrs = []
    with open(score_f,'r') as inpf:
        for line in inpf:
            line = line.strip()
            if len(line) == 0:
                continue
            if line[0] == '#':
                continue
            _arrs = re.split(' +',line)
            arrs.append(_arrs[:3])
    if len(arrs) == 0:
        return None
    df = pd.DataFrame(arrs,columns = ['POS','SEQ','SCORE'])
    df['SCORE'] = df['SCORE'].map(float)
    df['BASE'] = df['POS'] + '-' + df['SEQ']
    return df

def drawdists(dists,output):
    fig,ax = plt.subplots()
    df = pd.DataFrame({'Pairwise distance':list(dists)})
    g = sns.histplot(df,x='Pairwise distance',kde=True,ax=ax)
    fig.savefig(output,bbox_inches='tight')
    return

def drawtree(input,output):
    tree = Phylo.read(input, 'newick')
    tree.ladderize()  # Flip branches so deeper clades are displayed at top

    matplotlib.rc('font', size=10)
    fig = plt.figure(figsize=(20, 20), dpi=100)
    axes = fig.add_subplot(1, 1, 1)
    Phylo.draw(tree, axes=axes)
    plt.savefig(output, dpi=100)


def reverse_msa_seqname(name_dict,oldfile,newfile):

    with open(newfile,'w') as outpf:
        seqname = ''
        seq = ''
        with open(oldfile,'r') as inpf:
            for line in inpf:
                line = line.strip()
                if len(line) == 0:
                    continue
                if line[0] == '>':
                    if seqname != '' and seq != '':
                        for alias in name_dict.get(seqname,[]):
                            outpf.write(f'>{alias}\n')
                            outpf.write(f'{seq}\n')
                    seqname = line[1:]
                    seq = ''
                else:
                    seq += line

            if seqname != '' and seq != '':
               for alias in name_dict.get(seqname,[]):
                   outpf.write(f'>{alias}\n')
                   outpf.write(f'{seq}\n')
    return None

def reverse_tree_seqname(name_dict,oldtreefile,newtreefile):
    tree = dendropy.Tree.get(path=oldtreefile,schema='newick')
    for node in tree:
        if node.is_leaf():
            if node.taxon is not None:
                if len(name_dict.get(node.taxon.label,[])) > 0 :
                    node.taxon.label = name_dict.get(node.taxon.label,[])[0]
    tree.write(path=newtreefile,schema='newick')
    return None

def save_group_seqs(group_dict,outfa):
    with open(outfa,'w') as outpf:
        outpf.write('Sequence name\tGroup_id\n')
        for grpid in group_dict:
            for seqname,seq in group_dict[grpid]:
                outpf.write(f'{seqname} \t {grpid} \n')

def save_seqs(seqs, filename):
    with open(filename,'w') as outpf:
        for seqname,seq in seqs:
            outpf.write(f'>{seqname}\n')
            outpf.write(f'{seq}\n') 

def auto_detect_groups(seqs, seq_fa, sequence_type='aa',group_resolution=1,clustering_method='max', 
                       clustalo_bin='',fasttree_bin='',fasttreemp_bin='',treecluster_bin='',
                       uid='', fa_output_dir='', figure_output_dir=''):
    
    if seq_fa == '':
        if uid == '':
            uid = str(uuid.uuid4())
        seq_fa = f'{fa_output_dir}/server.{uid}.fa'

    if not os.path.exists(seq_fa): 
        save_seqs(seqs, seq_fa)

    dep_seq_fa = f'{fa_output_dir}/server.{uid}.dep.fa'
    name_dict, seq_dict = deduplicate(seq_fa,dep_seq_fa)

    msa_dict = msa(dep_seq_fa,f'{fa_output_dir}/server.{uid}.msa.fa',clustalo_bin)

    if len(seqs) > 1000:
        fasttree(f'{fa_output_dir}/server.{uid}.msa.fa',
                f'{fa_output_dir}/server.{uid}.fasttree.tree',
                fasttreemp_bin,sequence_type)
    else:
        fasttree(f'{fa_output_dir}/server.{uid}.msa.fa',
                f'{fa_output_dir}/server.{uid}.fasttree.tree',
                fasttree_bin,sequence_type)
    try:
        if os.path.exists(f'{fa_output_dir}/server.{uid}.treedists.csv'):
            dists = pd.read_csv(f'{fa_output_dir}/server.{uid}.treedists.csv',index_col=False,header=0)['0'].tolist()
        else: 
            if len(seqs) > 1000:
                dists = get_distance_range_lessmem(f'{fa_output_dir}/server.{uid}.fasttree.tree')
            else:
                dists = get_distance_range(f'{fa_output_dir}/server.{uid}.fasttree.tree')
            pd.Series(list(dists)).to_csv(f'{fa_output_dir}/server.{uid}.treedists.csv',index=None)
    except:
        dists = get_distance_range_lessmem(f'{fa_output_dir}/server.{uid}.fasttree.tree')

    
    treecluster(group_resolution,clustering_method,dists,f'{fa_output_dir}/server.{uid}.fasttree.tree',f'{fa_output_dir}/server.{uid}.fasttree.cluster',treecluster_bin)

    reverse_msa_seqname(name_dict,f'{fa_output_dir}/server.{uid}.msa.fa',f'{fa_output_dir}/server.{uid}.msa.rawid.fa')
    reverse_tree_seqname(name_dict,f'{fa_output_dir}/server.{uid}.fasttree.tree',f'{fa_output_dir}/server.{uid}.fasttree.rawid.tree')

    drawdists(dists,f'{figure_output_dir}/{uid}.treedistances.png')
    drawtree(f'{fa_output_dir}/server.{uid}.fasttree.rawid.tree',f'{figure_output_dir}/{uid}.tree.png')

    cluster_df = pd.read_csv(f'{fa_output_dir}/server.{uid}.fasttree.cluster',sep='\t')
    groups_dict = {}
    for index, grp in cluster_df.groupby('ClusterNumber'):
        #if str(index) == '-1':
        #    continue
        groups_dict[index] = []
        for seqname in grp['SequenceName']:
            for _seqname in name_dict[seqname]:
                groups_dict[index].append([_seqname,msa_dict[seqname]])
    save_group_seqs(groups_dict,f'{fa_output_dir}/server.{uid}.grouping.fa')
        
    return groups_dict

def msa(seq_fa,outfile,clustalo_bin):
    if not os.path.exists(outfile):
        cmd = f'{clustalo_bin} --auto -i {seq_fa} -o {outfile}'
        os.system(f'{clustalo_bin} --auto -i {seq_fa} -o {outfile}')
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

def fasttree(msa_fa,outfile_tree,fasttree_bin='',sequence_type='aa'):
    if (not os.path.exists(outfile_tree)):
        if sequence_type != 'aa':
            cmd = f'{fasttree_bin} -nt  -quiet -nopr {msa_fa} > {outfile_tree} '
        else:
            cmd = f'{fasttree_bin}  -quiet -nopr {msa_fa} > {outfile_tree} '
        return os.system(cmd)
    return -1

def treecluster(threshold,clustering_method,dists,treefile,outfile,treecluster_bin=''):
    if threshold == 0:
        adj_threshold = threshold
    else:
        sorted_dists = sorted(dists)
        adj_threshold_idx = round(threshold*len(dists))
        adj_threshold = sorted_dists[min(len(dists)-1,adj_threshold_idx)]
    cmd = f'{treecluster_bin} -i {treefile} -o {outfile} -t {adj_threshold} -m {clustering_method}'
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
                    seq += line.upper()
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


