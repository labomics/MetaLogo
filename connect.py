#!/usr/bin/python
from scipy.stats import spearmanr,pearsonr
import numpy as np

def get_connect(bits_array, align_metric = 'sort_diff'):
    print('len of bits: ', len(bits_array))
    connected = {}
    for index,bit in enumerate(bits_array):
        if index == len(bits_array) - 1:
            break
        bits1 = bit
        bits2 = bits_array[index + 1]
        align1,align2 = needle(bits1,bits2, align_metric=align_metric)

        connected[index] = {}

        for pos1, pos2 in zip(align1,align2):
            if pos1 == '-' or pos2 == '-':
                continue
            score = match_score(bits1[pos1],bits2[pos2], align_metric=align_metric)
            connected[index][pos1] = [score, [pos2]]
    return connected

def match_score(bit1, bit2, align_metric='sort_consistency'):

    if align_metric == 'diff':
        bit1 = dict(bit1)
        bit2 = dict(bit2)
        keys = sorted(list(bit1.keys()|bit2.keys()))
        err = 0
        for key in keys:
            err += abs(bit1.get(key,0) - bit2.get(key,0))
        return 1-err
    if align_metric == 'sort_consistency':
        bit1 = sorted(bit1, key=lambda d:d[1],reverse=True)
        bit2 = sorted(bit2, key=lambda d:d[1],reverse=True)
        score = 0
        for i in range(min(len(bit1),len(bit2))):
            if bit1[i][0] == bit2[i][0]:
                #score += (bit1[i][1] + bit2[i][1])/2
                score += np.sqrt(bit1[i][1] * bit2[i][1])
        return score
    if align_metric == 'correlation':

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
def needle(seq1, seq2, gap_penalty=-1,delete=-1,insert=-1, align_metric='sort_consistency'):
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
            match = score[i - 1][j - 1] + match_score(seq1[i-1], seq2[j-1],align_metric=align_metric)
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

        if score_current == score_diagonal + match_score(seq1[i-1], seq2[j-1],align_metric=align_metric):
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
