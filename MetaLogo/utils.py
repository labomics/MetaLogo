#!/usr/bin/env python
import os
import uuid
import numpy as np
import numpy as np
import re

from matplotlib import pyplot as plt
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
                    seqname = f'{line[1:]} {ith}'
                    seqnames.append(seqname)
                else:
                    seq_dict[seqname]  = seq_dict.get(seqname,'') + line.upper()
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
                    seq_dict[seqname] = line.upper()
    else:
        pass

    return [[seqname,seq_dict[seqname]]  for seqname in seqnames if (len(seq_dict[seqname])>=min_length) and (len(seq_dict[seqname])<=max_length)]

def grouping(seqs,group_by='length'):

    groups_dict = {}
    if group_by.lower() == 'length':
        for name,seq in seqs:
            key = f'Len{len(seq)}'
            if key not in groups_dict:
                groups_dict[key] = []
            groups_dict[key].append([name,seq])
    if group_by.lower() == 'identifier':
        for name,seq in seqs:
            group_pat = re.search('group@\d+-\S+',name)
            if group_pat:
                group_id = group_pat.group()
                if group_id not in groups_dict:
                    groups_dict[group_id] = []
                groups_dict[group_id].append([name,seq])
    return groups_dict

def check_group(groups):
    for group_id in groups:
        seqs = groups[group_id]
        if len(set([len(x[1]) for x in seqs])) > 1:
            print('Sequence lengths not same in one group')
            exit(0)

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


def angle_between(p1, p2=(0,0)):
    ang1 = np.arctan2(*p1[::-1])
    ang2 = np.arctan2(*p2[::-1])
    return (ang1 - ang2) % (2 * np.pi)

def get_coor_by_angle(radius, angle, origin=(0,0)):
    relative_coor =  (radius * np.cos(angle), radius * np.sin(angle))
    return (relative_coor[0]+origin[0],relative_coor[1]+origin[1])


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

def link_edges(edge1, edge2, ax, threed=False,x=0,y=1,z=-1, color='blue',alpha=0.1):
    if ax is None:
        _, ax = plt.subplots(1, 1,figsize=(10,10))
    
    
    p1,p2 = edge1
    p4,p3 = edge2

    if threed:
        patch = straight_connect((p1[x],p1[y]),
                                 (p2[x],p2[y]),
                                 (p3[x],p3[y]),
                                 (p4[x],p4[y]), fill=True,alpha=alpha,color=color,linewidth=0)

    else:
        patch = straight_connect(p1,p2,p3,p4, fill=True,alpha=alpha,color=color,linewidth=0)


    ax.add_patch(patch)
    if threed:
        art3d.pathpatch_2d_to_3d(patch, z=0, zdir='z')

    return ax


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

def detect_seq_type(seqs):
    

    dna_set = {'A','T','G','C','N','-'}
    rna_set = {'A','U','G','C','N','-'}
    protein_set = {'A','R','N','D','C','Q','E','G','H','I','L','K','M','F','P','S','T','W','Y','V','-'}

    base_set = set()
    for _,seq in seqs:
        base_set |= set(seq)


    seq_type = 'aa'
    if base_set.issubset(dna_set):
        seq_type = 'dna' 
    elif base_set.issubset(rna_set):
        seq_type = 'rna' 
    elif base_set.issubset(protein_set):
        seq_type = 'aa' 
    
    return seq_type
    
