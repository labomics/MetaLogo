#!/usr/bin/env python
from numpy.core.fromnumeric import product
from scipy.stats import spearmanr,pearsonr
import numpy as np
from scipy.spatial import distance
import math

def dotproduct(v1, v2):
    return sum((a*b) for a, b in zip(v1, v2))
def length(v):
    return math.sqrt(dotproduct(v, v))
def costheta(v1, v2):
    return dotproduct(v1, v2) / (length(v1) * length(v2))

def get_score_mat(bits_array, align_metric = 'sort_consistency',  gap_score=-1, seq_type='dna'):
    scores_mat = {}
    for i in range(len(bits_array)):
        for j in range(len(bits_array)):
            if i >= j:
                continue
            bits1 = bits_array[i]
            bits2 = bits_array[j]
            align1,align2 = needle(bits1,bits2, align_metric=align_metric, 
                                    gap_penalty=gap_score, seq_type=seq_type)
            score = 0
            for pos1, pos2 in zip(align1,align2):
                if pos1 == '-' or pos2 == '-':
                    score += gap_score
                else:
                    score += match_score(bits1[pos1],bits2[pos2], align_metric=align_metric,seq_type=seq_type)

            if i not in scores_mat:
                scores_mat[i] = {}
            scores_mat[i][j] = score/len(align1)
    return scores_mat

def msa(bits_array, scores_mat, align_metric = 'sort_consistency', gap_score=-1, seq_type='dna'):

    #find the nearest couple
    max_score = max([max(scores_mat[x].values()) for x in scores_mat])
    findij = False
    for i in scores_mat:
        for j in scores_mat[i]:
            #if abs(scores_mat[i][j] - max_score) < 0.00001:
            if scores_mat[i][j] == max_score:
                findij = True
                break
        if findij:
            break
    #align the first two
    align1,align2 = needle(bits_array[i],bits_array[j], align_metric=align_metric, 
                              gap_penalty=gap_score, seq_type=seq_type)
    #print(align1)#test
    #print(align2)#test
    
    pools = [i,j]
    new_bits_array = []
    new_bits_array.append([bits_array[i][pos] if pos!= '-' else [] for pos in align1])
    new_bits_array.append([bits_array[j][pos] if pos!= '-' else [] for pos in align2])
    repeat = 0
    while len(pools) < len(bits_array):
        repeat += 1
        if repeat > len(bits_array) + 1:
            break
        left = set(range(len(bits_array))) - set(pools)
        max_score = -1E9
        max_i= -1
        max_j = -1

        for i in pools:
            for j in left:
                score = scores_mat[min(i,j)][max(i,j)]
                if score > max_score:
                    max_score = score
                    max_i = i
                    max_j = j
        #
        bits1 = new_bits_array[pools.index(max_i)]
        bits2 = bits_array[max_j]
        align1,align2 = needle(bits1,bits2, align_metric=align_metric, 
                              gap_penalty=gap_score, seq_type=seq_type)
        
        for i in range(len(new_bits_array)):
            _arr = []
            for pos in align1:
                if pos == '-':
                    _arr.append([])
                else:
                    _arr.append(new_bits_array[i][pos])
            new_bits_array[i] = _arr

        new_bits_array.append([bits2[pos] if pos!= '-' else [] for pos in align2]) 
        pools.append(max_j)
    
    sorted_bits_array = []
    for i in range(len(pools)):
        sorted_bits_array.append(new_bits_array[pools.index(i)])
    
    return sorted_bits_array



def get_connect(bits_array, align_metric = 'sort_consistency', gap_score=-1, msa_input=False, seq_type='dna'):
    connected = {}
    for index,bit in enumerate(bits_array):
        if index == len(bits_array) - 1:
            break
        bits1 = bit
        bits2 = bits_array[index + 1]
        if msa_input:
            align1 = list(range(len(bits1)))
            align2 = list(range(len(bits2)))
        else:
            align1,align2 = needle(bits1,bits2, align_metric=align_metric, 
                                gap_penalty=gap_score,seq_type=seq_type)
        connected[index] = {}

        for pos1, pos2 in zip(align1,align2):
            if pos1 == '-' or pos2 == '-':
                continue
            score = match_score(bits1[pos1],bits2[pos2], align_metric=align_metric, seq_type = seq_type)
            connected[index][pos1] = [score, [pos2]]
    return connected

max_entropy_aa = -sum([(1/20)*np.log(1/20) for i in range(20)])
max_entropy_dna = -sum([(1/4)*np.log(1/4) for i in range(4)])

def match_score(bit1, bit2, align_metric='sort_consistency',gap_score=-1,seq_type='dna'):

    try:

        if len(bit1) == 0 or len(bit2) == 0:
            return 0

        if align_metric not in ['dot_product','sort_consistency','js_divergence','cosine','entropy_bhattacharyya']:
            align_metric = 'dot_product'
        
        if align_metric == 'entropy_bhattacharyya':
            bit1 = dict(bit1)
            bit2 = dict(bit2)
            keys = sorted(list(bit1.keys()|bit2.keys()))
            v1 = [bit1.get(key,0) for key in keys]
            v2 = [bit2.get(key,0) for key in keys]
            bc = sum([np.sqrt(i1*i2) for i1,i2 in zip(v1,v2)])
            max_entropy = 0
            if seq_type.lower() in  ['protein','aa']:
                max_entropy = max_entropy_aa
            if seq_type.lower() in  ['dna','rna']:
                max_entropy = max_entropy_dna
            entropy1 = -sum([bit1.get(key,0)*np.log(bit1.get(key,0)) for key in keys if bit1.get(key,0) > 0])
            entropy2 = -sum([bit2.get(key,0)*np.log(bit2.get(key,0)) for key in keys if bit2.get(key,0) > 0])
            res = bc * np.sqrt((1 - (entropy1/max_entropy)) * (1 - (entropy2/max_entropy)))

            return res


        if align_metric == 'dot_product':
            bit1 = dict(bit1)
            bit2 = dict(bit2)
            keys = sorted(list(bit1.keys()|bit2.keys()))
            v1 = [bit1.get(key,0) for key in keys]
            v2 = [bit2.get(key,0) for key in keys]
            val = dotproduct(v1,v2)
            return val

        if align_metric == 'cosine':
            bit1 = dict(bit1)
            bit2 = dict(bit2)
            keys = sorted(list(bit1.keys()|bit2.keys()))
            v1 = [bit1.get(key,0) for key in keys]
            v2 = [bit2.get(key,0) for key in keys]
            if length(v1)*length(v2)==0:
                return 0
            return costheta(v1,v2)

        if align_metric == 'sort_consistency':
            bit1 = sorted(bit1, key=lambda d:d[1],reverse=True)
            bit2 = sorted(bit2, key=lambda d:d[1],reverse=True)
            score = 0
            for i in range(min(len(bit1),len(bit2))):
                if bit1[i][0] == bit2[i][0]:
                    score += bit1[i][1] * bit2[i][1]
            return score
    
        if align_metric =='js_divergence': #noted, here must input probabilites rather than bits.
            q1 = []
            q2 = []
            bit1 = dict(bit1)
            bit2 = dict(bit2)
            keys = sorted(list(bit1.keys()|bit2.keys()))
            for key in keys:
                q1.append(bit1.get(key,0))
                q2.append(bit2.get(key,0))
            if sum(q1)*sum(q2) == 0:
                return 0
            return 1-distance.jensenshannon(q1,q2)

    except Exception as e:
        print('exception: ', e)
        return 0


#https://github.com/alevchuk/pairwise-alignment-in-python/blob/master/alignment.py
def needle(seq1, seq2, gap_penalty=-1, align_metric='sort_consistency',seq_type='dna'):
    m, n = len(seq1), len(seq2)  # length of two sequences
    
    # Generate DP table and traceback path pointer matrix
    score = np.zeros((m+1, n+1))      # the DP table
   
    # Calculate DP table
    for i in range(0, m + 1):
        score[i][0] = gap_penalty * i
    for j in range(0, n + 1):
        score[0][j] = gap_penalty * j
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            match = score[i - 1][j - 1] + match_score(seq1[i-1], seq2[j-1],align_metric=align_metric,seq_type=seq_type)
            delete = score[i - 1][j] + gap_penalty
            insert = score[i][j - 1] + gap_penalty
            score[i][j] = max(match, delete, insert)


    # Traceback and compute the alignment 
    align1, align2 = [], [] 
    i,j = m,n # start from the bottom right cell
    repeat = 0
    while i > 0 and j > 0: # end toching the top or the left edge
        repeat += 1
        if repeat > (m+1) * (n*1):
            break 
        score_current = score[i][j]
        score_diagonal = score[i-1][j-1]
        score_up = score[i][j-1]
        score_left = score[i-1][j]

        #print('seq1[i-1]:', seq1[i-1])
        #print('seq2[j-1]:', seq1[j-1])

        if score_current == score_diagonal + match_score(seq1[i-1], seq2[j-1],align_metric=align_metric,seq_type=seq_type):
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
        else:
            break

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
