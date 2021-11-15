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
import toml


from ..app import app
from .analysis import CONFIG_PATH, SQLITE3_DB, PNG_PATH,FA_PATH
from ..utils import get_img_src

from contextlib import closing
import sqlite3
from dash.exceptions import PreventUpdate
import base64
import datetime
import re
import pandas as pd




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
            dbc.Label("Please input the job ID and click the Search button",html_for='input',id='input_label'),
            dbc.Input(type="string", id="uid_input"),
        ])
    search_btn = html.Div(
                #[dbc.Button("Check", color='primary',id='search_btn',n_clicks=0)],
                [html.A("Check", href="results",target='_self',id='search_btn')],
                style={'marginTop':'20px','textAlign':'right'})

    not_found_panel = html.Div(
        [html.Span('Task id not found, please input the right id and click the check button', id='not_found_span', style={'display':'none'})], style={'fontSize':'25px','color':'#ff3400','margin':'20px'}
    )

    error_panel = html.Div(
        [html.Span('Task failed', id='error_span', style={'display':'none'})], style={'fontSize':'25px','color':'#ff3400','margin':'20px'}
    )

    running_panel = html.Div(
        [
            html.Span(
                [
                    html.Div([html.Div('The task is still running, please check it later: ',style={'color':'black'}),
                              html.Div('',id='page_url')]), 
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
            dbc.CardHeader("Task info and parameters",style={'fontWeight':'bold'}),
            dbc.CardBody(
                [
                    dbc.Col([
                        dbc.Row([
                            dbc.Col([html.Span('ID',style=label_style), html.Span('ffdee00f-24a8-4501-8e45-5d8327ce97d8',style=value_style, id='uid_span')]) ,
                            dbc.Col([html.Span('Created Time',style=label_style), html.Span('2021/2/3, 15:00',style=value_style, id='create_time')]),
                        ]),
                        html.Hr(),
                        dbc.Row([
                            dbc.Col([html.Span('Input Format',style=label_style), html.Span('auto',style=value_style,id='input_format')]),
                            dbc.Col([html.Span('Sequence Type',style=label_style), html.Span('auto',style=value_style,id='sequence_type')]),
                            dbc.Col([html.Span('Group Strategy',style=label_style), html.Span('auto',style=value_style,id='group_strategy')]),
                            dbc.Col([html.Span('Grouping Resolution ',style=label_style), html.Span('auto',style=value_style,id='group_resolution')]),
                            dbc.Col([html.Span('Clustering method ',style=label_style), html.Span('auto',style=value_style,id='clustering_method_value')]),
                        ],style={'marginTop':'10px'}),
                        dbc.Row([
                            dbc.Col([html.Span('Minimum Length ',style=label_style), html.Span('auto',style=value_style,id='min_len')]),
                            dbc.Col([html.Span('Maximum Length ',style=label_style), html.Span('auto',style=value_style,id='max_len')]),
                            dbc.Col([html.Span('Display Range (left) ',style=label_style), html.Span('auto',style=value_style,id='display_left')]),
                            dbc.Col([html.Span('Display Range (right) ',style=label_style), html.Span('auto',style=value_style,id='display_right')]),
                        ],style={'marginTop':'10px'}),
                        html.Hr(),
                        dbc.Row([
                            dbc.Col([html.Span('* For more details, please download the configure file at the bottom of the result page')],style={'fontSize':'10px'}),
                        ]),
                    ], style={'display':'tableCell','verticalAlign':'middle',})
                ]
            )
        ],style={'marginBottom':'10px'},id='task_info_panel'
    )

    seqlogo_panel = dbc.Card(
        [
            dbc.CardHeader("Sequence Logo",style={'fontWeight':'bold'}),
            dbc.CardBody(
                [
                    dbc.Row([
                        html.Img(id='logo_img',src='',style={"width":"100%","margin":"auto"}),
                    ]),
                ]
            )
        ],style={'marginBottom':'10px'},id='seqlogo_panel'
    )
    statistics_panel = dbc.Card(
        [
            dbc.CardHeader("Statistics Analysis",style={'fontWeight':'bold'}),
            dbc.CardBody(
                [
                    dbc.Row(
                        dbc.Col(
                            html.Span('Figure 1. Sequence counts of each group.')
                    )),
                    dbc.Row([
                        html.Img(id='count_img_res',src='',style={"margin":"auto"}),
                        ]),
                    html.Hr(),
                    dbc.Row(
                        dbc.Col(
                            html.Span('Figure 2. Entropies of each position. ("X"s mean gaps)')
                    )),
                    dbc.Row([
                        html.Img(id='entropy_img_res',src='',style={"margin":"auto"}),
                        ]),
                    html.Hr(),
                    dbc.Row(
                        dbc.Col(
                            html.Span('Figure 3. Entropies distribution of each group.')
                    )),
                    dbc.Row([
                        html.Img(id='entropy_boxplot_img_res',src='',style={"margin":"auto"}),
                        ]),
                    html.Hr(),
                    dbc.Row(
                        dbc.Col(
                            html.Span('Figure 4. Correlations among groups (only in global alignment mode and #groups>1).')
                    )),
                    dbc.Row([
                        html.Img(id='clustermap_img_res',src='',style={"margin":"auto","width":"60%"}),
                        ]),
                    html.Hr(),
                    dbc.Row(
                        dbc.Col(
                            html.Span('Figure 5. Conservation scores for positions of the target sequence by rate4site.')
                    )),
                    dbc.Row([
                        html.Img(id='score_img_res',src='',style={"margin":"auto","width":"60%"}),
                        ]),


                ]
            )
        ], id='statistics_panel', style={'marginBottom':'10px'}
    )

    msa_panel = dbc.Card(
        [
            dbc.CardHeader("Other Results",style={'fontWeight':'bold'}),
            dbc.CardBody(
                [
                    html.Div([
                    html.Span('1. Please click to open '),
                    html.A("MSA visualization", href="/msa",target='_blank',id='msa_btn')
                    ]),
                    html.Div([
                    html.Span('2. Please click to open '),
                    html.A("Phylogenetic tree visualization", href="/tree",target='_blank',id='tree_btn')
                    ])

                ]
            )
        ],style={'marginBottom':'10px'},id='msa_panel'
    )
    btn_style = {'maring':'10px'}
    download_panel = dbc.Card(
        [
            dbc.CardHeader("Download Files",style={'fontWeight':'bold'}),
            dbc.CardBody(
                [
                    dbc.Col([
                        dbc.Row([
                            dbc.Col(
                                [
                                  dbc.Button("Config File", id="config_download_btn", style=btn_style, color='info'), 
                                  dcc.Download(id="config_download",type='text'),
                                ]
                            ),
                            dbc.Col(
                                [
                                    dbc.Button("Sequence Input",   color='info',id='seq_input_download_btn',style=btn_style),
                                  dcc.Download(id="seq_input_download",type='text'),
                                ]

                            ),
                            dbc.Col(
                                [
                                    dbc.Button("Sequence Logo",   color='info',id='seq_logo_download_btn',style=btn_style),
                                  dcc.Download(id="seq_logo_download",type='text',),
                                ]
                            )
                        ], style={'margin':'20px'}),
                        dbc.Row([
                            dbc.Col(
                                [
                                    dbc.Button("MSA result",   color='info',id='msa_download_btn',style=btn_style),
                                    dcc.Download(id="msa_download",type='text',),
                                ]
                            ),
                            dbc.Col(
                                [
                                    dbc.Button("Phylogenetic Tree",   color='info',id='phylo_download_btn',style=btn_style),
                                    dcc.Download(id="phylo_download",type='text',),
                                ]),
                            dbc.Col(
                                [
                                    dbc.Button("Conservation scores",   color='info',id='scores_download_btn',style=btn_style),
                                    dcc.Download(id="scores_download",type='text',),
                                ]),
                            ],style={'margin':'20px'}),
                        dbc.Row([
                            dbc.Col(
                                [
                                    dbc.Button("Grouping details", color='info',id='grouping_download_btn',style=btn_style),
                                    dcc.Download(id="grouping_download",type='text',),
                                ]
                            ),
                            dbc.Col(
                                [
                                    dbc.Button("Grouping clustering",   color='info',id='clustering_download_btn',style=btn_style),
                                    dcc.Download(id="clustering_download",type='text',),
                                ]
                            ),
                            dbc.Col(
                                [
                                    dbc.Button("Sequence name mapping",   color='info',id='mapping_download_btn',style=btn_style),
                                    dcc.Download(id="mapping_download",type='text',),
                                ]
                            )],style={'margin':'20px'})
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
            error_panel,
            running_panel,
            html.Div([
                task_info_panel,
                seqlogo_panel,
                statistics_panel,
                msa_panel,
                download_panel,
                trigger_panel
            ],id='result_panel',style={"display":"none"}),
            loading_spinner,
            dcc.Interval(
                id='interval-component',
                interval=1000,
                n_intervals=0
            ),
            html.Div('',id='garbage3',style={'display':'none'}),
    ])

    return layout

@app.callback(
        Output("config_download","data"),
        Input("config_download_btn","n_clicks"),
        State('url','pathname'),
        prevent_initial_call=True,
    )
def update_config_download(n_clicks,pathname):

    if ('/results' in pathname) and (not pathname == '/results'):
        uid = pathname.split('/')[-1]
    else:
        uid = ''
    target = f"{CONFIG_PATH}/{uid}.toml"
    
    if len(uid) > 0 and n_clicks > 0 and os.path.exists(target):
        return dcc.send_file(target)
    else:
        return None

@app.callback(
        Output("seq_input_download","data"),
        Input("seq_input_download_btn","n_clicks"),
        State('url','pathname'),
        prevent_initial_call=True,
    )
def update_seq_input_download(n_clicks,pathname):
    if ('/results' in pathname) and (not pathname == '/results'):
        uid = pathname.split('/')[-1]
    else:
        uid = ''
    target =  f"{FA_PATH}/server.{uid}.fasta"
    print(target)
    if len(uid) > 0 and n_clicks > 0 and os.path.exists(target):
        return dcc.send_file(target)
    else:
        return None

@app.callback(
        Output("seq_logo_download","data"),
        Input("seq_logo_download_btn","n_clicks"),
        State('url','pathname'),
        prevent_initial_call=True,
    )
def update_logo_input_download(n_clicks,pathname):
    if ('/results' in pathname) and (not pathname == '/results'):
        uid = pathname.split('/')[-1]
    else:
        uid = ''
    target =  f"{PNG_PATH}/{uid}.png"
    print(target)
    if len(uid) > 0 and n_clicks > 0 and os.path.exists(target):
        return dcc.send_file(target)
    else:
        return None

@app.callback(
        Output("msa_download","data"),
        Input("msa_download_btn","n_clicks"),
        State('url','pathname'),
        prevent_initial_call=True,
    )
def update_msa_download(n_clicks,pathname):
    if ('/results' in pathname) and (not pathname == '/results'):
        uid = pathname.split('/')[-1]
    else:
        uid = ''
    target =  f"{FA_PATH}/server.{uid}.msa.fa"
    print(target)
    if len(uid) > 0 and n_clicks > 0 and os.path.exists(target):
        return dcc.send_file(target)
    else:
        return None

@app.callback(
        Output("phylo_download","data"),
        Input("phylo_download_btn","n_clicks"),
        State('url','pathname'),
        prevent_initial_call=True,
    )
def update_phylo_download(n_clicks,pathname):
    if ('/results' in pathname) and (not pathname == '/results'):
        uid = pathname.split('/')[-1]
    else:
        uid = ''
    target =  f"{FA_PATH}/server.{uid}.rate4site.tree"
    print(target)
    if len(uid) > 0 and n_clicks > 0 and os.path.exists(target):
        return dcc.send_file(target)
    else:
        return None

@app.callback(
        Output("scores_download","data"),
        Input("scores_download_btn","n_clicks"),
        State('url','pathname'),
        prevent_initial_call=True,
    )
def update_scores_download(n_clicks,pathname):
    if ('/results' in pathname) and (not pathname == '/results'):
        uid = pathname.split('/')[-1]
    else:
        uid = ''
    target =  f"{FA_PATH}/server.{uid}.rate4site.scores"
    print(target)
    if len(uid) > 0 and n_clicks > 0 and os.path.exists(target):
        return dcc.send_file(target)
    else:
        return None

@app.callback(
        Output("grouping_download","data"),
        Input("grouping_download_btn","n_clicks"),
        State('url','pathname'),
        prevent_initial_call=True,
    )
def update_grouping_download(n_clicks,pathname):
    if ('/results' in pathname) and (not pathname == '/results'):
        uid = pathname.split('/')[-1]
    else:
        uid = ''
    target =  f"{FA_PATH}/server.{uid}.rate4site.cluster"
    print(target)
    if len(uid) > 0 and n_clicks > 0 and os.path.exists(target):
        return dcc.send_file(target)
    else:
        return None

@app.callback(
        Output("clustering_download","data"),
        Input("clustering_download_btn","n_clicks"),
        State('url','pathname'),
        prevent_initial_call=True,
    )
def update_clustering_download(n_clicks,pathname):
    if ('/results' in pathname) and (not pathname == '/results'):
        uid = pathname.split('/')[-1]
    else:
        uid = ''
    target =  f"{PNG_PATH}/{uid}.clustering.png"
    print(target)
    if len(uid) > 0 and n_clicks > 0 and os.path.exists(target):
        return dcc.send_file(target)
    else:
        return None

@app.callback(
                [
                    Output('uid_input', 'value'),
                    Output('page_url', 'children')
                ],
                Input('url', 'href'),
                State('url','pathname')
            )
def display_page(href,pathname):

    uid_arr = href.split('/results/')
    if len(uid_arr) > 1:
        return uid_arr[-1].split('#')[0], href
    else:
        return '',''

@app.callback(
    [Output("search_btn","href"),
     Output("msa_btn","href"),
     Output("tree_btn","href")],
    Input("uid_input","value")
)
def change_link(uid):
    return f'/results/{uid}',f'/msa/{uid}',f'/tree/{uid}'
#@app.callback(
#    Output("url","pathname"),
#    Input('search_btn','n_clicks'),
#    State('uid_input','value'), prevent_initial_call=True
#)
#def navigate(n_clicks,uid):
#    if n_clicks > 0:
#        return f'/results/{uid}'
#    else:
#        raise PreventUpdate


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
        if len(old_trigger) > 1:
            return old_trigger[:-1]
        else:
            return 'x'
    left = get_left_time(n_intervals)
    if left == 0 and (not LOADED):
        if len(old_trigger) > 1:
            return old_trigger[:-1]
        else:
            return 'x'
    else:
        raise PreventUpdate

def load_config(config_file):
    if os.path.exists(config_file):
        paras_dict = toml.load(config_file)
    else:
        paras_dict = {}
    return paras_dict


@app.callback(
    [
        Output("loading-output2", "children"),
        Output('uid_span','children') ,
        Output('not_found_span','style'),
        Output('running_span','style'),
        Output('error_span','style'),
        Output('result_panel','style'),
        Output('logo_img','src'),
        Output('create_time','children'),
        Output('input_format','children'),
        Output('sequence_type','children'),
        Output('group_strategy','children'),
        Output('group_resolution','children'),
        Output('clustering_method_value','children'),
        Output('min_len','children'),
        Output('max_len','children'),
        Output('display_left','children'),
        Output('display_right','children'),
        #statistics
        Output('count_img_res', 'src'),
        Output('entropy_img_res', 'src'),
        Output('entropy_boxplot_img_res', 'src'),
        Output('clustermap_img_res', 'src'),
        Output('score_img_res', 'src'),
        Output("interval-component","disabled"),

    ],
    [
        Input('trigger_panel','children'),
    ],
        State('url','pathname')
    )
def trigger(nonsense,pathname):

    if ('/results' in pathname) and (not pathname == '/results'):
        uid = pathname.split('/')[-1]
    else:
        uid = ''

    results_arr = ['',uid]
    status = get_status(uid)

    global LOADED

    if status == 'not found':
        LOADED = True
        results_arr += [{},{'display':'none'},{'display':'none'},{'display':'none'}]
    elif status == 'running':
        LOADED = False
        results_arr += [{'display':'none'},{},{'display':'none'},{'display':'none'}]
    elif status == 'error':
        LOADED = True
        results_arr += [{'display':'none'},{'display':'none'},{},{'display':'none'}]
    elif status == 'finished':
        results_arr += [{'display':'none'},{'display':'none'},{'display':'none'},{}]
        LOADED = True
    else:
        LOADED = True

    src = '' 
    if LOADED and status == 'finished':
        encoded_image = base64.b64encode(open(f'{PNG_PATH}/{uid}.png', 'rb').read())
        src = 'data:image/png;base64,{}'.format(encoded_image.decode())
    results_arr += [src]

    config_file = f"{CONFIG_PATH}/{uid}.toml"
    config_dict = load_config(config_file)

    for item in ['create_time','seq_file_type','sequence_type','group_strategy','group_resolution','clustering_method',
                 'min_length','max_length','display_range_left','display_range_right']:
        if item == 'create_time':
            tm = config_dict.get(item,'')
            if tm != '':
                tm = datetime.datetime.utcfromtimestamp(int(tm)).strftime('%Y-%m-%d %H:%M:%S (UTC)')
            results_arr += ['%s'%(tm)]
        else:
            results_arr += ['%s'%(config_dict.get(item,''))]
    

    ###

    count_src = ''
    entropy_src = ''
    boxplot_entropy_src = ''
    clustermap_src = ''
    score_src = ''
    if LOADED and status == 'finished':
        if  config_dict['analysis']: 
            count_name = f'{PNG_PATH}/{uid}.counts.png'
            count_src = get_img_src(count_name)

            entropy_name = f'{PNG_PATH}/{uid}.entropy.png'
            entropy_src = get_img_src(entropy_name)

            boxplot_entropy_name = f'{PNG_PATH}/{uid}.boxplot_entropy.png'
            boxplot_entropy_src = get_img_src(boxplot_entropy_name)

            clustermap_name = f'{PNG_PATH}/{uid}.clustermap.png'
            clustermap_src = get_img_src(clustermap_name)

            score_name = f'{PNG_PATH}/{uid}.scores.png'
            score_src = get_img_src(score_name)
    
    results_arr += [count_src, entropy_src, boxplot_entropy_src, clustermap_src,score_src]

    interval_disabled = False
    if LOADED:
        interval_disabled = True
    results_arr += [interval_disabled]

    ###
       
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