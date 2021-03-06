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
from flask import config
from pandas.io.formats import style
import toml
import math

from ..app import app
from ..config import PNG_PATH,CONFIG_PATH,SQLITE3_DB,FA_PATH,GROUP_LIMIT,MAX_SEQ_LEN
from ..utils import get_img_src
from ..sqlite3 import get_finished_time, get_status
from ..redis_queue import check_queue_status, enqueue

from dash.exceptions import PreventUpdate
import base64
import datetime,time
import re
import pandas as pd




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
        [
            html.Div([
                        html.Div('Task failed. '),
                        html.Div('',id='error_info_panel'),
                    ], id='error_span', style={'display':'none'})
        ], style={'fontSize':'25px','color':'#ff3400','margin':'20px'}
    )

    running_panel = html.Div(
        [
            html.Span(
                [
                    html.Div([html.Div([
                                         html.Span('The task is still running'),
                                         html.Span('',id='in_queue_note'),
                                         html.Span(' please check it later: '),
                                        ],style={'color':'black'}),
                              html.Div('',id='page_url')]), 
                    html.Div(
                        [ 
                            html.Span('The page will be refreshed every '),
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
            html.Div('Please save the link of this page for future use. MetaLogo will keep it for at least 7 days.',style={'fontWeight':'bold','color':'#576ef2','background':'#568af13b'}),
            dbc.CardHeader("Task info and parameters",style={'fontWeight':'bold'}),
            dbc.CardBody(
                [
                    dbc.Col([
                        dbc.Row([
                            dbc.Col([html.Span('ID',style=label_style), html.Span('xx',style=value_style, id='uid_span')]) ,
                        ],style={'marginTop':'10px'}),
                        dbc.Row([
                            dbc.Col([html.Span('Name',style=label_style), html.Span('xx',style=value_style, id='task_name_span')]) ,
                        ],style={'marginTop':'10px'}),
                        dbc.Row([
                            dbc.Col([html.Span('Created Time',style=label_style), html.Span('2021/2/3, 15:00',style=value_style, id='create_time')]),
                        ],style={'marginTop':'10px'}),
                        html.Hr(),
                        dbc.Row([
                            dbc.Col([html.Span('Input Format',style=label_style), html.Span('auto',style=value_style,id='input_format')]),
                            dbc.Col([html.Span('Sequence Type',style=label_style), html.Span('auto',style=value_style,id='sequence_type')]),
                            dbc.Col([html.Span('Group Strategy',style=label_style), html.Span('auto',style=value_style,id='group_strategy')]),
                            dbc.Col([html.Span('Grouping Resolution ',style=label_style), html.Span('auto',style=value_style,id='group_resolution')]),
                            dbc.Col([html.Span('Clustering Method ',style=label_style), html.Span('auto',style=value_style,id='clustering_method_value')]),
                        ],style={'marginTop':'10px'}),
                        dbc.Row([
                            dbc.Col([html.Span('Min Length ',style=label_style), html.Span('auto',style=value_style,id='min_len')]),
                            dbc.Col([html.Span('Max Length ',style=label_style), html.Span('auto',style=value_style,id='max_len')]),
                            dbc.Col([html.Span('Display Range',style=label_style), html.Span('auto',style=value_style,id='display_left_right')]),
                            dbc.Col([html.Span('Basic Analysis',style=label_style), html.Span('auto',style=value_style,id='basic_analysis')]),
                            dbc.Col([html.Span('Height',style=label_style), html.Span('auto',style=value_style,id='height_algorithm')]),
                        ],style={'marginTop':'10px'}),
                        dbc.Row([
                            dbc.Col([html.Span('Adjacent Alignment ',style=label_style), html.Span('auto',style=value_style,id='adjacent_alignment')]),
                            dbc.Col([html.Span('Global Alignment ',style=label_style), html.Span('auto',style=value_style,id='global_alignment')]),
                            dbc.Col([html.Span('Align Metric ',style=label_style), html.Span('auto',style=value_style,id='align_metric')]),
                            dbc.Col([html.Span('Connect Threshold ',style=label_style), html.Span('auto',style=value_style,id='connect_threshold_value')]),
                            dbc.Col([html.Span('Logo Type',style=label_style), html.Span('auto',style=value_style,id='logo_type')]),
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
            dbc.CardBody([
                    #html.Div([
                    #    html.Img(id='logo_img',src='',style={"height":"100%","verticalAlign":"top"}),
                    #], style={"height":"100%","overflowX":"scroll","whiteSpace":"nowrap","width":"100%"}),
                    html.Div([
                        html.Img(id='logo_img',src='',style={"width":"100%","verticalAlign":"top"}),
                    ], ),

                    html.Div('* The red dot on the tree indicates the group your target sequence (first sequence of your input) is in.',style={'fontSize':'10px','color':'#ff6f00'}),
                    html.Hr(),
                    dbc.Row(
                        [
                            dbc.Col(
                                dbc.FormGroup([
                                    dbc.Label("Left pos",html_for='input'),
                                    dbc.Input(type="number", min=0, max=MAX_SEQ_LEN, id="fast_left_pos",step=1,value=0),
                                ])
                            ),

                            dbc.Col(
                                dbc.FormGroup([
                                    dbc.Label("Right pos",html_for='input'),
                                    dbc.Input(type="number",  max=MAX_SEQ_LEN, id="fast_right_pos",step=1,value=10),
                                    ])
                            ),

                            dbc.Col(
                                dbc.FormGroup([
                                    dbc.Label("Group limit",html_for='input'),
                                    dbc.Input(type="number", min=1, max=GROUP_LIMIT, id="fast_group_limit",step=1,value=1),
                                    ])
                            ),

                            dbc.Col(
                                dbc.FormGroup([
                                    dbc.Label("Reset resolution",html_for='input'),
                                    dbc.Input(type="number", min=0, max=1, id="reset_resolution",step=0.000001,value=1),])
                            )
                        ]),
                         
                    html.Div(
                        [
                         dbc.Button("Fast Re-Run", n_clicks=0,id='reset_resolution_btn',color='info'),
                         html.Div('* Only for auto-grouping or global alignment scenario'),
                        ],style={'textAlign':'right','fontSize':'10px'})
             
            ])
        ],style={'marginBottom':'10px'},id='seqlogo_panel'
    )
    statistics_panel = dbc.Card(
        [
            dbc.CardHeader("Statistics Analysis",style={'fontWeight':'bold'}),
            dbc.CardBody(
                [
                    dbc.Row(
                        dbc.Col(
                            html.Span('Figure 0. Sequence lengths distribution.')
                    )),
                    dbc.Row([
                        html.Img(id='lengths_img_res',src='',style={"margin":"auto"}),
                        ]),
                    html.Hr(),
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
                        html.Img(id='entropy_img_res',src='',style={"margin":"auto","width":"100%"}),
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
                            html.Span('Figure 4. Correlations among groups (only in global alignment mode and #groups>1). (Only for global alignment or auto-grouping mode)')
                    )),
                    dbc.Row([
                        html.Img(id='clustermap_img_res',src='',style={"margin":"auto","width":"60%"}),
                        ]),
                    html.Hr(),
                    dbc.Row(
                        dbc.Col(
                            html.Span('Figure 5. Distribution of pairwise distances of nodes in the phylogenetic tree. (Only for auto-grouping mode)')
                    )),
                    dbc.Row([
                        html.Img(id='dists_img_res',src='',style={"margin":"auto","width":"60%"}),
                        ]),
                ]
            )
        ], id='statistics_panel', style={'marginBottom':'10px'}
    )

    other_panel = dbc.Card(
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
        ],style={'marginBottom':'10px'},id='other_panel'
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
                                    dbc.Button("Grouping details", color='info',id='grouping_download_btn',style=btn_style),
                                    dcc.Download(id="grouping_download",type='text',),
                                ]
                            ),

                            ],style={'margin':'20px'}),
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
    modal = dbc.Modal(
                [
                    dbc.ModalHeader("Error", id="result_modal_header"),
                    dbc.ModalBody("Message", id="result_modal_body"),
                    dbc.ModalFooter(
                       html.Span('* Click outside of the modal or press ESC to hide it', style={"fontSize":"10px","color":"orange"}) 
                    ),
                ],
                id="result_modal",
                centered=True,
                is_open=False,
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
                other_panel,
                download_panel,
                trigger_panel
            ],id='result_panel',style={"display":"none"}),
            loading_spinner,
            html.Div('',id='garbage3',style={'display':'none'}),
            html.Div('',id='garbage4',style={'display':'none'}),
            html.Div('',id='reset_waitter',style={'display':'none'}),
            dbc.Input(id='status',style={'display':'none'},type='string'),
            modal
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

    config_file = f"{CONFIG_PATH}/{uid}.toml"
    config_dict = load_config(config_file)

    target =  f"{PNG_PATH}/{uid}.{config_dict['logo_format']}"
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
    target =  f"{FA_PATH}/server.{uid}.msa.rawid.fa"
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
    target =  f"{FA_PATH}/server.{uid}.fasttree.rawid.tree"
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
    target =  f"{FA_PATH}/server.{uid}.grouping.fa"
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


LOADED = False


def load_config(config_file):
    if os.path.exists(config_file):
        paras_dict = toml.load(config_file)
    else:
        paras_dict = None
    return paras_dict

def save_config(config,config_file):

    with open(config_file, 'w') as f:
        toml.dump(config, f)


@app.callback(
    [
        Output("loading-output2", "children"),
        Output('uid_span','children') ,

        Output('not_found_span','style'),
        Output('running_span','style'),
        Output('error_span','style'),
        Output('result_panel','style'),
        Output('in_queue_note','children'),
        Output('error_info_panel','children'),

        Output('logo_img','src'),
        #info 1L
        Output('task_name_span','children') ,
        Output('create_time','children'),
        Output('input_format','children'),
        Output('sequence_type','children'),
        Output('group_strategy','children'),
        Output('group_resolution','children'),
        Output('clustering_method_value','children'),
        #info 2L
        Output('min_len','children'),
        Output('max_len','children'),
        Output('display_left_right','children'),
        Output('basic_analysis','children'),
        Output('height_algorithm','children'),
        #info 3L
        Output('adjacent_alignment','children'),
        Output('global_alignment','children'),
        Output('align_metric','children'),
        Output('connect_threshold_value','children'),
        Output('logo_type','children'),

        Output("fast_left_pos","value"),
        Output("fast_right_pos","value"),
        Output("fast_group_limit","value"),
        Output("reset_resolution","value"),

        #statistics
        Output('lengths_img_res', 'src'),
        Output('count_img_res', 'src'),
        Output('entropy_img_res', 'src'),
        Output('entropy_boxplot_img_res', 'src'),
        Output('clustermap_img_res', 'src'),
        Output('dists_img_res', 'src'),
        #nondisplay/active
        Output('other_panel','style'),
        Output('msa_download_btn','disabled'),
        Output('phylo_download_btn','disabled'),
        Output('grouping_download_btn','disabled'),
        Output('reset_resolution_btn','disabled'),
        Output('reset_resolution','disabled'),
        #other
        Output("seq_logo_download_btn","children"),
        #loaded count
        Output("status","value")

    ],
    [
        Input('trigger_panel','children'),
    ],
        State('url','pathname'),
    )
def trigger(nonsense,pathname):

    if ('result' not in pathname):
        raise PreventUpdate

    if ('/results' in pathname) and (not pathname == '/results'):
        uid = pathname.split('/')[-1]
    else:
        uid = ''

    

    results_arr = ['',uid]

    if uid != '':
        status = get_status(uid)
        rq_found,rq_failed,exc_info = check_queue_status(uid)
    else:
        status = 'not found'
        rq_found = False
        rq_failed = False
        exc_info = ''
    if exc_info is None:
        exc_info = ''

       

    global LOADED
    if not rq_failed:
        if status == 'not found':
            LOADED = True
            results_arr += [{},{'display':'none'},{'display':'none'},{'display':'none'},'']
        elif status == 'running':
            LOADED = False
            results_arr += [{'display':'none'},{},{'display':'none'},{'display':'none'},'']
        elif status == 'in-queue':
            LOADED = False
            results_arr += [{'display':'none'},{},{'display':'none'},{'display':'none'},'(in queue)']
        elif status in ['error','failed']:
            LOADED = True
            results_arr += [{'display':'none'},{'display':'none'},{},{'display':'none'},'']
        elif status == 'finished':
            finished_time = get_finished_time(uid)
            if finished_time - time.time() > 7 * 24 * 60 * 60:
                results_arr += [{},{'display':'none'},{'display':'none'},{'display':'none'},'']
                status = 'not found'
            else:
                results_arr += [{'display':'none'},{'display':'none'},{'display':'none'},{},'']
            LOADED = True
        else:
            LOADED = True
    else:
        LOADED = True
        results_arr += [{'display':'none'},{'display':'none'},{},{'display':'none'},'']
    
    err_info = ''
    if status in ['error','failed']:
        err_info = get_status(f"{uid}-errinfo")
        if err_info is None:
            err_info = ''
        if err_info == 'not found':
            err_info = ''
        err_info += ' ('+exc_info + ') '
    results_arr += [err_info]

    src = '' 
    if LOADED and status == 'finished':
        encoded_image = base64.b64encode(open(f'{PNG_PATH}/{uid}.png', 'rb').read())
        src = 'data:image/png;base64,{}'.format(encoded_image.decode())
    results_arr += [src]

    config_file = f"{CONFIG_PATH}/{uid}.toml"
    if os.path.exists(config_file):
        config_dict = load_config(config_file)
    else:
        config_dict = {}

    #if not config_dict:
    #    raise PreventUpdate

    for item in ['task_name','create_time','seq_file_type','sequence_type','group_strategy','group_resolution','clustering_method',
                 'min_length','max_length','display_left_right','analysis','height_algorithm','align','padding_align','align_metric','connect_threshold','logo_type']:
        if item == 'create_time':
            tm = config_dict.get(item,'')
            if tm != '':
                tm = datetime.datetime.utcfromtimestamp(int(tm)).strftime('%Y-%m-%d %H:%M:%S (UTC)')
            results_arr += ['%s'%(tm)]
        elif item == 'display_left_right':
            results_arr += ['%s:%s'%(config_dict.get('display_range_left'),config_dict.get('display_range_right'))]
        else:
            results_arr += ['%s'%(config_dict.get(item,''))]
    
    #fast rerun
    results_arr += [config_dict.get('display_range_left',''),config_dict.get('display_range_right',''), config_dict.get('group_limit',''),config_dict.get('group_resolution','')]
    ###

    lengths_src = ''
    count_src = ''
    entropy_src = ''
    boxplot_entropy_src = ''
    clustermap_src = ''
    dists_src = ''

    if LOADED and status == 'finished':
        if  config_dict['analysis']: 

            lengths_name = f'{PNG_PATH}/{uid}.lengths.png'
            lengths_src = get_img_src(lengths_name)

            count_name = f'{PNG_PATH}/{uid}.counts.png'
            count_src = get_img_src(count_name)

            entropy_name = f'{PNG_PATH}/{uid}.entropy.png'
            entropy_src = get_img_src(entropy_name)

            boxplot_entropy_name = f'{PNG_PATH}/{uid}.boxplot_entropy.png'
            boxplot_entropy_src = get_img_src(boxplot_entropy_name)

            clustermap_name = f'{PNG_PATH}/{uid}.clustermap.png'
            clustermap_src = get_img_src(clustermap_name)

            dists_name = f'{PNG_PATH}/{uid}.treedistances.png'
            dists_src = get_img_src(dists_name)

    results_arr += [lengths_src, count_src, entropy_src, boxplot_entropy_src, clustermap_src,dists_src]

    show_other_panel = False
    disabled_msa_download = True
    disabled_phylo_download =  True
    disabled_grouping_download = True
    disabled_reset_resolution_btn = True
    disabled_reset_resolution_input = True

    if config_dict.get('group_strategy','') == 'auto':
        show_other_panel = True
        disabled_msa_download = False
        disabled_phylo_download = False
        disabled_grouping_download = False
        disabled_reset_resolution_btn = False
        disabled_reset_resolution_input = False

    if config_dict.get('padding_align',False) and config_dict.get('align',False):
        show_other_panel = True
    
    if not show_other_panel:
        results_arr += [{'display':'none'}]
    else:
        results_arr += [{}]
    results_arr += [disabled_msa_download,disabled_phylo_download,
                    disabled_grouping_download,
                    disabled_reset_resolution_btn,disabled_reset_resolution_input]
    

    ###
    logo_type = config_dict.get('logo_format','')
    results_arr += [f'Sequence Logo ({logo_type})']

    results_arr += [status]
    return results_arr

@app.callback(
    [
        Output('result_modal_body', 'children'),
        Output('result_modal', 'is_open'),
        Output('reset_waitter', 'children'),
    ],
    [
        Input("reset_resolution_btn","n_clicks")
    ],
    [
        State("fast_left_pos","value"),
        State("fast_right_pos","value"),
        State("fast_group_limit","value"),
        State("reset_resolution","value"),
        State("url","pathname"),
        State("uid_span","children")
    ],
    prevent_initial_call=True,
)
def trigger_reset_resolution(n_clicks,left_pos,right_pos,group_limit,resolution,pathname,uid):

    if n_clicks == 0:
        raise PreventUpdate

    config_file = f"{CONFIG_PATH}/{uid}.toml"
    config_dict = load_config(config_file)

    if resolution == config_dict['group_resolution'] and left_pos == config_dict['display_range_left'] and right_pos == config_dict['display_range_right'] and group_limit == config_dict['group_limit']:
        return 'Same configuration, no need to re-run',True,''
    if resolution is None:
        return 'Please input the resolution',True,''
    if left_pos is None:
        return 'Please input the left position',True,''
    if right_pos is None:
        return 'Please input the right position',True,''
    if group_limit is None:
        return 'Please input the group limit',True,''

    if resolution > 1 or resolution <0 :
        return 'Resolution value must be between 0 and 1',True,''
    
    if group_limit > GROUP_LIMIT:
        return f'Group limit must be <= {GROUP_LIMIT}',True,''
    if group_limit == 0:
        return f'Group limit must > 0 ',True,''
    
    if right_pos > MAX_SEQ_LEN:
        return f'Right pos > Max sequence length {MAX_SEQ_LEN}',True,''
    if right_pos < -1*MAX_SEQ_LEN:
        return f'Right pos < -1 * Max sequence length {MAX_SEQ_LEN}',True,''
    
    config_dict['group_resolution'] = float(resolution)
    config_dict['display_range_left'] = left_pos
    config_dict['display_range_right'] = right_pos
    config_dict['group_limit'] = group_limit
    save_config(config_dict,config_file)

    enqueue(config_file)

    return '',False,'Go'

app.clientside_callback(
    """
    function(command) {
        if (command=='Go'){
            document.location.reload()
        }
        return ''
    }
    """,
    Output('garbage3', 'children'),
    Input('reset_waitter', 'children'),
)


app.clientside_callback(
    """
    function(status) {
        if((status == 'running')||(status=='in-queue')){
            setTimeout(function(){
                window.location.reload(1);
             }, 10000);
        }
    }
    """,
    Output('garbage4', 'children'),
    Input('status', 'value'),
)  

layout = get_layout()