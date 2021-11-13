# -*- coding: utf-8 -*-
#!/usr/bin/env python

import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import dash_bio as dashbio
from dash.dependencies import Input, Output, State
from ..app import app
from .analysis import CONFIG_PATH, SQLITE3_DB, PNG_PATH,FA_PATH
import os

#uid = '85eb7426-71d3-4d55-8688-dd15cfe9b482'
#msa_file = f'{FA_PATH}/server.{uid}.msa.fa'
#rf = open(msa_file,'r')
#fa_string = ''.join(rf.readlines())
#rf.close()



layout = html.Div([
    dashbio.AlignmentChart(
        id='my-default-alignment-viewer',
        data='>1\nAATT',
        height=1800,
        tileheight=50,
    ),
    html.Div(id='default-alignment-viewer-output')
])

@app.callback(Output('my-default-alignment-viewer', 'data'),
              Input('url', 'pathname'),prevent_initial_call=True)
def display_page(pathname):
    arrs = pathname.split('/msa/')
    if len(arrs) > 1:
        import urllib.request as urlreq

        #uid = arrs[-1]
        #msa_file = f'{FA_PATH}/server.{uid}.msa.fa'
        #if not os.path.exists(msa_file):
        #    return ''
        #rf = open(msa_file,'r')
        #fa_string = ''.join(rf.readlines())
        #rf.close()
        #print('yyyyy')
        data = urlreq.urlopen(
        fa_string = 'https://raw.githubusercontent.com/plotly/dash-bio-docs-files/master/alignment_viewer_p53.fasta'
).read().decode('utf-8')

        return fa_string
    else:
        print('xxxxxx')
        return ''

@app.callback(
    Output('default-alignment-viewer-output', 'children'),
    Input('my-default-alignment-viewer', 'eventDatum')
)
def update_output(value):
    if value is None:
        return 'No data.'
    return str(value)


