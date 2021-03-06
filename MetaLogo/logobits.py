#!/usr/bin/env python
import numpy as np

def compute_prob(groups,threshold=0):
    counts = {}
    for gid,group in groups.items():
        _counts = {}
        for name,seq in group:
            for i in range(len(seq)):
                if i not in _counts:
                    _counts[i] = {}
                #if seq[i] == '-':
                #    continue
                _counts[i][seq[i]] = _counts[i].get(seq[i],0) + 1
        counts[gid] = _counts
    
    probs = {}
    for gid,_counts in counts.items():
        _probs = []
        for i in range(len(_counts)):
            #total = sum(_counts[i].values())
            total = sum(_counts.get(i,{}).values())
            _ps = []
            #for base in sorted(_counts[i].keys()):
            for base in sorted(_counts.get(i,{}).keys()):
                ration = _counts[i][base]/total
                if ration < threshold:
                    continue
                _ps.append([base,ration])
            _probs.append(_ps)
        
        probs[gid] = _probs
    
    return probs
    
def compute_bits(groups, probs, seq_type='dna',no_correction=False):
    bits = {}
    for gid,prob in probs.items():
        if seq_type.lower() in ['dna','rna']:
            if no_correction:
                e = np.log2(4) 
            else:
                e = np.log2(4) - (4-1)/(np.log(2)*2*len(groups[gid]))
        elif seq_type.lower() == 'aa':
            if no_correction:
                e = np.log2(20)
            else:
                e = np.log2(20) - (20-1)/(np.log(2)*2*len(groups[gid]))
        bit = [] 
        for i in range(len(prob)):
            h = 0
            for base,p in prob[i]:
                #if base == '-':
                #    continue
                h -= p*np.log2(p) 
            _bit = [] 
            for base,p in prob[i]:
                if base == '-':
                    continue
                height = max(p * (e - h),0)
                _bit.append((base,height))
            bit.append(_bit)
        bits[gid] = bit 
    
    return bits
        
        