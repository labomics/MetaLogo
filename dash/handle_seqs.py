#!/usr/bin/python
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
        print('content: ',content)
        data = content.split(";base64,")[1]
        print('data1:',data)
        data = base64.b64decode(data).decode('utf-8')
        print('data2: ', data)
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
    not_dna = False
    not_protein = False
    for seqname,seq in seqs:
        dna_set = {'A','T','G','C','N','-'}
        protein_set = {'A','R','N','D','C','Q','E','G','H','I','L','K','M','F','P','S','T','W','Y','V','-'}
        if sequence_type.upper()  == 'DNA':
            if len(dna_set) < len(set(seq) | dna_set):
                base_err = True
                break
        if sequence_type.upper()  == 'AA':
            if len(protein_set) < len(set(seq) | protein_set):
                base_err = True
                break
        if sequence_type.upper() == 'AUTO':
            if len(dna_set) < len(set(seq) | dna_set):
                not_dna = True
            if len(protein_set) < len(set(seq) | protein_set):
                not_protein = True
    if base_err:
        return {'successful':False, 'msg':f'{sequence_type} sequences not valid, please check', 'res': {'seqs':seqs}}
    
    if (sequence_type.upper() == 'AUTO') and (not_dna) and (not_protein) :
        return {'successful':False, 'msg':f'Unclear sequence type (DNA or Protein), please check', 'res': {'seqs':seqs}}
    
    if len(seqs) == 0:
        return {'successful':False, 'msg':f'No sequences parsed, please check', 'res': {'seqs':seqs}}
    if sequence_type.upper() == 'AUTO':
        if not_dna:
            sequence_type = 'aa'
        if not_protein:
            sequence_type = 'dna'
    return {'successful':successful, 'msg':msg, 'res': {'seqs':seqs,'sequence_type':sequence_type}}
            

            
    