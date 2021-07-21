# -*- coding: utf-8 -*-

# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State

from handle_seqs import handle_seqs_str,handle_seqs_file
from handle_seqs import save_seqs
import uuid
import os
import time

from flask import Flask, send_from_directory



import plotly.express as px
import pandas as pd
from matplotlib import pyplot as plt
import sys
from plotly.tools import mpl_to_plotly
from io import BytesIO
import base64

def fig_to_uri(in_fig, close_all=True, **save_args):
    # type: (plt.Figure) -> str
    """
    Save a figure as a URI
    :param in_fig:
    :return:
    """
    out_img = BytesIO()
    in_fig.savefig(out_img, format='png', **save_args)
    if close_all:
        in_fig.clf()
        plt.close('all')
    out_img.seek(0)  # rewind file
    encoded = base64.b64encode(out_img.read()).decode("ascii").replace("\n", "")
    return "data:image/png;base64,{}".format(encoded)


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

#app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app = dash.Dash(
    __name__,
    title="Modern Sequence Logo",
    external_stylesheets=[dbc.themes.BOOTSTRAP]
)
app.title = "Modern Sequence Logo"


nav = dbc.Nav(
    [
        dbc.NavItem(dbc.NavLink("Tutorial",  href="#")),
        dbc.NavItem(dbc.NavLink("Python package", href="#")),
        dbc.NavItem(dbc.NavLink("Github", href="#")),
        dbc.NavItem(dbc.NavLink("Paper",  href="#")),
        dbc.NavItem(dbc.NavLink("Lab",  href="#")),
        dbc.NavItem(dbc.NavLink("Feedback",  href="#")),
    ]
)
toppanel = html.Div(
    [
        dbc.Row([
            dbc.Col(html.H1(['Modern Sequence Logo'])),
            ],
        ),
        dbc.Row(nav)
    ]
)

input_format_dropdown = dbc.FormGroup(
    [
        dbc.Label("Input Format", html_for="dropdown"),
        dcc.Dropdown(
            id="input_format_dropdown",
            options=[
                {"label": "Fasta", "value": 'Fasta'},
                {"label": "Fastq", "value": 'Fastq'}
            ],
            value='Fasta'
        ),
    ]
)

sequence_type_dropdown = dbc.FormGroup(
    [
        dbc.Label("Sequence Type", html_for="dropdown"),
        dcc.Dropdown(
            id="sequence_type_dropdown",
            options=[
                {"label": "Auto", "value": 'Auto'},
                {"label": "DNA", "value": 'DNA'},
                {"label": "Protein", "value": 'Protein'},
            ],
            value='Auto'
        ),
    ]
)
grouping_by_dropdown = dbc.FormGroup(
    [
        dbc.Label("Grouping By", html_for="dropdown"),
        dcc.Dropdown(
            id="grouping_by_dropdown",
            options=[
                {"label": "Length", "value": 'length'},
                {"label": "Seq identifier", "value": 'identifier'},
            ],
            value='length'
        ),
    ]
)
max_len_input = dbc.FormGroup(
    [
        dbc.Label("Maximum length",html_for='input'),
        dbc.Input(type="number", min=0, max=100, step=1, value=20, id="max_len_input"),
    ]
)

min_len_input = dbc.FormGroup(
    [
        dbc.Label("Minimum length",html_for='input'),
        dbc.Input(type="number", min=0, max=100, step=1, value=10,id="min_len_input"),
    ]
)

seqinput_form = html.Div([
    html.Label('Paste sequences (<= 50,000 sequences)'),
    dcc.Textarea(
        placeholder='',
        value='',
        style={'width': '100%'},
        id = 'seq_textarea'
    ),  
    html.Label('Or upload a file (<=5MB)'),
    html.Label('',id='uploaded_label2',style={"color":"orange"}),
    html.Label('',id='uploaded_label',style={"color":"#11FF00"}),
    dcc.Upload([
        html.Div('Drag and Drop or Select a File',n_clicks=0,id='upload_div')
        ], 
        max_size = 1024 * 1024 * 5,
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


input_panel = dbc.Card(
    [
        dbc.CardHeader("Step1. Input data"),
        dbc.CardBody(
            [
                dbc.Row([
                    dbc.Col(input_format_dropdown),
                    dbc.Col(sequence_type_dropdown),
                    dbc.Col(grouping_by_dropdown),
                    dbc.Col(min_len_input),
                    dbc.Col(max_len_input),
                ]),
                dbc.Row(dbc.Col(seqinput_form)),
                dbc.Row([dbc.Col(''),dbc.Col(input_submit)],justify='end'),

            ]
        )
    ],style={'marginBottom':'10px'}
)

algrithm_panel = dbc.Card([
    dbc.CardHeader("Step2. Choose Algrithm"),
    dbc.CardBody()
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
                {"label": "Three Dimensional", "value": 'Threed'},
            ],
            value='Horizontal'
        ),
    ]
)

align_dropdown = dbc.FormGroup(
    [
        dbc.Label("Align logos?", html_for="dropdown"),
        dcc.Dropdown(
            id="align_dropdown",
            options=[
                {"label": "Yes", "value": 'Yes'},
                {"label": "No", "value": 'No'}
            ],
            value='Yes'
        ),
    ]
)
sort_dropdown = dbc.FormGroup(
    [
        dbc.Label("Sort by", html_for="dropdown"),
        dcc.Dropdown(
            id="sortby_dropdown",
            options=[
                {"label": "Length", "value": 'Length'},
                {"label": "Length reverse", "value": 'Length_rev'},
                {"label": "Group Id", "value": 'group_id'},
                {"label": "Group Id reverse", "value": 'group_id_rev'},
            ],
            value='Length'
        ),
    ]
)

logo_margin_input = dbc.FormGroup(
    [
        dbc.Label("Logo margin ratio",html_for='input'),
        dbc.Input(type="number", min=0, max=1, step=0.01, value=0.1,id="logo_margin_input"),
    ]
)

column_margin_input = dbc.FormGroup(
    [
        dbc.Label("Column margin ratio",html_for='input'),
        dbc.Input(type="number", min=0, max=1, step=0.01, value=0.05,id="column_margin_input"),
    ]
)

character_margin_input = dbc.FormGroup(
    [
        dbc.Label("Character margin ratio",html_for='input'),
        dbc.Input(type="number", min=0, max=1, step=0.01, value=0.05,id="char_margin_input"),
    ]
)
layout_submit =  html.Div(
    [
        dbc.Button(
            "Submit", id="submit2",  color='info'
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
                    dbc.Col(sort_dropdown),
                    dbc.Col(align_dropdown)
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
        dbc.Label("X,Y axis"),
        dbc.Checklist(
            options=[
                {"label": "Show X", "value": 'showx'},
                {"label": "Show Y", "value": 'showy'},
            ],
            value=['showx','showy'],
            id="showxy_check_input",
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
width_input = dbc.FormGroup(
    [
        dbc.Label("Figure Width (inch)",html_for='input'),
        dbc.Input(type="number", min=1, max=20, value=10,id="width_input"),
    ]
)
height_input = dbc.FormGroup(
    [
        dbc.Label("Figure Height (inch)",html_for='input'),
        dbc.Input(type="number", min=1, max=20, value=10, id="height_input")
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
        dbc.Label("Grid background"),
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
download_format_dropdown = dbc.FormGroup(
    [
        dbc.Label("Download Format", html_for="dropdown"),
        dcc.Dropdown(
            id="download_format_dropdown",
            options=[
                {"label": "PNG", "value": 'PNG'},
                {"label": "PDF", "value": 'PDF'}
            ],
            value='PNG'
        ),
    ]
)
color_scheme_dropdown = dbc.FormGroup(
    [
        dbc.Label("Color Scheme", html_for="dropdown"),
        dcc.Dropdown(
            id="color_dropdown",
            options=[
                {"label": "DNA Basic", "value": 'dna_basic'},
                {"label": "Protein Basic", "value": 'protein_basic'},
                {"label": "Custom (click color pickers to choose)", "value": 'Custom'},
            ],
            value='dna_basic'
        ),
    ]
)
#generate dna basic scheme
dna_basic_scheme = {'A':'#009980','T':'#1A1A1A','G':'#E69B04','C':'#59B3E6','N':'grey'}
dna_basic_spans = []
for base in 'ATGCN':
    dna_basic_spans.append(html.Span(base,id=f"basic_dna_{base}",
                    style = {
                             "verticalAlign": "middle","color":dna_basic_scheme[base],
                            "fontSize":"40px","fontWeight":"bold","padding":"20px"
                            }
    ))
dna_basic_panel = html.Div(dna_basic_spans)

protein_basic_scheme = {'A':'#009980','T':'#1A1A1A','G':'#E69B04','C':'#59B3E6','N':'grey'}
protein_basic_spans = []
for aa in 'ARNDCQEGHILKMFPSTWYV':
    protein_basic_spans.append(html.Span(aa,id=f"basic_protein_{aa}",
                    style = {
                             "verticalAlign": "middle","color":protein_basic_scheme.get(aa,'grey'),
                            "fontSize":"40px","fontWeight":"bold","padding":"20px"
                            }
    ))
protein_basic_panel = html.Div(protein_basic_spans)

custom_basic_scheme = {}
custom_basic_groups = []
for alphabet in ['A','R','N','D','C','Q','E','G','H','I','L','K','M','F','P','S','T','W','Y','V','-']:
    colorpicker = dbc.Col(
        dbc.FormGroup(
        [
            dbc.Label(alphabet, style={"fontWeight":"bold"}),
            dbc.Input(
                type="color",
                id=f"colorpicker_{alphabet}",
                value="#000000",
                style={"width": 50, "height": 50, "margin":"auto"},
            ),
        ],style={"textAlign":"center"}
        )
    )
    custom_basic_groups.append(colorpicker)

style_submit =  html.Div(
    [
        dbc.Button(
            "Submit", id="submit3",  color='primary'
        ),
        html.Div("* Submit the job to our server and wait for results", 
                    style={"fontSize":"10px","verticalAlign": "middle"}),
    ],
    style={'marginTop':'10px','textAlign':'right'}
)

style_panel = dbc.Card(
    [
        dbc.CardHeader("Step4. Set Output Style"),
        dbc.CardBody(
            [
                dbc.Row([
                    dbc.Col(xlabel_input),
                    dbc.Col(ylabel_input),
                    dbc.Col(width_input),
                    dbc.Col(height_input),
                    ]),
                dbc.Row([
                    dbc.Col(showxy_checklist),
                    dbc.Col(show_groupid_checklist),
                    dbc.Col(show_grid_checklist),
                    dbc.Col(download_format_dropdown),
                ]),
                dbc.Row([
                    dbc.Col(color_scheme_dropdown),
                ]),
                dbc.Row([
                    dbc.Col(dna_basic_panel)
                ],id='dna_basic_panel'),
                dbc.Row([
                    dbc.Col(protein_basic_panel)
                ],id='protein_basic_panel'),
                dbc.Row(
                    custom_basic_groups
                ,style={'padding':'20px'},id='custom_basic_groups'),

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
result_panel = dbc.Card(
    [
        dbc.CardHeader("Result",style={'fontWeight':'bold'}),
        dbc.CardBody(
            [
                dbc.Row([
                    html.Img(id='img_res',src='',style={"width":"100%","margin":"auto"}),
                    ]),
                dbc.Row([
                    dbc.Col([
                        dbc.Button("Download Figure", id="download_btn",active=False,disabled=True), 
                        dcc.Download(id="download_png",type='image/png')
                    ], style={'textAlign':'center','margin':'auto'})
                ]),
            ]
        )
    ], style={'marginTop':'20px'}
)

footer_panel = html.Div([
    dbc.Row([
        dbc.Col(['© Developed by Yaowen Chen @ Beijing Institute of Basic Medical Sciences by using ', 
                html.A('Matplotlib',href='https://matplotlib.org/'),' and ', html.A('Plotly Dash',href='https://dash.plotly.com/')],
                )
    ]),
    dbc.Row(dbc.Col('Jun, 2021'))
],style={"textAlign":"center","marginTop":"40px","fontSize":"10px","color":"grey"})



app.layout = dbc.Container(children=[
        toppanel,
        html.Hr(),
        input_panel,
        algrithm_panel,
        layout_panel,
        style_panel,
        result_panel,
        footer_panel,
        modal,
        result_modal,
        loading_spinner,
        html.Div('',id='functional_garbage'),
        html.Div('',id='garbage',style={'display':'none'}),
       ])







#@app.callback(Output('modal','is_open'), Input('modal_close','n_clicks'))
#def close_modal(n):
#    return False

@app.callback(Output("seq_textarea","placeholder"), Input("input_format_dropdown","value"))
def change_placeholder(input_format):
    return f"Input sequences as {input_format} format"


@app.callback(Output("dna_basic_panel", "style"), Input("color_dropdown", "value"))
def hidden(color_scheme):
    if color_scheme == 'dna_basic':
        return {"display":""}
    else:
        return {"display":"none"}

@app.callback(Output("protein_basic_panel", "style"), Input("color_dropdown", "value"))
def hidden(color_scheme):
    if color_scheme == 'protein_basic':
        return {"display":""}
    else:
        return {"display":"none"}

@app.callback(Output("custom_basic_groups", "style"), Input("color_dropdown", "value"))
def hidden(color_scheme):
    if color_scheme == 'Custom':
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


@app.callback(Output('uploaded_label', 'children'),
              Input('file_upload', 'contents'),
              State('file_upload', 'filename'),
              State('file_upload', 'last_modified'))
def update_output(content, name, date):
    if content is not None:
        print('in callback1',name,date)
        return f"√ {name} uploaded!"

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
    [Output("download_btn","active"),Output("download_btn","disabled")],
    Input("functional_garbage","children")
)
def show_btn(uid):
    if (uid is not None) and (len(uid) > 0):
        return True,False
    else:
        return False,True

@app.callback(
    [
        Output("download_png","data"),
    ],
    [
        Input("download_btn","n_clicks")
    ],
    [
        State("functional_garbage","children"),
        State('img_res', 'src'),
    ],prevent_initial_call=True,
    )
def udpate_download(n_clicks,uid,src):
    if len(uid) > 0:
        return [dict(
                base64=True,
                content=src.split('base64,')[1],
                filename=f'{uid}.png'
            )]



@app.callback(
    [
        Output("loading-output", "children"),
        Output('modal_header', 'children'),
        Output('modal_body', 'children'),
        Output('modal', 'is_open'),
        Output('img_res', 'src'),
        Output('functional_garbage','children')
    ],
    [
        Input('submit1', 'n_clicks'),
        Input('submit2', 'n_clicks'),
        Input('submit3', 'n_clicks')
    ],
    [
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
        State('logo_margin_input', 'value'),
        State('column_margin_input', 'value'),
        State('char_margin_input', 'value'),
        State('xlabel_input','value'),
        State('ylabel_input','value'),
        State('width_input','value'),
        State('height_input','value'),
        State('showid_check_input','value'),
        State('showgrid_check_input','value'),
        State('showxy_check_input','value'),
        State('download_format_dropdown','value'),
        State('color_dropdown','value'),
    ] + [State(f'colorpicker_{base}', 'value') for base in ['A','R','N','D','C','Q','E','G','H','I','L','K','M','F','P','S','T','W','Y','V','-']],
    prevent_initial_call=True
)
def submit(nclicks1,nclicks2,nclicks3,input_format_dropdown, sequence_type_dropdown, grouping_by_dropdown, max_len_input, min_len_input,
            seq_textarea, file_upload_content, logo_shape_dropdown, sortby_dropdown,align_dropdown,logo_margin_input, column_margin_input,
            char_margin_input, xlabel_input, ylabel_input, width_input, height_input, showid_check_input, showgrid_check_input,
            showxy_check_input, download_format_dropdown, color_dropdown, *args):
    print('in submit')

    if max_len_input < min_len_input:
        return '','Error','Maximum length < Minimum length',True,'',''
    
    if (len(seq_textarea) == 0) and (file_upload_content is None):
        return '','Error','Please paste sequences into the textarea or upload a fasta/fastq file',True,'',''
    #time.sleep(50)
    seqs = []
    if file_upload_content is not None:
        response = handle_seqs_file(file_upload_content,format=input_format_dropdown,sequence_type=sequence_type_dropdown)
        if not response['successful']:
            return '','Error',response['msg'],True,'',''
        seqs = response['res']['seqs']
    elif len(seq_textarea) != 0:
        response = handle_seqs_str(seq_textarea,format=input_format_dropdown,sequence_type=sequence_type_dropdown)
        if not response['successful']:
            return '','Error',response['msg'],True,'',''
        seqs = response['res']['seqs']

    if sum([((len(seq) >= min_len_input) and (len(seq) <= max_len_input)) for name,seq in seqs]) == 0:
        return '','Error','Detect no sequences with limited lengths',True,'',''

    uid = str(uuid.uuid4())
    seq_file = f"tmp/server-{uid}.fasta"
    save_seqs(seqs, seq_file)

    align = align_dropdown == 'Yes'

    os.system(f'cd ../..;\
                python -m vllogo.entry --input_file vllogo/dash/{seq_file}  --input_file_type {input_format_dropdown}\
                --type  {logo_shape_dropdown}  --group_strategy {grouping_by_dropdown} \
                --max_length {max_len_input} --min_length {min_len_input}  --align {align} \
                --output_name {uid}.png \
                ')
    png = f'../../test/{uid}.png'
    
    encoded_image = base64.b64encode(open(png, 'rb').read())
    src = 'data:image/png;base64,{}'.format(encoded_image.decode())


    return '','','',False,src,uid

if __name__ == '__main__':
        app.run_server(debug=True)

