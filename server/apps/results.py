# -*- coding: utf-8 -*-
#!/usr/bin/env python

from re import search
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import flask
from dash.dependencies import Input, Output, State
import os

from ..app import app
from .analysis import CONFIG_PATH


uid_input = dbc.FormGroup(
    [
        dbc.Label("Please input the job ID and click the Search button",html_for='input'),
        dbc.Input(type="string", id="uid_input"),
    ])
search_btn = html.Div(
            [dbc.Button("Check", color='primary',id='search_btn',n_clicks=0)],
            style={'marginTop':'20px','textAlign':'right'})

not_found_panel = html.Div(
    [html.Span('Task id not found, please make sure it exists', id='not_found_span')], style={'fontSize':'25px','color':'#ff3400','margin':'20px'}
)
running_panel = html.Div(
    [html.Span('The task is running, please check it later.',id='running_span')],style={'fontSize':'25px','color':'#092eff','margin':'20px'}
)
label_style = {
    'background':'#80808021',
    'borderRadius':'5px',
    'margin':'5px',
    'padding':'5px',
    'fontSize':'10px',
}

value_style = {
    'marigin' : '5px',
}

task_info_panel = dbc.Card(
    [
        dbc.CardHeader("Task info and parameters"),
        dbc.CardBody(
            [
                dbc.Col([
                    dbc.Row([
                        dbc.Col([html.Span('ID',style=label_style), html.Span('ffdee00f-24a8-4501-8e45-5d8327ce97d8',style=value_style, id='uid_span')]) ,
                        dbc.Col([html.Span('Created Time',style=label_style), html.Span('2021/2/3, 15:00',style=value_style)]),
                    ]),
                    html.Hr(),
                    dbc.Row([
                        dbc.Col([html.Span('Input Format',style=label_style), html.Span('auto',style=value_style)]),
                        dbc.Col([html.Span('Sequence Type',style=label_style), html.Span('auto',style=value_style)]),
                        dbc.Col([html.Span('Group Strategy',style=label_style), html.Span('auto',style=value_style)]),
                        dbc.Col([html.Span('Grouping Resolution ',style=label_style), html.Span('auto',style=value_style)]),
                    ],style={'marginTop':'10px'}),
                    dbc.Row([
                        dbc.Col([html.Span('Minimum Length ',style=label_style), html.Span('auto',style=value_style)]),
                        dbc.Col([html.Span('Maximum Length ',style=label_style), html.Span('auto',style=value_style)]),
                        dbc.Col([html.Span('Display Range (left) ',style=label_style), html.Span('auto',style=value_style)]),
                        dbc.Col([html.Span('Display Range (right) ',style=label_style), html.Span('auto',style=value_style)]),
                    ],style={'marginTop':'10px'})
                ], style={'display':'tableCell','verticalAlign':'middle',})
            ]
        )
    ],style={'marginBottom':'10px'},id='task_info_panel'
)

seqlogo_panel = dbc.Card(
    [
        dbc.CardHeader("Sequence Logo"),
        dbc.CardBody(
            [
            ]
        )
    ],style={'marginBottom':'10px'},id='seqlogo_panel'
)

statistics_panel = dbc.Card(
    [
        dbc.CardHeader("Statistics Figures"),
        dbc.CardBody(
            [
            ]
        )
    ],style={'marginBottom':'10px'},id='statistics_panel'
)
btn_style = {'maring':'10px'}
download_panel = dbc.Card(
    [
        dbc.CardHeader("Download Files"),
        dbc.CardBody(
            [
                dbc.Col([
                    dbc.Row([
                        dbc.Col(dbc.Button(
                            "Config File",   color='info',style=btn_style
                        )),
                        dbc.Col(dbc.Button(
                            "Sequence Logo",   color='info',style=btn_style
                        )),
                        dbc.Col(dbc.Button(
                            "Sequence input",   color='info',style=btn_style
                        ))], style={'margin':'20px'}),
                    dbc.Row([
                        dbc.Col(dbc.Button(
                            "MSA result",   color='info',style=btn_style
                        )),
                        dbc.Col(dbc.Button(
                            "Phylogenetic Tree",   color='info',style=btn_style
                        )),
                        dbc.Col(dbc.Button(
                            "Grouping result",   color='info',style=btn_style
                        ))],style={'margin':'20px'})
                ])
            ]
        )
    ],style={'marginBottom':'10px'},id='download_panel'
)
trigger_panel = html.Span('',style={'display':'none'},id='trigger_panel')

loading_spinner = html.Div(
    [
        dbc.Spinner(html.Div(id="loading-output2"),fullscreen=True,fullscreen_style={"opacity":"0.8"}),
    ]
)
layout = dbc.Container(children=[
        html.Hr(),
        uid_input,
        search_btn,
        html.Hr(),
        not_found_panel,
        running_panel,
        html.Div([
            task_info_panel,
            seqlogo_panel,
            statistics_panel,
            download_panel,
            trigger_panel
        ],id='result_panel'),
        loading_spinner
])


@app.callback(
            [Output('uid_input', 'value'),
             Output('trigger_panel','children')
            ],
            [Input('url', 'pathname'),
             Input('search_btn','n_clicks'),
             ],
            State('uid_input','value'))
def display_page(pathname,nclicks,uid_input):

    if nclicks > 0:
        return uid_input, uid_input
    if ('/results' in pathname) and (not pathname == '/results'):
        return pathname.split('/')[-1], pathname.split('/')[-1]
    else:
        return '',''

@app.callback(
    [
        Output("loading-output2", "children"),
        Output('uid_span','children') ,
        Output('not_found_span','style'),
        Output('running_span','style'),
        Output('result_panel','style'),
    ],
    [
        Input('trigger_panel','children'),
    ])
def trigger(uid):
    print('changed!!!!')
    results_arr = ['',uid]

    if not os.path.exists(f'{CONFIG_PATH}/{uid}.toml'):
        results_arr += [{},{'display':'none'},{'display':'none'}]
    else:
        results_arr += [{'display':'none'},{'display':'none'},{}]

    return results_arr