# -*- coding: utf-8 -*-
#!/usr/bin/env python

from re import search
from sys import getallocatedblocks
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import flask
from dash.dependencies import Input, Output, State
import os

from ..app import app
from .analysis import CONFIG_PATH, SQLITE3_DB

from contextlib import closing
import sqlite3
from dash.exceptions import PreventUpdate



def get_status(uid):
    with closing(sqlite3.connect(SQLITE3_DB)) as connection:
        with closing(connection.cursor()) as cursor:
            cursor.execute("create table if not exists metalogo_server (uid TEXT primary key, status TEXT, created INTEGER, finished INTEGER )")
            rows = cursor.execute(f"SELECT uid, status FROM metalogo_server WHERE uid = '{uid}'").fetchall()
            if len(rows) == 1:
                return rows[0][1]
            else:
                return 'not found'
    

def get_layout():
    uid_input = dbc.FormGroup(
        [
            dbc.Label("Please input the job ID and click the Search button",html_for='input'),
            dbc.Input(type="string", id="uid_input"),
        ])
    search_btn = html.Div(
                [dbc.Button("Check", color='primary',id='search_btn',n_clicks=0)],
                style={'marginTop':'20px','textAlign':'right'})

    not_found_panel = html.Div(
        [html.Span('Task id not found, please input the right id and click the check button', id='not_found_span', style={'display':'none'})], style={'fontSize':'25px','color':'#ff3400','margin':'20px'}
    )
    running_panel = html.Div(
        [
            html.Span(
                [
                    html.Div('The task is running, please check it later.'), 
                    html.Div(
                        [ 
                            html.Span('The page will be refreshed after '),
                            html.Span('10',id='refresh_count',style={'color':'red'}),
                            html.Span(' seconds')
                        ],style={'fontSize':'5px'})
                ],
                id='running_span',style={'display':'none'})],
                style={'fontSize':'25px','color':'#092eff','margin':'20px'}
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
            ],id='result_panel',style={"display":"none"}),
            loading_spinner,
            dcc.Interval(
                id='interval-component',
                interval=1000,
                n_intervals=0
            )
    ])

    return layout


@app.callback(
                Output('uid_input', 'value'),
                Input('url', 'pathname'),
            )
def display_page(pathname):

    if ('/results' in pathname) and (not pathname == '/results'):
        return pathname.split('/')[-1]
    else:
        return ''

@app.callback(
    Output("url","pathname"),
    Input('search_btn','n_clicks'),
    State('uid_input','value'), prevent_initial_call=True
)
def navigate(n_clicks,uid):
    if n_clicks > 0:
        return f'/results/{uid}'
    else:
        raise PreventUpdate

def get_left_time(n_intervals):

    if n_intervals <= 60:
        left = (10 - n_intervals%10)%10
        return left
    if n_intervals <= 600:
        left = (60 - n_intervals%60)%60
        return left
    return (60*10 - n_intervals%(60*10))%(60*10)


LOADED = False

@app.callback(
    Output("trigger_panel","children"),
    Input("interval-component","n_intervals"),
    State("trigger_panel","children")
)
def fire_trigger(n_intervals,old_trigger):
    if n_intervals == 0:
        return old_trigger + 'x'
    left = get_left_time(n_intervals)
    if left == 0 and (not LOADED):
        return old_trigger + 'x'
    else:
        raise PreventUpdate



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
    ],
        State('url','pathname')
    )
def trigger(uid,pathname):

    if ('/results' in pathname) and (not pathname == '/results'):
        uid = pathname.split('/')[-1]
    else:
        uid = ''

    results_arr = ['',uid]
    status = get_status(uid)

    global LOADED

    if status == 'not found':
        LOADED = True
        results_arr += [{},{'display':'none'},{'display':'none'}]
    elif status == 'running':
        LOADED = False
        results_arr += [{'display':'none'},{},{'display':'none'}]
    elif status == 'finished':
        results_arr += [{'display':'none'},{'display':'none'},{}]
        LOADED = True
    else:
        LOADED = True
    
    return results_arr


@app.callback(
    Output("refresh_count","children"),
    Input("interval-component","n_intervals")
)
def count_time(n_intervals):
    global LOADED
    if LOADED:
        raise PreventUpdate
    left = get_left_time(n_intervals)
    return left

   

layout = get_layout()