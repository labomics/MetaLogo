# -*- coding: utf-8 -*-
#!/usr/bin/env python

from re import search
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import flask

from ..app import app

uid_input = dbc.FormGroup(
    [
        dbc.Label("Please input the job ID and click the Search button",html_for='input'),
        dbc.Input(type="string", id="uid_input"),
    ])
search_btn = html.Div(
            [dbc.Button("Check", color='info')],
            style={'marginTop':'20px','textAlign':'right'})

layout = dbc.Container(children=[
        html.Hr(),
        uid_input,
        search_btn,
        html.Hr(),

])


@app.callback(Output('uid_input', 'value'),
              Input('url', 'pathname'))
def display_page(pathname):

    print(flask.request.args)
    return pathname
