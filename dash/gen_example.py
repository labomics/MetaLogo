#!/usr/bin/python
import random
if __name__ == '__main__':
    n = 10
    lens = [12,13,14,15,16,17]

    point = 4
    seqs = []
    for ln in lens:
        for c in range(n):
            seq = ''
            name = f'>seq{c} group@{ln}-tmp'
            if ln == 14:
                name = random.choice([f'>seq{c} group@{ln}-tmp',f'>seq{c} group@{ln}-2-tmp'])
            targets =  [3,9,14,15]
            table = {3:'ATGC',9:'TCGA',14:'CAGT',15:'AGCT'}
            for i in range(ln):
                if i in targets:
                    seq += random.choices(table[i],weights=[0.7,0.2,0.1,0.1],k=1)[0]
                else:
                    seq += random.choice('ATGC')
            seqs.append([name,seq])
    
    with open('example2.fa','w') as outpf:
        for name,seq in seqs:
            outpf.write(f'{name}\n')
            outpf.write(f'{seq}\n')


