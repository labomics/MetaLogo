#!/usr/bin/env python
import base64
import os

def save_seqs(seqs, filename):
    with open(filename,'w') as outpf:
        for seqname,seq in seqs:
            outpf.write(f'>{seqname}\n')
            outpf.write(f'{seq}\n')

def handle_seqs_file(content,format="fasta",sequence_type="dna"):
    print('enter handle seqs')
    try:
        data = content.split(";base64,")[1]
        data = base64.b64decode(data).decode('utf-8')
        return handle_seqs_str(data,format,sequence_type)
    except Exception as e:
        return {'successful':False, 'msg':f'File processing error: {e}'}

def handle_seqs_str(content, format="fasta", sequence_type="dna"):
    seqs = []
    msg = ''
    successful = True
    if format.lower() == 'fasta':
        seq_name = ''
        seq = ''
        i = -1
        for line in content.split('\n'):
            line = line.strip()
            if len(line) == 0:
                continue
            i += 1
            if i == 0 and line[0] != '>':
                successful = False
                msg = 'Fasta format error, please check!'
                break

            if line[0] == '>':
                if len(seq_name) > 0: 
                        if len(seq) > 0:
                            seqs.append([seq_name,seq.upper()])
                        else:
                            successful = False
                            msg = 'Fasta format error, please check!'
                            break

                seq_name = line[1:]
                seq = ''
            else:
                seq += line
        if len(seq_name) > 0: 
                if len(seq) > 0:
                    seqs.append([seq_name,seq.upper()])
                else:
                    successful = False
                    msg = 'Fastq format error, please check!'

    elif format.lower() == 'fastq':
        seq_name = ''
        seq = ''
        i = -1
        for line in content.split('\n'):
            line = line.strip()
            if len(line) == 0:
                continue
            i += 1
            if i%4 == 0:
                if line[0] != '@':
                    successful = False
                    msg = 'Fastq format error, please check!'
                    break
                seq_name = line[1:]
            if i%4 == 1:
                seq = line
                seqs.append([seq_name,seq.upper()])
    
    if successful:
        if len(seqs) == 0:
            successful = False
            msg = 'No sequences parsed, please check!'

    base_err = False 
    base_set = set()

    dna_set = {'A','T','G','C','N','-'}
    rna_set = {'A','U','G','C','N','-'}
    protein_set = {'A','R','N','D','C','Q','E','G','H','I','L','K','M','F','P','S','T','W','Y','V','-'}

    for seqname,seq in seqs:
        base_set |= set(seq)

    if sequence_type.upper()  == 'DNA':
        if not base_set.issubset(dna_set):
            base_err = True
    elif sequence_type.upper()  == 'AA':
        if not base_set.issubset(protein_set):
            base_err = True
    elif sequence_type.upper()  == 'RNA':
        if not base_set.issubset(rna_set):
            base_err = True
    if base_err:
        return {'successful':False, 'msg':f'{sequence_type} sequences not valid, please check', 'res': {'seqs':seqs}}

    is_dna = False
    is_rna = False
    is_protein = False

    if sequence_type.upper() == 'AUTO':
       if base_set.issubset(dna_set):
           is_dna = True
       if base_set.issubset(rna_set):
           is_rna = True
       elif base_set.issubset(protein_set):
           is_protein = True
    
    if (sequence_type.upper() == 'AUTO') and (not is_dna) and (not is_protein) and (not is_rna) :
        return {'successful':False, 'msg':f'Unclear sequence type (DNA or Protein), please check', 'res': {'seqs':seqs}}
    
    if len(seqs) == 0:
        return {'successful':False, 'msg':f'No sequences parsed, please check', 'res': {'seqs':seqs}}

    if sequence_type.upper() == 'AUTO':
        if is_dna:
            sequence_type = 'dna'
        elif is_rna:
            sequence_type = 'rna'
        elif is_protein:
            sequence_type = 'aa'
    return {'successful':successful, 'msg':msg, 'res': {'seqs':seqs,'sequence_type':sequence_type}}
            

            
    