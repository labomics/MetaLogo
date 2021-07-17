# -*- coding: utf-8 -*-

# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State




import plotly.express as px
import pandas as pd
from matplotlib import pyplot as plt
import sys
#sys.path.insert(0,'..')
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
app = dash.Dash(__name__,external_stylesheets=[dbc.themes.BOOTSTRAP])

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
                {"label": "Length", "value": 'Length'},
                {"label": "Seq identifier", "value": 'identifier'},
            ],
            value='Length'
        ),
    ]
)
max_len_input = dbc.FormGroup(
    [
        dbc.Label("Maximum length",html_for='input'),
        dbc.Input(type="number", min=0, max=100, step=1, value=20),
    ],
    id="max_len_input",
)

min_len_input = dbc.FormGroup(
    [
        dbc.Label("Minimum length",html_for='input'),
        dbc.Input(type="number", min=0, max=100, step=1, value=10),
    ],
    id="min_len_input",
)

seqinput_form = html.Div([
    html.Label('Paste sequences'),
    dcc.Textarea(
        placeholder='Input sequences as Fasta/Fastq format',
        value='',
        style={'width': '100%'}
    ),  
    html.Label('Or upload a file (<= 50,000 sequences)'),
    dcc.Upload([
        'Drag and Drop or ',
        html.A('Select a File')
    ], style={
        'width': '100%',
        'height': '60px',
        'lineHeight': '60px',
        'borderWidth': '1px',
        'borderStyle': 'dashed',
        'borderRadius': '5px',
        'textAlign': 'center'
    }),
])
input_submit =  html.Div(
    [
        dbc.Button(
            "Submit", id="example-button",  color='info'
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
                {"label": "Seq identifier", "value": 'Seq_iden'},
            ],
            value='Length'
        ),
    ]
)

logo_margin_input = dbc.FormGroup(
    [
        dbc.Label("Logo margin ratio",html_for='input'),
        dbc.Input(type="number", min=0, max=1, step=0.01, value=0.1),
    ],
    id="logo_margin_input",
)

column_margin_input = dbc.FormGroup(
    [
        dbc.Label("Column margin ratio",html_for='input'),
        dbc.Input(type="number", min=0, max=1, step=0.01, value=0.05),
    ],
    id="column_margin_input",
)

character_margin_input = dbc.FormGroup(
    [
        dbc.Label("Character margin ratio",html_for='input'),
        dbc.Input(type="number", min=0, max=1, step=0.01, value=0.05),
    ],
    id="char_margin_input",
)
layout_submit =  html.Div(
    [
        dbc.Button(
            "Submit", id="example-button2",  color='info'
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
            id="checklist-inline-input",
            inline=True,
        ),
    ]
)
xlabel_input = dbc.FormGroup(
    [
        dbc.Label("Xlabel",html_for='input'),
        dbc.Input(type="str",  value='Position'),
    ],
    id="xlabel_input",
)
ylabel_input = dbc.FormGroup(
    [
        dbc.Label("Ylabel",html_for='input'),
        dbc.Input(type="str",  value='Bits'),
    ],
    id="ylabel_input",
)
width_input = dbc.FormGroup(
    [
        dbc.Label("Figure Width (inch)",html_for='input'),
        dbc.Input(type="number", min=1, max=20, value=10),
    ],
    id="width_input",
)
height_input = dbc.FormGroup(
    [
        dbc.Label("Figure Height (inch)",html_for='input'),
        dbc.Input(type="number", min=1, max=20, value=10),
    ],
    id="height_input",
)
show_groupid_checklist = dbc.FormGroup(
    [
        dbc.Label("Group Label"),
        dbc.Checklist(
            options=[
                {"label": "Show Group Label", "value": 'showid'},
            ],
            value=['showid'],
            id="showid-input",
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
            id="showgrid-input",
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
dna_basic_scheme = {'A':'red','T':'blue','G':'green','C':'orange','N':'grey'}
dna_basic_spans = []
for base in 'ATGCN':
    dna_basic_spans.append(html.Span(base,id=f"basic_dna_{base}",
                    style = {
                             "verticalAlign": "middle","color":dna_basic_scheme[base],
                            "fontSize":"40px","fontWeight":"bold","padding":"20px"
                            }
    ))
dna_basic_panel = html.Div(dna_basic_spans)

protein_basic_scheme = {'A':'red','T':'blue','G':'green','C':'orange','N':'grey'}
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
for alphabet in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ-':
    colorpicker = dbc.Col(
        dbc.FormGroup(
        [
            dbc.Label(alphabet, style={"fontWeight":"bold"}),
            dbc.Input(
                type="color",
                id=f"colorpicker_{alphabet}",
                value="#000000",
                style={"width": 50, "height": 50},
            ),
        ],style={"textAlign":"center"}
        )
    )
    custom_basic_groups.append(colorpicker)

style_submit =  html.Div(
    [
        dbc.Button(
            "Submit", id="style-button",  color='primary'
        ),
        html.Div("* Submit the job to our server and wait for results", 
                    style={"fontSize":"10px","verticalAlign": "middle"}),
    ],
    style={'marginTop':'10px','textAlign':'right'}
)

#https://dash-bootstrap-components.opensource.faculty.ai/docs/components/input/
#app.clientside_callback(
#    Output("color", "style"),
#    Input("color_dropdown", "value"),
#)

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



app.layout = dbc.Container(children=[
        toppanel,
        html.Hr(),
        input_panel,
        algrithm_panel,
        layout_panel,
        style_panel
       ])

if __name__ == '__main__':
        app.run_server(debug=True)

