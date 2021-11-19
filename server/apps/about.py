# -*- coding: utf-8 -*-
#!/usr/bin/env python

import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State


about_md = dcc.Markdown('''
**MetaLogo** is a tool for making sequence logos. It can take multiple sequences as input, automatically identify the heterogeneity among sequences and cluster them into different groups given any wanted resolution, finally output multiple aligned sequence logos in one figure. Grouping can also be specified by users, such as grouping by lengths, grouping by sample Id, etc.  Compared to conventional sequence logo generator, MetaLogo can display the total sequence population in a more detailed, dynamic and informative view.

In the auto-grouping mode, MetaLogo will perform multiple sequence alignment (MSA), phylogenetic tree construction and group clustering for the input sequences. Users can give MetaLogo different resolution values to guide the sequence clustering process and the sequence logos building, which lead to a dynamic understanding of the input data. In the user-defined-grouping mode, MetaLogo will perform an adjusted MSA algorithms to align multiple logos and highlight the conserved connections among groups. MetaLogo also provides a basic analysis module to present statistics of the sequences, involving sequencing distribution, conservation scores, pairwise distances, group correlations, etc.  Almost all the related intermediate results are available for downloading.

Users have plenty of options to get their custom sequence logos and basic analysis figures. Multiple styles of the output are provided. Users can customize most of the elements of drawing, including title, axis, ticks, labels, font color, graphic size, etc. At the same time, it can export a variety of formats including PDF, PNG, SVG and so on. It is really convenient for users without programming experiences to produce publication-level figures.

Users could also download the standalone package of MetaLogo, integrate it into their own python project or easily set up a local MetaLogo server by using docker. A concise and complete front website + a queue organized back end could give users convenience to investigate and understand their sequences in their own computing environments. 

If you think this tool is easy to use, please share it with those who need it. If you have any comments, you can send an email to the maintainer via the feedback button at the top. When our article gets published, please remember to cite our work.

''')  

aboutpanel = dbc.Card(
    [
        dbc.CardHeader("About MetaLogo"),
        dbc.CardBody(
            [
                dbc.Row([
                    dbc.Col(html.Div(html.Img(src='/assets/about.png',width='100%')))
                ])
                ,
                dbc.Row([
                    dbc.Col(about_md),
                ]),
                dbc.Row(
                    dbc.Col([
                    html.Div([
                        dbc.NavLink(
                            [dbc.Button("> Analysis", color='info')],
                            href='/analysis'
                        )
                        ], 
                    style={'marginTop':'20px','textAlign':'right'})
                ]))
            ]
        )
    ],style={'marginBottom':'10px'}
)


layout = dbc.Container(children=[
        html.Hr(),
        aboutpanel

])