# -*- coding: utf-8 -*-
#!/usr/bin/env python
import os
import toml

#read config file
PNG_PATH = 'figure_output'
FA_PATH = 'sequence_input'
EXAMPLE_PATH = 'examples'
CONFIG_PATH = 'configs'
GOOGLE_ANALYTICS_ID = ''
MAX_SEQ_LIMIT = 50000
MAX_INPUT_SIZE = 5242880
MAX_SEQ_LEN = 100
GOOGLE_ANALYTICS_ID = ''
BAIDU_TONGJI_ID = ''
SQLITE3_DB = 'MetaLogo/db/metalogo.db'
CLUSTALO_BIN = ''
RATE4SITE_BIN = ''
TREECLUSTER_BIN = ''

if os.path.exists('MetaLogo/server.toml'):
    paras_dict = toml.load('MetaLogo/server.toml')
    if 'example_path' in paras_dict:
        EXAMPLE_PATH = paras_dict['example_path']
    if 'output_fa_dir' in paras_dict:
        FA_PATH = paras_dict['output_fa_dir']
    if 'output_png_path' in paras_dict:
        PNG_PATH = paras_dict['output_png_path']
    if 'config_path' in paras_dict:
        CONFIG_PATH = paras_dict['config_path']
    if 'max_seq_limit' in paras_dict:
        MAX_SEQ_LIMIT = paras_dict['max_seq_limit']
    if 'max_input_size' in paras_dict:
        MAX_INPUT_SIZE = paras_dict['max_input_size']
    if 'max_seq_len' in paras_dict:
        MAX_SEQ_LEN = paras_dict['max_seq_len']
    if 'google_analytics_id' in paras_dict:
        GOOGLE_ANALYTICS_ID = paras_dict['google_analytics_id']
    if 'baidu_tongji_id' in paras_dict:
        BAIDU_TONGJI_ID = paras_dict['baidu_tongji_id']
    if 'sqlite3_db' in paras_dict:
        SQLITE3_DB = paras_dict['sqlite3_db']
    if 'clustalo_bin' in paras_dict:
        CLUSTALO_BIN = paras_dict['clustalo_bin']
    if 'rate4site_bin' in paras_dict:
        RATE4SITE_BIN = paras_dict['rate4site_bin']
    if 'treecluster_bin' in paras_dict:
        TREECLUSTER_BIN = paras_dict['treecluster_bin']

if not os.path.exists(PNG_PATH):
    os.makedirs(PNG_PATH, exist_ok=True)
if not os.path.exists(FA_PATH):
    os.makedirs(FA_PATH, exist_ok=True)
if not os.path.exists(CONFIG_PATH):
    os.makedirs(CONFIG_PATH, exist_ok=True)
