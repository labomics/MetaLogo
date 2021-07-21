#!/usr/bin/python
from numpy.lib.function_base import delete
from .format_utils import process_data
import tempfile
import os
import uuid
import numpy as np
from scipy.stats import spearmanr,pearsonr
from matplotlib import pyplot as plt
import numpy as np

from matplotlib.patches import PathPatch,Rectangle,Circle,Polygon
from matplotlib.path import Path
import mpl_toolkits.mplot3d.art3d as art3d
from matplotlib.text import TextPath
from matplotlib.transforms import Affine2D




def read_file(filename, filetype, min_length, max_length):

    seq_dict = {}
    seqnames = []
    seqname = None
    seq = None
    ith = 0
    if filetype.lower() in ['fasta','fa']:
        with open(filename,'r') as inpf:
            for line in inpf:
                line = line.strip()
                if line[0] == '>':
                    ith += 1
                    seqname = f'{line[1:]}-{ith}'
                    seqnames.append(seqname)
                else:
                    seq_dict[seqname]  = seq_dict.get(seqname,'') + line
    elif filetype.lower() == ['fastq','fq']:
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
    if group_by.lower() == 'length':
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

def get_connect(bits_array, p_threshold = 0.05):
    print('len of bits: ', len(bits_array))
    connected = {}
    for index,bit in enumerate(bits_array):
        if index == len(bits_array) - 1:
            break
        bits1 = bit
        bits2 = bits_array[index + 1]
        align1,align2 = needle(bits1,bits2)

        connected[index] = {}

        for pos1, pos2 in zip(align1,align2):
            if pos1 == '-' or pos2 == '-':
                continue
            score = match_score(bits1[pos1],bits2[pos2])
            connected[index][pos1] = [score, [pos2]]
    return connected


def check_parallel(edge1, edge2):
    start1, end1 = edge1
    start2, end2 = edge2
    shifted_end1 = (end1[0]-start1[0], end1[1]-start1[1])
    shifted_end2 = (end2[0]-start2[0], end2[1]-start2[1])

def curve_connect(leftbot,lefttop,righttop,rightbot,limit_width,direction='right',**kargs):
    if np.abs((leftbot[0] - lefttop[0])/limit_width)< 0.1:
        return Polygon(xy=[leftbot,lefttop,righttop,rightbot], **kargs)
    else:
        if direction == 'left':
            limit_width = -limit_width
        p0 = leftbot
        p1 = (leftbot[0] + limit_width, leftbot[1])
        p2 = (lefttop[0] + limit_width, lefttop[1])
        p3 = lefttop
        p4 = righttop
        p5 = (righttop[0] + limit_width,righttop[1])
        p6 = (rightbot[0] + limit_width, rightbot[1])
        p7 = rightbot
        p8 = p0

        verts = [p0,p1,p2,p3,p4,p5,p6,p7,p8]

        codes = [
            Path.MOVETO,
            Path.CURVE4,
            Path.CURVE4,
            Path.CURVE4,
            Path.LINETO,
            Path.CURVE4,
            Path.CURVE4,
            Path.CURVE4,
            Path.CLOSEPOLY
        ]
        path = Path(verts, codes)
        patch = PathPatch(path, **kargs)
        return patch

def straight_connect(p1,p2,p3,p4,**kargs):
    verts = [p1,p2,p3,p4,p1]
    codes = [
        Path.MOVETO,
        Path.LINETO,
        Path.LINETO,
        Path.LINETO,
        Path.CLOSEPOLY
    ]
    path = Path(verts, codes)
    patch = PathPatch(path, **kargs)
    return patch

def link_edges(edge1, edge2, ax, threed=False,x=0,y=1,z=-1):
    if ax is None:
        _, ax = plt.subplots(1, 1,figsize=(10,10))
    
    print('in link edges')
    print('edge1: ', edge1)
    print('edge2: ', edge2)
    
    p1,p2 = edge1
    p4,p3 = edge2

    #ax.scatter(p1[0],p1[1])
    #ax.scatter(p2[0],p2[1])
    #ax.scatter(p3[0],p3[1])
    #ax.scatter(p4[0],p4[1])
    if threed:
        patch = straight_connect((p1[x],p1[y]),
                                 (p2[x],p2[y]),
                                 (p3[x],p3[y]),
                                 (p4[x],p4[y]), fill=True,alpha=0.1,color='blue',linewidth=0)

    else:
        patch = straight_connect(p1,p2,p3,p4, fill=True,alpha=0.1,color='blue',linewidth=0)


    ax.add_patch(patch)
    if threed:
        art3d.pathpatch_2d_to_3d(patch, z=0, zdir='z')

    return ax


def match_score(bit1, bit2, algrithm='sort_diff'):

    if algrithm == 'error':
        bit1 = dict(bit1)
        bit2 = dict(bit2)
        keys = sorted(list(bit1.keys()|bit2.keys()))
        err = 0
        for key in keys:
            err += abs(bit1.get(key,0) - bit2.get(key,0))
        return 1-err
    if algrithm == 'sort_diff':
        bit1 = sorted(bit1, key=lambda d:d[1],reverse=True)
        bit2 = sorted(bit2, key=lambda d:d[1],reverse=True)
        score = 0
        for i in range(min(len(bit1),len(bit2))):
            if bit1[i][0] == bit2[i][0]:
                #score += (bit1[i][1] + bit2[i][1])/2
                score += np.sqrt(bit1[i][1] * bit2[i][1])
        return score
    if algrithm == 'correlation':

        bit1 = dict(bit1)
        bit2 = dict(bit2)
        keys = sorted(list(bit1.keys()|bit2.keys()))
        a1 = []
        a2 = []
        for i in range(len(keys)):
            v1 = bit1.get(keys[i],0)
            v2 = bit2.get(keys[i],0)
            #if v1 < 0.01:
            #    v1 = 0
            #if v2 < 0.01:
            #    v2 = 0
            if v1 == v2 == 0:
                continue
            a1.append(v1)
            a2.append(v2)
        
        coor,pval = pearsonr(a1,a2)
        if pval > 0.05:
            corr = 0
        #print(a1,a2,coor)
        return coor






    



#https://github.com/alevchuk/pairwise-alignment-in-python/blob/master/alignment.py
def needle(seq1, seq2, gap_penalty=-1,delete=-1,insert=-1):
    m, n = len(seq1), len(seq2)  # length of two sequences
    
    # Generate DP table and traceback path pointer matrix
    score = np.zeros((m+1, n+1))      # the DP table
   
    # Calculate DP table
    for i in range(0, m + 1):
        score[i][0] = gap_penalty * i
    for j in range(0, n + 1):
        score[0][j] = gap_penalty * j
    #print(score)
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            match = score[i - 1][j - 1] + match_score(seq1[i-1], seq2[j-1])
            delete = score[i - 1][j] + gap_penalty
            insert = score[i][j - 1] + gap_penalty
            score[i][j] = max(match, delete, insert)

    # Traceback and compute the alignment 
    align1, align2 = [], [] 
    i,j = m,n # start from the bottom right cell
    while i > 0 and j > 0: # end toching the top or the left edge
        score_current = score[i][j]
        score_diagonal = score[i-1][j-1]
        score_up = score[i][j-1]
        score_left = score[i-1][j]

        #print('seq1[i-1]:', seq1[i-1])
        #print('seq2[j-1]:', seq1[j-1])

        if score_current == score_diagonal + match_score(seq1[i-1], seq2[j-1]):
            align1.append(i-1)
            align2.append(j-1)
            i -= 1
            j -= 1
        elif score_current == score_left + gap_penalty:
            align1.append(i-1)
            align2.append('-')
            i -= 1
        elif score_current == score_up + gap_penalty:
            align1.append('-')
            align2.append(j-1)
            j -= 1

    # Finish tracing up to the top left cell
    while i > 0:
        align1.append(i-1)
        align2.append('-')
        i -= 1
    while j > 0:
        align1.append('-')
        align2.append(j-1)
        j -= 1
    #print('align1:',  align1)
    #print('align2: ', align2)
    return align1[::-1],align2[::-1]


#https://stackoverflow.com/questions/34372480/rotate-point-about-another-point-in-degrees-python/34374437
def rotate(p, origin=(0, 0), angle=0):
    R = np.array([[np.cos(angle), -np.sin(angle)],
                  [np.sin(angle),  np.cos(angle)]])
    o = np.atleast_2d(origin)
    p = np.atleast_2d(p)
    return np.squeeze((R @ (p.T-o.T) + o.T).T)



#https://matplotlib.org/stable/gallery/mplot3d/pathpatch3d.html#sphx-glr-gallery-mplot3d-pathpatch3d-py
def text3d(ax, xyz, s, zdir="z", size=None, angle=0, usetex=False, **kwargs):
    """
    Plots the string *s* on the axes *ax*, with position *xyz*, size *size*,
    and rotation angle *angle*. *zdir* gives the axis which is to be treated as
    the third dimension. *usetex* is a boolean indicating whether the string
    should be run through a LaTeX subprocess or not.  Any additional keyword
    arguments are forwarded to `.transform_path`.

    Note: zdir affects the interpretation of xyz.
    """
    x, y, z = xyz
    if zdir == "y":
        xy1, z1 = (x, z), y
    elif zdir == "x":
        xy1, z1 = (y, z), x
    else:
        xy1, z1 = (x, y), z

    text_path = TextPath((0, 0), s, size=size, usetex=usetex)
    trans = Affine2D().rotate(angle).translate(xy1[0], xy1[1])

    p1 = PathPatch(trans.transform_path(text_path), **kwargs)
    ax.add_patch(p1)
    art3d.pathpatch_2d_to_3d(p1, z=z1, zdir=zdir)
