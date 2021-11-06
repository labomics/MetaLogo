# -*- coding: utf-8 -*-
#!/usr/bin/env python

import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State


about_md = dcc.Markdown('''
**MetaLogo** is a tool for making sequence logos. It is different from the conventional sequence logo tool in that it can take multiple sets of sequences as input, with different lengths or other characteristics, integrate the logos into one single figure and align them through certain algorithms, so as to display the total sequence population in a more detailed and dynamic view.

Users can choose to group sequences by length, or divide sequences of the same length into multiple groups. For each group, MetaLogo will draw a sequence logo separately. At the logo level, alignment is performed through a modified version of sequence alignment and multiple sequence alignment algorithms.

There are a total of 4 different logo layouts for users to choose from, such as horizontal, circular, radial and 3D logos, which are suitable for different scenes. At the same time, there are many different algorithms to choose from for the logo comparison and alignment.

Users can customize most of the elements of drawing, including title, axis, ticks, labels, font color, graphic size, etc. At the same time, it can export a variety of formats including PDF, PNG, SVG and so on. Users do not need any programming experience at all to make publication-level pictures.

Due to server resource limitations, this tool has a limit on the number of input sequences. But we also provide a python package that can be run independently, which can facilitate users to integrate the drawing code in their own projects or deploy them on high-performance computing nodes. In addition, we also provide a convenient server dockerfile for users to perform convenient graphical visualization operations locally.

If you think this tool is easy to use, please share it with those who need it. If you have any comments, you can send an email to the maintainer via the feedback button at the top. When our article gets published, please remember to cite our work.


''')  

aboutpanel = dbc.Card(
    [
        dbc.CardHeader("About MetaLogo"),
        dbc.CardBody(
            [
                dbc.Row([
                    dbc.Col(html.Div(html.Img(src='/assets/introduction.PNG',width='100%')))
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