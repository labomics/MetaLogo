# -*- coding: utf-8 -*-
#!/usr/bin/env python

import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import os
from ..app import app
from ..config import CONFIG_PATH, SQLITE3_DB, PNG_PATH, FA_PATH
from ..utils import get_img_src

loading_spinner = html.Div(
    [
        dbc.Spinner(html.Div(id="loading-output5"), fullscreen=True,
                    fullscreen_style={"opacity": "0.8"}),
    ]
)

layout = dbc.Container([
    html.H3([html.Span("Phylogenetic tree visualization result for task "),html.A(id="tree_uid")]),
    dbc.Col(
        [
            dbc.Row([
                    html.Img(id='tree_img_src',src='',style={"margin":"auto","width":"60%"}),
            ]),
        ]
    ),
    loading_spinner
])

@app.callback(
              [ 
                Output("tree_uid","children"),
                Output("tree_uid","href"),
                Output("tree_img_src","src"),
                Output("loading-output5", "children"),
              ],
              Input('url', 'pathname'),
              )

def display_page(pathname):
    arrs = pathname.split('/tree/')
    if len(arrs) > 1:
        uid = arrs[-1]
        tree_file = f'{PNG_PATH}/{uid}.tree.png'
        if not os.path.exists(tree_file):
            return uid,'/results/'+uid,'',''
        tree_src = get_img_src(tree_file)
        return uid,'/results/'+uid,tree_src,''
    else:
        return '','','',''



