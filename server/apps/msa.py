# -*- coding: utf-8 -*-
#!/usr/bin/env python

import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import dash_bio as dashbio
from dash.dependencies import Input, Output, State
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

layout = dbc.Container([
    html.H3([html.Span("MSA result for task "),html.A(id="uid")]),
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
                #overview='none'
            )]),
            dbc.Row([html.Div(id='default-alignment-viewer-output',style={'display': 'none'})]),
        ]
    ),
    loading_spinner
])


@app.callback(
              [
                Output('my-default-alignment-viewer', 'data'), 
                Output('my-default-alignment-viewer', 'height'), 
                Output("loading-output3", "children"),
                Output("uid","children"),
                Output("uid","href"),
              ],
              Input('url', 'pathname'),
              )

def display_page(pathname):
    arrs = pathname.split('/msa/')
    if len(arrs) > 1:
        uid = arrs[-1]
        msa_file = f'{FA_PATH}/server.{uid}.msa.rawid.fa'
        if not os.path.exists(msa_file):
            return "",100,'',uid,'/results/'+uid

        with open(msa_file, encoding='utf-8') as data_file:
            data = data_file.read()
        line_no = len(re.findall('\n',data))/2
        return data, line_no*15,'',uid,'/results/'+uid
    else:
        return '','','',''


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
