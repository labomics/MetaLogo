# -*- coding: utf-8 -*-
#!/usr/bin/env python

# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

import os, sys

from MetaLogo.MetaLogo.pholy import fasttree, treecluster
current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

from ..handle_seqs import handle_seqs_str,handle_seqs_file
from ..handle_seqs import save_seqs

import uuid
import os
import time
import json

from flask import Flask, send_from_directory



import plotly.express as px
import pandas as pd
from matplotlib import pyplot as plt
import sys
from plotly.tools import mpl_to_plotly
from io import BytesIO
import base64

from ...MetaLogo.colors import get_color_scheme,basic_aa_color_scheme, basic_dna_color_scheme,basic_rna_color_scheme
import json
import toml

from ..sqlite3 import get_status,write_status
from ..redis_queue import enqueue
from ..config import PNG_PATH,FA_PATH,EXAMPLE_PATH,CONFIG_PATH,\
                     GOOGLE_ANALYTICS_ID,MAX_SEQ_LIMIT,MAX_SEQ_LIMIT_AUTO,MAX_INPUT_SIZE,\
                     MAX_SEQ_LEN,BAIDU_TONGJI_ID,SQLITE3_DB,\
                     CLUSTALO_BIN,FASTTREE_BIN,FASTTREEMP_BIN,TREECLUSTER_BIN,\
                     GROUP_LIMIT




from ..app import app


cur_dir = os.path.dirname(os.path.realpath(__file__))
#google
gtag_js = '''
window.dataLayer = window.dataLayer || [];
 function gtag(){dataLayer.push(arguments);}
 gtag('js', new Date());
 gtag('config', '%s');
'''%GOOGLE_ANALYTICS_ID
with open(f'{cur_dir}/../assets/google.js','w') as outpf:
    outpf.write(gtag_js)

#baidu
tongji_js = '''
var _hmt = _hmt || [];
(function() {
  var hm = document.createElement('script');
  hm.src = 'https://hm.baidu.com/hm.js?%s';
  var s = document.getElementsByTagName('script')[0]; 
  s.parentNode.insertBefore(hm, s);
})();
'''%BAIDU_TONGJI_ID
with open(f'{cur_dir}/../assets/baidu.js','w') as outpf:
    outpf.write(tongji_js)




alphabets_list = ['A','R','N','D','C','Q','E','G','H','I','L','K','M','F','P','S','T','W','Y','V','-','B','J','O','U','X','Z']

input_format_dropdown = dbc.FormGroup(
    [
        dbc.Label("Input Format", html_for="dropdown"),
        dcc.Dropdown(
            id="input_format_dropdown",
            options=[
                {"label": "Fasta", "value": 'Fasta'},
                {"label": "Fastq", "value": 'Fastq'}
            ],
            value='Fasta',
            searchable=False,
            clearable=False,
        ),
    ]
)

sequence_type_dropdown = dbc.FormGroup(
    [
        dbc.Label("Sequence Type", html_for="dropdown"),
        dcc.Dropdown(
            id="sequence_type_dropdown",
            options=[
                {"label": "Auto", "value": 'auto'},
                {"label": "DNA", "value": 'dna'},
                {"label": "RNA", "value": 'rna'},
                {"label": "Protein", "value": 'aa'},
            ],
            value='auto',
            searchable=False,
            clearable=False,
        ),
    ]
)
grouping_by_dropdown = dbc.FormGroup(
    [
        dbc.Label("Grouping By", html_for="dropdown"),
        dcc.Dropdown(
            id="grouping_by_dropdown",
            options=[
                {"label": "Auto", "value": 'auto'},
                {"label": "Length", "value": 'length'},
                {"label": "Seq identifier", "value": 'identifier'},
            ],
            value='auto',
            searchable=False,
            clearable=False,
        ),
    ]
)
cluster_method_dropdown = dbc.FormGroup(
    [
        dbc.Label("Clustering method",html_for='input'),
        dcc.Dropdown(
            id="clustering_method_dropdown",
            options=[
                {"label": "Max", "value": 'max'},
                {"label": "Max_clade", "value": 'max_clade'},
                {"label": "Single_linkage", "value": 'single_linkage'},
            ],
            value='max',
            searchable=False,
            clearable=False,
        ),

    ]
)
grouping_resolution = dbc.FormGroup(
    [
        dbc.Label("Grouping resolution",html_for='input'),
        dbc.Input(type="number", min=0, max=1, value=0.5, step=0.00001, id="grouping_resolution"),
    ]
)
max_len_input = dbc.FormGroup(
    [
        dbc.Label("Maximum Length",html_for='input'),
        dbc.Input(type="number", min=0, max=MAX_SEQ_LEN, step=1, value=100, id="max_len_input"),
    ]
)

min_len_input = dbc.FormGroup(
    [
        dbc.Label("Minimum Length",html_for='input'),
        dbc.Input(type="number", min=0, max=MAX_SEQ_LEN, step=1, value=10,id="min_len_input"),
    ]
)
display_range_left_input = dbc.FormGroup(
    [
        dbc.Label("Display Range (left)",html_for='input'),
        dbc.Input(type="number", min=0, max=MAX_SEQ_LEN, step=1, value=0,id="display_range_left",disabled="disabled"),
        html.Span("For aligned sequences",style={'fontSize':'10px','color':'#ff6f00'})
    ]
)
display_range_right_input = dbc.FormGroup(
    [
        dbc.Label("Display Range (right)",html_for='input'),
        dbc.Input(type="number", min=-1, max=MAX_SEQ_LEN, step=1, value=-1,id="display_range_right",disabled="disabled"),
        html.Span("-1 means till the end",style={'fontSize':'10px','color':'#ff6f00'})
    ]
)
group_limit = dbc.FormGroup(
    [
        dbc.Label("Group Limit",html_for='input'),
        dbc.Input(type="number", min=1, max=GROUP_LIMIT, step=1, value=20,id="group_limit"),
    ]
)

seqinput_form = html.Div([
    html.Label([f'Paste sequences (<= {MAX_SEQ_LIMIT}  sequences) ',html.A("Load example1, ",href='#input_panel',id="load_example"),
                html.A(" example2,",href='#input_panel',id="load_example2"), html.A(" example3",href='#input_panel',id="load_example3")]),
    html.Div('*The first sequence of the input should be your target sequence, if you have one. MetaLogo will track the grouping position of the first sequence for you. ',style={'fontSize':'10px','color':'#ff6f00'}),
    dcc.Textarea(
        placeholder='Paste sequences in chosen input format',
        value='',
        rows=5,
        style={'width': '100%'},
        id = 'seq_textarea',
        persistence='true'
    ),  
    html.Div([
        html.Span('* Because of small-sample correction, make sure each group (grouping by length or others) contains sufficient DNA or protein sequences if you choose '),
        html.Span('Bits ', style={'fontStyle':'italic'}),
        html.Span('as height algorithm (Default) rather than '),
        html.Span('Probabilities.', style={'fontStyle':'italic'}),
        html.Span(' Or choose the '), 
        html.Span('Bits_without_correction',style={'fontStyle':'italic'}),
        html.Span(' algorithm.'),

        ],style={'fontSize':'10px','color':'#ff6f00'}),    
    html.Label(f'Or upload a file (<={(MAX_INPUT_SIZE/1024)/1024}MB)'),
    html.Label('',id='uploaded_label2',style={"color":"orange"}),
    html.Label('',id='uploaded_label',style={"color":"#11FF00"}),
    html.Label('',id='remove_label',style={"color":"red"}),
    dcc.Upload([
        html.Div('Drag and Drop or Select a File',n_clicks=0,id='upload_div')
        ], 
        #max_size = 1024 * 1024 * 5,
        max_size =  MAX_INPUT_SIZE,
        id='file_upload',
        style_reject = { 'borderStyle': 'solid', 'borderColor': '#c66', 'backgroundColor': 'orange'},
        style={
            'width': '100%',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center'
        }
        ),
])

input_submit =  html.Div(
    [
        dbc.Button(
            "Submit", id="submit1",  color='info'
        ),
        html.Div("* Submit here and skip following steps by using default parameters", 
                    style={"fontSize":"10px","verticalAlign": "middle"}),
    ],
    style={'marginTop':'10px','textAlign':'right'}
)

basic_analysis_dropdown = dbc.FormGroup(
    [
        dbc.Label("Basic analysis?", html_for="dropdown"),
        dcc.Dropdown(
            id="basic_analysis_dropdown",
            options=[
                {"label": "Yes", "value": 'Yes'},
                {"label": "No", "value": 'No'}
            ],
            value='Yes',
            searchable=False,
            clearable=False,
        ),
    ]
)

input_panel = dbc.Card(
    [
        dbc.CardHeader("Step1. Input data"),
        dbc.CardBody(
            [
                dbc.Row([
                    dbc.Col(input_format_dropdown),
                    dbc.Col(sequence_type_dropdown),
                    dbc.Col(basic_analysis_dropdown),
                ]),
                dbc.Row([
                    dbc.Col(grouping_by_dropdown),
                    dbc.Col(cluster_method_dropdown),
                    dbc.Col(grouping_resolution),
                ]),
                dbc.Row([
                    dbc.Col(min_len_input),
                    dbc.Col(max_len_input),
                    dbc.Col(display_range_left_input),
                    dbc.Col(display_range_right_input),
                    dbc.Col(group_limit),
                ]),
                dbc.Row(dbc.Col(seqinput_form)),
                dbc.Row([dbc.Col(''),dbc.Col(input_submit)],justify='end'),

            ]
        )
    ],style={'marginBottom':'10px'},id='input_panel'
)

height_algorithm_dropdown = dbc.FormGroup(
    [
        dbc.Label("Height Algorithm", html_for="dropdown"),
        dcc.Dropdown(
            id="height_algorithm_dropdown",
            options=[
                {"label": "Bits", "value": 'bits'},
                {"label": "Bits without correction", "value": 'bits_without_correction'},
                {"label": "Probabilities", "value": 'probabilities'}
            ],
            value='bits',
            searchable=False,
            clearable=False,
        ),
    ]
)
align_dropdown = dbc.FormGroup(
    [
        dbc.Label("Adjacent Alignment?", html_for="dropdown"),
        dcc.Dropdown(
            id="align_dropdown",
            options=[
                {"label": "Yes", "value": 'Yes'},
                {"label": "No", "value": 'No'}
            ],
            value='Yes',
            searchable=False,
            clearable=False,
        ),
    ]
)
padding_align_dropdown = dbc.FormGroup(
    [
        dbc.Label("Global Alignment with Padding?", html_for="dropdown"),
        dcc.Dropdown(
            id="padding_align_dropdown",
            options=[
                {"label": "Yes", "value": 'Yes'},
                {"label": "No", "value": 'No'}
            ],
            value='Yes',
            searchable=False,
            clearable=False,
        ),
        html.Span("Avaliable when grouping by length or identifier",style={'fontSize':'10px','color':'#ff6f00'})
    ]
)


align_metric = dbc.FormGroup(
    [
        dbc.Label("Score Metric", html_for="dropdown"),
        dcc.Dropdown(
            id="score_metric",
            options=[
                {"label": "Dot Production", "value": 'dot_product'},
                {"label": "Jensen Shannon", "value": 'js_divergence'},
                {"label": "Cosine", "value": 'cosine'},
                {"label": "Entropy weighted Bhattacharyya Coefficient", "value": 'entropy_bhattacharyya'},
            ],
            value='dot_product',
            searchable=False,
            clearable=False,
        ),
    ]
)

connect_threshold = dbc.FormGroup(
    [
        dbc.Label("Connect Threshold",html_for='input'),
        dbc.Input(type="number", min=-1, step=0.01, value=-0.2, id="connect_threshold"),
    ]
)


align_gap_score = dbc.FormGroup(
    [
        dbc.Label("Gap Penalty",html_for='input'),
        dbc.Input(type="number",  value=-1, step=0.001, id="gap_score"),
    ]
)

style_submit =  html.Div(
    [
        dbc.Button(
            "Submit", id="submit2",  color='info'
        ),
        html.Div("* Submit the job to our server and wait for results", 
                    style={"fontSize":"10px","verticalAlign": "middle"}),
    ],
    style={'marginTop':'10px','textAlign':'right'}
)

algorithm_panel = dbc.Card([
    dbc.CardHeader("Step2. Logo Alignment Algorithm"),
    dbc.CardBody([
        dbc.Row([
            dbc.Col(height_algorithm_dropdown),
            dbc.Col(align_dropdown),
            dbc.Col(padding_align_dropdown),
        ]),
        dbc.Row([
            dbc.Col(align_metric),
            dbc.Col(align_gap_score),
            dbc.Col(connect_threshold),
        ]),
        dbc.Row(dbc.Col(style_submit))
    ])
])

logo_type_dropdown = dbc.FormGroup(
    [
        dbc.Label("Logo Shape", html_for="dropdown"),
        dcc.Dropdown(
            id="logo_shape_dropdown",
            options=[
                {"label": "Horizontal", "value": 'Horizontal'},
                {"label": "Circular", "value": 'Circle'},
                {"label": "Radial", "value": 'Radiation'},
                {"label": "3D", "value": 'Threed'},
            ],
            value='Horizontal',
            searchable=False,
            clearable=False,
        ),
    ]
)
logo_connect_tree_dropdown = dbc.FormGroup(
    [
        dbc.Label("Connect tree?", html_for="dropdown"),
        dcc.Dropdown(
            id="connect_tree_dropdown",
            options=[
                {"label": "Yes", "value": 'Yes'},
                {"label": "No", "value": 'No'},
            ],
            value='Yes',
            searchable=False,
            clearable=False,
        ),
    ]
)


sort_dropdown = dbc.FormGroup(
    [
        dbc.Label("Sort By", html_for="dropdown"),
        dcc.Dropdown(
            id="sortby_dropdown",
            options=[
                {"label": "Length", "value": 'length'},
                {"label": "Length Reverse", "value": 'length_reverse'},
                {"label": "Group Id", "value": 'identifier'},
                {"label": "Group Id Reverse", "value": 'identifier_reverse'},
                {"label": "Auto", "value": 'auto'},
            ],
            value='length',
            searchable=False,
            clearable=False,
        ),
    ]
)

logo_margin_input = dbc.FormGroup(
    [
        dbc.Label("Logo Margin Ratio",html_for='input'),
        dbc.Input(type="number", min=0, max=1, step=0.01, value=0.1,id="logo_margin_input"),
    ]
)

column_margin_input = dbc.FormGroup(
    [
        dbc.Label("Column Margin Ratio",html_for='input'),
        dbc.Input(type="number", min=0, max=1, step=0.01, value=0.05,id="column_margin_input"),
    ]
)

character_margin_input = dbc.FormGroup(
    [
        dbc.Label("Character Margin Ratio",html_for='input'),
        dbc.Input(type="number", min=0, max=1, step=0.01, value=0.05,id="char_margin_input"),
    ]
)
layout_submit =  html.Div(
    [
        dbc.Button(
            "Submit", id="submit3",  color='info'
        ),
        html.Div("* Submit here and skip following steps by using default parameters", 
                    style={"fontSize":"10px","verticalAlign": "middle"}),
    ],
    style={'marginTop':'10px','textAlign':'right'}
)

layout_panel = dbc.Card(
    [
        dbc.CardHeader("Step3. Define Layout"),
        dbc.CardBody(
            [
                dbc.Row([
                    dbc.Col(logo_type_dropdown),
                    dbc.Col(logo_connect_tree_dropdown),
                    dbc.Col(sort_dropdown),
                    #dbc.Col(align_dropdown)
                    ]),
                dbc.Row([
                    dbc.Col(logo_margin_input),
                    dbc.Col(column_margin_input),
                    dbc.Col(character_margin_input)
                ]),
                dbc.Row([dbc.Col(''),dbc.Col(layout_submit)],justify='end'),
            ]
        )
    ], style={'marginTop':'10px'}
)
showxy_checklist = dbc.FormGroup(
    [
        dbc.Label("Hide Axis Border and Ticks "),
        dbc.Checklist(
            options=[
                {"label": "left", "value": 'hideleft'},
                {"label": "right", "value": 'hideright'},
                {"label": "bottom", "value": 'hidebottom'},
                {"label": "top", "value": 'hidetop'},
                {"label": "x ticks", "value": 'hidexticks'},
                {"label": "y ticks", "value": 'hideyticks'},
                {"label": "z ticks", "value": 'hidezticks'},
            ],
            value=[],
            id="hidexy_check_input",
            inline=True,
        ),
    ]
)
xlabel_input = dbc.FormGroup(
    [
        dbc.Label("Xlabel",html_for='input'),
        dbc.Input(type="str",  value='Position',id="xlabel_input"),
    ]
)
ylabel_input = dbc.FormGroup(
    [
        dbc.Label("Ylabel",html_for='input'),
        dbc.Input(type="str",  value='Bits',id="ylabel_input"),
    ]
)
zlabel_input = dbc.FormGroup(
    [
        dbc.Label("Zlabel",html_for='input'),
        dbc.Input(type="str",  value='',id="zlabel_input"),
    ]
)
width_input = dbc.FormGroup(
    [
        dbc.Label("Figure Width",html_for='input'),
        dbc.Input(type="number", min=1,  value=10,id="width_input"),
    ]
)
height_input = dbc.FormGroup(
    [
        dbc.Label("Figure Height",html_for='input'),
        dbc.Input(type="number", min=1,  value=10, id="height_input")
    ]
    
)
show_groupid_checklist = dbc.FormGroup(
    [
        dbc.Label("Group Label"),
        dbc.Checklist(
            options=[
                {"label": "Show Group Label", "value": 'showid'},
            ],
            value=['showid'],
            id="showid_check_input",
            inline=True,
        ),
    ]
)
show_grid_checklist = dbc.FormGroup(
    [
        dbc.Label("Grid Background"),
        dbc.Checklist(
            options=[
                {"label": "Show Grid", "value": 'showgrid'},
            ],
            value=['showgrid'],
            id="showgrid_check_input",
            inline=True,
        ),
    ]
)
hide_version_checklist = dbc.FormGroup(
    [
        dbc.Label("Version Tag"),
        dbc.Checklist(
            options=[
                {"label": "Hide Version", "value": 'hideversion'},
            ],
            value=[],
            id="hide_version_checklist",
            inline=True,
        ),
    ]
)
download_format_dropdown = dbc.FormGroup(
    [
        dbc.Label("Download Format", html_for="dropdown"),
        dcc.Dropdown(
            id="download_format_dropdown",
            options=[
                {"label": "PNG", "value": 'png'},
                {"label": "PDF", "value": 'pdf'},
                {"label": "PS", "value": 'ps'},
                {"label": "EPS", "value": 'eps'},
                {"label": "SVG", "value": 'svg'}
            ],
            value='png',
            searchable=False,
            clearable=False,
        ),
    ]
)
color_scheme_dropdown = dbc.FormGroup(
    [
        dbc.Label("Color Scheme", html_for="dropdown"),
        dcc.Dropdown(
            id="color_dropdown",
            options=[
                {"label": "Auto", "value": 'auto'},
                {"label": "DNA Basic", "value": 'basic_dna_color'},
                {"label": "RNA Basic", "value": 'basic_rna_color'},
                {"label": "Protein Basic", "value": 'basic_aa_color'},
                {"label": "Custom (click color pickers to choose)", "value": 'custom'},
            ],
            value='auto',
            searchable=False,
            clearable=False,
        ),
    ]
)
#generate dna basic scheme
basic_dna_color_spans = []
for base in basic_dna_color_scheme.keys():
    basic_dna_color_spans.append(html.Span(base,id=f"basic_dna_{base}",
                    style = {
                             "verticalAlign": "middle","color":basic_dna_color_scheme[base],
                            "fontSize":"40px","fontWeight":"bold","padding":"20px"
                            }
    ))
basic_dna_color_panel = html.Div(basic_dna_color_spans)

basic_rna_color_spans = []
for base in basic_rna_color_scheme.keys():
    basic_rna_color_spans.append(html.Span(base,id=f"basic_rna_{base}",
                    style = {
                             "verticalAlign": "middle","color":basic_rna_color_scheme[base],
                            "fontSize":"40px","fontWeight":"bold","padding":"20px"
                            }
    ))
basic_rna_color_panel = html.Div(basic_rna_color_spans)


basic_aa_color_spans = []
for aa in basic_aa_color_scheme.keys():
    basic_aa_color_spans.append(html.Span(aa,id=f"basic_protein_{aa}",
                    style = {
                             "verticalAlign": "middle","color":basic_aa_color_scheme.get(aa,'grey'),
                            "fontSize":"40px","fontWeight":"bold","padding":"20px"
                            }
    ))
basic_aa_color_panel = html.Div(basic_aa_color_spans)

custom_basic_scheme = {}
custom_basic_groups = []
for alphabet in alphabets_list:
    colorpicker = dbc.Col(
        dbc.FormGroup(
        [
            dbc.Label(alphabet, style={"fontWeight":"bold"}),
            dbc.Input(
                type="color",
                id=f"colorpicker_{alphabet}",
                value="#000000",
                style={"width": 50, "height": 50, "margin":"auto"},
                persistence='true'
            ),
        ],style={"textAlign":"center"}
        )
    )
    custom_basic_groups.append(colorpicker)

style_submit =  html.Div(
    [
        dbc.Button(
            "Submit", id="submit4",  color='primary'
        ),
        html.Div("* Submit the job to our server and wait for results", 
                    style={"fontSize":"10px","verticalAlign": "middle"}),
    ],
    style={'marginTop':'10px','textAlign':'right'}
)

title_input = dbc.FormGroup(
    [
        dbc.Label("Figure Title",html_for='input'),
        dbc.Input(type="string", value='MetaLogo',id="title_input"),
    ]
)
labelsize_input = dbc.FormGroup(
    [
        dbc.Label("XY Label Size",html_for='input'),
        dbc.Input(type="number",min=0, value=10,id="label_size"),
    ]
)

ticksize_input = dbc.FormGroup(
    [
        dbc.Label("Ticks Size",html_for='input'),
        dbc.Input(type="number",min=0, value=10,id="tick_size"),
    ]
)

titlesize_input = dbc.FormGroup(
    [
        dbc.Label("Title Size",html_for='input'),
        dbc.Input(type="number", min=0,value=20,id="title_size"),
    ]
)
auto_size_dropdown = dbc.FormGroup(
    [
        dbc.Label("Auto figure size?", html_for="dropdown"),
        dcc.Dropdown(
            id="auto_size_dropdown",
            options=[
                {"label": "Yes", "value": 'Yes'},
                {"label": "No", "value": 'No'}
            ],
            value='Yes',
            searchable=False,
            clearable=False,
        ),
    ]
)


idsize_input = dbc.FormGroup(
    [
        dbc.Label("Group Label Size",html_for='input'),
        dbc.Input(type="number", min=0, value=10,id="id_size"),
    ]
)
align_alpha_input = dbc.FormGroup(
    [
        dbc.Label("Alignment Transparency",html_for='input'),
        dbc.Input(type="number", min=0, max=1, value=0.1, step=0.001, id="align_alpha"),
    ]
)
align_color_picker =  dbc.FormGroup(
        [
            dbc.Label("Alignment Color"),
            dbc.Input(
                type="color",
                id=f"align_color",
                value="#007bff",
                style={"width": 50, "height": 50, "margin":"auto"},
                persistence='true'
            ),
        ],style={"textAlign":"center"})

style_panel = dbc.Card(
    [
        dbc.CardHeader("Step4. Set Output Style"),
        dbc.CardBody(
            [
                dbc.Row([dbc.Col(title_input)]),
                dbc.Row([
                    dbc.Col(titlesize_input),
                    dbc.Col(xlabel_input),
                    dbc.Col(ylabel_input),
                    dbc.Col(zlabel_input),
                ]),
                dbc.Row([
                    dbc.Col(auto_size_dropdown),
                    dbc.Col(labelsize_input),
                    dbc.Col(ticksize_input),
                    dbc.Col(idsize_input),
                ]),
                dbc.Row([

                    dbc.Col(width_input),
                    dbc.Col(height_input),
                    dbc.Col(align_color_picker),
                    dbc.Col(align_alpha_input)
                    ]),
                dbc.Row([
                    dbc.Col(showxy_checklist),
                    dbc.Col(show_groupid_checklist),
                    dbc.Col(show_grid_checklist),
                    dbc.Col(hide_version_checklist),
                ]),
                dbc.Row([
                    dbc.Col(color_scheme_dropdown),
                ]),
                dbc.Row([
                    dbc.Col(basic_dna_color_panel)
                ],id='basic_dna_color_panel'),
                dbc.Row([
                    dbc.Col(basic_rna_color_panel)
                ],id='basic_rna_color_panel'),
                dbc.Row([
                    dbc.Col(basic_aa_color_panel)
                ],id='basic_aa_color_panel'),
                dbc.Row(
                    custom_basic_groups
                ,style={'padding':'20px'},id='custom_basic_groups'),
                dbc.Row(
                    dbc.Col(download_format_dropdown),
                ),
                dbc.Row([dbc.Col(''),dbc.Col(style_submit)],justify='end'),

            ]
        )
    ], style={'marginTop':'10px'}
)

modal = dbc.Modal(
            [
                dbc.ModalHeader("Error", id="modal_header"),
                dbc.ModalBody("Message", id="modal_body"),
                dbc.ModalFooter(
                   html.Span('* Click outside of the modal or press ESC to hide it', style={"fontSize":"10px","color":"orange"}) 
                ),
            ],
            id="modal",
            centered=True,
            is_open=False,
        )

result_modal =  dbc.Modal(
            [
                dbc.ModalHeader("Result"),
                dbc.ModalBody(
                    [

                ]
                ),
            ],
            id="res_modal",
            is_open=False,
            backdrop=False,
            size="xl",
            centered=True,
        )


loading_spinner = html.Div(
    [
        dbc.Spinner(html.Div(id="loading-output"),fullscreen=True,fullscreen_style={"opacity":"0.8"}),
    ]
)

layout = dbc.Container(children=[
        html.Hr(),
        input_panel,
        algorithm_panel,
        layout_panel,
        style_panel,
        modal,
        result_modal,
        loading_spinner,
        html.Div('',id='functional_garbage',style={'display':'none'}),
        html.Div('',id='garbage',style={'display':'none'}),
        html.Div('',id='garbage2',style={'display':'none'}),
        html.Div('',id='finished_item',style={'display':'none'})
       ])

@app.callback(
    [
         Output('width_input','disabled'),
         Output('height_input','disabled'),
    ],
    Input('auto_size_dropdown','value')
)
def disable_figsize(auto):
    if auto=='Yes':
        return True,True
    else:
        return False,False

@app.callback(
    [
        Output('clustering_method_dropdown','disabled'),
        Output('grouping_resolution','disabled'),
    ],
    Input('grouping_by_dropdown','value')
)
def activate_clustering_method(group_by):
    if group_by != 'auto':
        return [True ,True]
    else:
        return [False,False]


@app.callback(Output("color_dropdown","value"), Input("sequence_type_dropdown","value"), prevent_initial_call=True)
def change_color_scheme(seqtype):
    if  seqtype in ['dna','rna']:
        return 'basic_dna_color'
    if seqtype == 'aa':
        return 'basic_aa_color'
    if seqtype == 'auto':
        return 'auto'
    return 'basic_aa_color'



#@app.callback(Output('modal','is_open'), Input('modal_close','n_clicks'))
#def close_modal(n):
#    return False

@app.callback(Output("seq_textarea","value"), 
    [Input("load_example","n_clicks"), Input("load_example2","n_clicks"),Input("load_example3","n_clicks"),Input("file_upload","contents")],
    prevent_initial_call=True)
def load_example(nclicks1,nclicks2,nclicks3,contents):
    ctx = dash.callback_context
    if not ctx.triggered:
        return
    else:
        example_id = ctx.triggered[0]['prop_id'].split('.')[0]
        if example_id == 'file_upload':
            return ''
        if example_id == 'load_example':
            #fa = 'examples/example2.fa'
            fa = f'{EXAMPLE_PATH}/ectf.fa'
        if example_id == 'load_example2':
            fa = f'{EXAMPLE_PATH}/cdr3.fa'
        if example_id == 'load_example3':
            fa = f'{EXAMPLE_PATH}/all_cluster_center.fa'
        if os.path.exists(fa):
            f = open(fa,'r')
            return ''.join(f.readlines())
        else:
            example = """\
>seq1 group@1-good
AAACACACACACAGAC
>seq2 group@1-good
AGACTTAGACACAGAC
>seq3 group@1-good
ATACATACGCACAGAC
>seq4 group@2-bad
CTGCATGCAGAC
>seq5 group@2-bad
GTACATACACAC
>seq6 group@2-bad
ATCCATCTATAC
"""
            return example


@app.callback([
                Output("score_metric","disabled"),
                Output("connect_threshold","disabled"),
                Output("gap_score","disabled"),
                Output("padding_align_dropdown","value"),
                Output("padding_align_dropdown","disabled")
              ], 
              [
                  Input("align_dropdown","value"),
                  Input("grouping_by_dropdown","value"),
              ])
def enable_align_detail(align,group_by):
    arrs = []

    if align == 'Yes':
        arrs = [False,False,False,'No']
    else:
        arrs = [True,True,True,'No']

    if group_by == 'auto':
        arrs += [True]
    else:
        if align == 'Yes':
            arrs += [False]
        else:
            arrs += [True]
    return arrs




@app.callback(Output("basic_dna_color_panel", "style"), Input("color_dropdown", "value"))
def hidden(color_scheme):
    if color_scheme == 'basic_dna_color':
        return {"display":""}
    else:
        return {"display":"none"}

@app.callback(Output("basic_rna_color_panel", "style"), Input("color_dropdown", "value"))
def hidden(color_scheme):
    if color_scheme == 'basic_rna_color':
        return {"display":""}
    else:
        return {"display":"none"}

@app.callback(Output("basic_aa_color_panel", "style"), Input("color_dropdown", "value"))
def hidden(color_scheme):
    if color_scheme == 'basic_aa_color':
        return {"display":""}
    else:
        return {"display":"none"}

@app.callback(Output("custom_basic_groups", "style"), Input("color_dropdown", "value"))
def hidden(color_scheme):
    if color_scheme == 'custom':
        return {"display":""}
    else:
        return {"display":"none"}

@app.callback(Output('uploaded_label2','children'),
              Input('upload_div','n_clicks'),Input('file_upload', 'filename') )
def show_warn_filesize(n_clicks,filename):
    #print('in warn',n_clicks,filename)
    #print( dash.callback_context.triggered)
    if (filename is not None) and (len(filename) > 0):
        return ''
    if (n_clicks >= 1) and (filename is None):
        return  '* Warning: Not exceed the size limit' 

@app.callback(
    Output('file_upload','contents'),
    Input('remove_label','n_clicks'), prevent_initial_call=True
)
def clear_content(n_clicks):
    if n_clicks > 0:
        return ''
    return ''

@app.callback(
              [Output('uploaded_label', 'children'),Output('remove_label', 'children')],
              Input('file_upload', 'contents'),
              State('file_upload', 'filename'),
              State('file_upload', 'last_modified'), prevent_initial_call=True)
def update_output(content, name, date):
    if (content is not None) and len(content)>0:
        return f"√ {name} uploaded!", "--remove"
    return '',''

app.clientside_callback(
    """
    function(children) {
        if (children.length>0){
            window.scrollTo({top:document.body.scrollHeight,behavior:'smooth'});
        }
    }
    """,
    Output('garbage', 'children'),
    Input('functional_garbage', 'children'),
)


@app.callback(
    [
        Output("sortby_dropdown","value"),
        Output("sortby_dropdown","disabled"),
    ],
    Input("grouping_by_dropdown","value")
)
def change_default_order(sort_by_value):
    if sort_by_value == 'identifier':
        return 'identifier' , False
    elif sort_by_value == 'length':
        return 'length' ,False
    else:
        return 'auto',True

@app.callback(
    [
        Output("xlabel_input","value"),
        Output("ylabel_input","value"),
        Output("zlabel_input","value"),
        Output("hidexy_check_input","value")
    ],
    [
        Input("logo_shape_dropdown","value"),
        Input("height_algorithm_dropdown","value"),
    ]
)
def change_labels(logo_shape,height_algorithm):
    ctx = dash.callback_context
    if not ctx.triggered:
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update
    else:
        example_id = ctx.triggered[0]['prop_id'].split('.')[0]
        if example_id == 'logo_shape_dropdown':
            if logo_shape == 'Circle':
                return '','','',['hidexticks','hideyticks']
            if logo_shape == 'Horizontal':
                return 'Position','Bits','',[]
            if logo_shape == 'Radiation':
                return '','','',['hidexticks','hideyticks']
            if logo_shape == 'Threed':
                return 'Position','','Bits',['hideyticks']
        if example_id == 'height_algorithm_dropdown':
            if height_algorithm in ['bits','bits_without_correction']:
                return dash.no_update, 'Bits', dash.no_update, dash.no_update
            elif height_algorithm =='probabilities':
                return dash.no_update, 'Probabilities', dash.no_update, dash.no_update

    return dash.no_update, dash.no_update, dash.no_update, dash.no_update

@app.callback(
    [
        Output("width_input","value"),
        Output("height_input","value"),
    ],
    Input("logo_shape_dropdown","value")
)
def change_figure_size(logo_shape):

    if logo_shape == 'Circle':
        return 10,10
    if logo_shape == 'Horizontal':
        return 20,10
    if logo_shape == 'Radiation':
        return 10,10
    if logo_shape == 'Threed':
        return 10,10

@app.callback(
    [
        Output("display_range_left","disabled"),
        Output("display_range_right","disabled")
    ],
    [
        Input("padding_align_dropdown","value"),
        Input("grouping_by_dropdown","value")
    ],prevent_initial_call=True
)
def activate_display_range(padding,group_by):
    if padding == 'Yes' or group_by == 'auto':
        return None,None 
    else:
        return 'disabled','disabled'

app.clientside_callback(
    """
    function(finished) {
        if (finished.startsWith('finished')){
            window.open('/results/'+finished.substr(8),'_self');
        }
    }
    """,
    Output('garbage2', 'children'),
    Input('finished_item', 'children'),
)

#@app.callback(
#    Output("url","pathname"),
#    Input("finished_item","children")
#)   
#def gotoresult(status):
#    if status.startswith('finished'):
#        return '/results/' + status.replace('finished','')
#    else:
#        raise PreventUpdate



@app.callback(
    [
        Output("loading-output", "children"),
        Output('modal_header', 'children'),
        Output('modal_body', 'children'),
        Output('modal', 'is_open'),
        Output('finished_item', 'children'),
    ],
    [
        Input('submit1', 'n_clicks'),
        Input('submit2', 'n_clicks'),
        Input('submit3', 'n_clicks'),
        Input('submit4', 'n_clicks')
    ],
    [
        State('auto_size_dropdown','value'),
        State('group_limit','value'),
        State('connect_tree_dropdown','value'),
        State('grouping_resolution','value'),
        State('clustering_method_dropdown','value'),
        State('basic_analysis_dropdown','value'),
        State('display_range_left','value'),
        State('display_range_right','value'),
        State('height_algorithm_dropdown','value'),
        State('hide_version_checklist','value'),
        State('padding_align_dropdown','value'),
        State('gap_score','value'),
        State('align_color','value'),
        State('align_alpha','value'),
        State('title_size','value'),
        State('tick_size','value'),
        State('label_size','value'),
        State('id_size','value'),
        State('title_input','value'),
        State('input_format_dropdown', 'value'),
        State('sequence_type_dropdown', 'value'),
        State('grouping_by_dropdown', 'value'),
        State('max_len_input', 'value'),
        State('min_len_input', 'value'),
        State('seq_textarea', 'value'),
        State('file_upload', 'contents'),
        State('logo_shape_dropdown', 'value'),
        State('sortby_dropdown', 'value'),
        State('align_dropdown', 'value'),
        State('score_metric', 'value'),
        State('connect_threshold', 'value'),
        State('logo_margin_input', 'value'),
        State('column_margin_input', 'value'),
        State('char_margin_input', 'value'),
        State('xlabel_input','value'),
        State('ylabel_input','value'),
        State('zlabel_input','value'),
        State('width_input','value'),
        State('height_input','value'),
        State('showid_check_input','value'),
        State('showgrid_check_input','value'),
        State('hidexy_check_input','value'),
        State('download_format_dropdown','value'),
        State('color_dropdown','value'),
    ] + [State(f'colorpicker_{base}', 'value') for base in alphabets_list],
    prevent_initial_call=True
)
def submit(nclicks1,nclicks2,nclicks3,nclicks4, 
            auto_size_dropdown,
            group_limit,
            connect_tree_dropdown,
            group_resolution,clustering_method,
            basic_analysis_dropdown,
            display_left, display_right,
            height_algorithm_dropdown,
            hide_version_checklist,
            padding_align,
            gap_score,
            align_color, align_alpha,
            title_size, tick_size, label_size, id_size,  
            title_input, input_format_dropdown, 
            sequence_type_dropdown, grouping_by_dropdown, max_len_input, min_len_input,
            seq_textarea, file_upload_content, logo_shape_dropdown, sortby_dropdown,
            align_dropdown,align_metric, connect_threshold, logo_margin_input, column_margin_input,
            char_margin_input, xlabel_input, ylabel_input, zlabel_input, width_input, height_input,
            showid_check_input, showgrid_check_input,
            hidexy_check_input, download_format_dropdown, color_dropdown, *args):
    
    #check input
    for para in [
                    auto_size_dropdown,
                    group_limit,
                    connect_tree_dropdown,
                    group_resolution,clustering_method,
                    basic_analysis_dropdown,
                    display_left, display_right,
                    height_algorithm_dropdown,
                    hide_version_checklist,
                    padding_align,
                    gap_score,
                    align_color, align_alpha,
                    title_size, tick_size, label_size, id_size,  
                    title_input, input_format_dropdown, 
                    sequence_type_dropdown, grouping_by_dropdown, max_len_input, min_len_input,
                    seq_textarea, file_upload_content, logo_shape_dropdown, sortby_dropdown,
                    align_dropdown,align_metric, connect_threshold, logo_margin_input, column_margin_input,
                    char_margin_input, xlabel_input, ylabel_input, zlabel_input, width_input, height_input,
                    showid_check_input, showgrid_check_input,
                    hidexy_check_input, download_format_dropdown, color_dropdown
        ]:
        if para is None:
            return '','Error',f'None parameter not allowed, please check',True,''


    if group_limit > GROUP_LIMIT:
        return '','Error',f'Group limit not allowed > {GROUP_LIMIT}',True,''

    display_left = int(display_left) 
    display_right = int(display_right) 
    if (display_left > display_right) and (display_right != -1):
        return '','Error','Display range left > Range right',True,''

    if display_left < 0:
        return '','Error','Display range left illegal',True,''

    if max_len_input < min_len_input:
        return '','Error','Maximum length < Minimum length',True,''

    if max_len_input > MAX_SEQ_LEN:
        return '','Error',f'Maximum length should be <= {MAX_SEQ_LEN}.',True,''
    
    if (len(seq_textarea) == 0) and ((file_upload_content is None) or (len(file_upload_content) == 0)):
        return '','Error','Please paste sequences into the textarea or upload a fasta/fastq file',True,''

    seqs = []
    if (file_upload_content is not None) and (len(file_upload_content)>0 and (len(file_upload_content)>0) and (len(file_upload_content)>0) and (len(file_upload_content)>0) and (len(file_upload_content)>0) and (len(file_upload_content)>0) and (len(file_upload_content)>0) and (len(file_upload_content)>0) and (len(file_upload_content)>0)):
        response = handle_seqs_file(file_upload_content,format=input_format_dropdown,sequence_type=sequence_type_dropdown)
    elif len(seq_textarea) != 0:
        response = handle_seqs_str(seq_textarea,format=input_format_dropdown,sequence_type=sequence_type_dropdown)
    if not response['successful']:
        return '','Error',response['msg'],True,''
    seqs = response['res']['seqs']
    sequence_type = response['res']['sequence_type']

    seqs = [(name,seq) for name,seq in seqs  if ((len(seq)>=min_len_input) and (len(seq)<=max_len_input))]

    if len(seqs) > MAX_SEQ_LIMIT:
        return '','Error','Sequence number exceed the limitation',True,''
    
    if len(seqs) > MAX_SEQ_LIMIT_AUTO and grouping_by_dropdown.lower() == 'auto':
        return '','Error',f'In auto-grouping mode (MSA+Phylogenic tree+clustering), the input sequence number is limited to under {MAX_SEQ_LIMIT_AUTO}.',True,''

    if len(seqs) == 0:
        return '','Error','Detect no sequences with limited lengths',True,''
    

    uid = str(uuid.uuid4())
    #seq_file = f"tmp/server-{uid}.fasta"


    seq_file = f"{FA_PATH}/server.{uid}.fasta"
    save_seqs(seqs, seq_file)

    if color_dropdown.lower() == 'auto':
        if sequence_type == 'aa':
            color_scheme = get_color_scheme('basic_aa_color')
        elif sequence_type == 'dna':
            color_scheme = get_color_scheme('basic_dna_color')
        elif sequence_type == 'rna':
            color_scheme = get_color_scheme('basic_rna_color')
    else:
        if color_dropdown != 'custom':
            color_scheme = get_color_scheme(color_dropdown)
        else:
            color_scheme = dict(zip(alphabets_list,args))
    
    color_scheme['scheme_name'] = color_dropdown

    align = align_dropdown=='Yes'
    auto_size = auto_size_dropdown=='Yes'

    hide_left,hide_right,hide_bottom,hide_top = [False]*4
    hide_x_ticks,hide_y_ticks,hide_z_ticks = [False]*3
    hide_version_tag = False

    if 'hideleft' in hidexy_check_input:
        hide_left = True
    if 'hideright' in hidexy_check_input:
        hide_right = True
    if 'hidetop' in hidexy_check_input:
        hide_top = True
    if 'hidebottom' in hidexy_check_input:
        hide_bottom = True
    if 'hidexticks' in hidexy_check_input:
        hide_x_ticks = True
    if 'hideyticks' in hidexy_check_input:
        hide_y_ticks = True
    if 'hidezticks' in hidexy_check_input:
        hide_z_ticks = True

    show_grid = False
    if 'showgrid' in showgrid_check_input:
        show_grid = True
    
    show_group_id = False
    if 'showid' in showid_check_input:
        show_group_id = True

    if 'hideversion' in hide_version_checklist:
        hide_version_tag = True
    
    withtree = connect_tree_dropdown == 'Yes'
    

    padding_align = padding_align=='Yes'
    analysis = basic_analysis_dropdown=='Yes'

    config = dict(group_strategy = grouping_by_dropdown, group_order = sortby_dropdown, logo_type = logo_shape_dropdown, 
                          align=align, align_metric=align_metric, connect_threshold = connect_threshold,
                          color=color_scheme, task_name=title_input, hide_left_axis = hide_left, hide_right_axis = hide_right, 
                          hide_bottom_axis = hide_bottom, hide_top_axis = hide_top, show_grid = show_grid, show_group_id = show_group_id,
                          hide_x_ticks = hide_x_ticks, hide_y_ticks = hide_y_ticks, hide_z_ticks=hide_z_ticks,
                          x_label=xlabel_input, y_label=ylabel_input, z_label=zlabel_input,
                          title_size=title_size, label_size=label_size, group_id_size=id_size,
                          tick_size=tick_size, logo_margin_ratio = logo_margin_input, column_margin_ratio = column_margin_input,
                          figure_size_x=width_input, figure_size_y=height_input,
                          display_range_left = display_left, display_range_right = display_right,
                          char_margin_ratio = char_margin_input, align_color=align_color,align_alpha=align_alpha ,
                          gap_score = gap_score, padding_align = padding_align, hide_version_tag=hide_version_tag,
                          sequence_type = sequence_type, height_algorithm=height_algorithm_dropdown,
                          seq_file=seq_file, fa_output_dir = FA_PATH, uid=uid,
                          min_length=min_len_input,max_length=max_len_input,seq_file_type='fasta',
                          sqlite3_db=SQLITE3_DB,output_dir = PNG_PATH,logo_format = download_format_dropdown,
                          group_resolution=group_resolution,create_time=int(time.time()),
                          analysis=analysis,clustering_method=clustering_method,withtree=withtree,
                          clustalo_bin=CLUSTALO_BIN,fasttreemp_bin=FASTTREEMP_BIN,fasttree_bin=FASTTREE_BIN,treecluster_bin=TREECLUSTER_BIN,
                          group_limit=group_limit,auto_size=auto_size,
    )

    with open(f'{CONFIG_PATH}/{uid}.toml', 'w') as f:
        toml.dump(config, f)
    
    
    #cmd = f"python -m MetaLogo.entry --config {CONFIG_PATH}/{uid}.toml &"
    #print(cmd)
    #os.system(cmd)

    enqueue(f"{CONFIG_PATH}/{uid}.toml")

    return '','','',False,f'finished{uid}'
    