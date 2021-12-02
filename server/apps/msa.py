# -*- coding: utf-8 -*-
#!/usr/bin/env python

import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import dash_bio as dashbio
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from ..app import app
from ..config import CONFIG_PATH, SQLITE3_DB, PNG_PATH, FA_PATH
import os
import re

loading_spinner = html.Div(
    [
        dbc.Spinner(html.Div(id="loading-output3"), fullscreen=True,
                    fullscreen_style={"opacity": "0.8"}),
        dbc.Spinner(html.Div(id="loading-output4"), fullscreen=True,
                    fullscreen_style={"opacity": "0.8"}),
    ]
)
checklist = dbc.FormGroup(
    [
        dbc.Label("Control the panel"),
        dbc.Checklist(
            options=[
                {"label": "Conservation", "value": 'conservation'},
                {"label": "Gaps", "value": 'gaps'},
                {"label": "Overview", "value": 'overview'},
                {"label": "Consensus", "value": 'consensus'},
            ],
            value=[],
            id="checklist",
            inline=True,
        ),
    ]
)
layout = dbc.Container([
    html.H3([html.Span("MSA result for task "),html.A(id="uid")]),
    dbc.Col(
        dbc.Row([
            checklist,
        ])
    ),
    dbc.Col(
        [
            dbc.Row([
                dashbio.AlignmentChart(
                id='my-default-alignment-viewer',
                data='>a\nA',
                height=1200,
                width="100%",
                showgap=False,
                #showconservation=False,
                #showconsensus=False,
                tilewidth=30,
                overview='slider'
            )]),
            dbc.Row([html.Div(id='default-alignment-viewer-output',style={'display': 'none'})]),
        ]
    ),
    loading_spinner
])


def get_values(checklist):
    arr = []
    if 'gaps' in checklist:
        arr.append(True)
    else:
        arr.append(False)
    if 'conservation' in checklist:
        arr.append(True)
    else:
        arr.append(False)
    if 'consensus' in checklist:
        arr.append(True)
    else:
        arr.append(False)
    if 'overview' in checklist:
        arr.append('slider')
    else:
        arr.append('none')
    return arr

@app.callback(
              [
                Output('my-default-alignment-viewer', 'data'), 
                Output('my-default-alignment-viewer', 'height'), 
                Output("loading-output3", "children"),
                Output("uid","children"),
                Output("uid","href"),
                Output('my-default-alignment-viewer','showgap'),
                Output('my-default-alignment-viewer','showconservation'),
                Output('my-default-alignment-viewer','showconsensus'),
                Output('my-default-alignment-viewer','overview')
              ],
              [
                  Input('url', 'pathname'),
                  Input('checklist','value')
              ],
              [
                  State('my-default-alignment-viewer','data'),
                  State('my-default-alignment-viewer','height'),
              ]
              )

def display_page(pathname,checklist,data,height):
    arrs = pathname.split('/msa/')
    return_arrs = []

    ctx = dash.callback_context
    print(ctx.triggered)
    example_id = ''
    if ctx.triggered:
        example_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if len(arrs) > 1:
        uid = arrs[-1]
        if example_id != 'checklist': 
            msa_file = f'{FA_PATH}/server.{uid}.msa.rawid.fa'
            if not os.path.exists(msa_file):
                return_arrs = ["",100,'',uid,'/results/'+uid]
            else:
                with open(msa_file, encoding='utf-8') as data_file:
                    data = data_file.read()
                line_no = len(re.findall('\n',data))/2
                return_arrs = [data, line_no*20,'',uid,'/results/'+uid]
            return_arrs += [False,False,False,'none']
        else:
            vals = get_values(checklist)
            c = 0
            for v in vals:
                if v:
                    c+= 1
            if vals[-1] != 'none':
                c += 1
            return_arrs = [data,height,'',uid,'/results/'+uid] + vals
        return return_arrs
    else:
        return '','','','','','','','',''


@app.callback(
    Output('default-alignment-viewer-output', 'children'),
    #Output("loading-output4", "children")],
    Input('my-default-alignment-viewer', 'eventDatum')
)
def update_output(value):
    if value is None:
        return 'No data.'#,''
    else:
        return str(value)#,''
