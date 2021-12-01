import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc

from .app import app
from .apps import results, analysis,about,msa,tree
from .. import MetaLogo

server = app.server

nav = dbc.Nav(
    [
        dbc.NavItem(dbc.NavLink("About", href="/about",id='jump_about')),
        dbc.NavItem(dbc.NavLink("Analysis",  href="/analysis", id='jump_analysis')),
        dbc.NavItem(dbc.NavLink("Results",  href="/results", id='jump_results')),
        dbc.NavItem(dbc.NavLink("Tutorial",  href="https://github.com/labomics/MetaLogo/wiki/Web-server/",target='_blank')),
        dbc.NavItem(dbc.NavLink("Python package", href="https://github.com/labomics/MetaLogo",target='_blank')),
        dbc.NavItem(dbc.NavLink("Paper",  target="_blank",href='https://www.biorxiv.org/content/10.1101/2021.08.12.456038v3')),
        dbc.NavItem(dbc.NavLink("Feedback", href="mailto:achenge07@163.com", target='_blank')),
    ]
)
toppanel = html.Div(
    [
        dbc.Row([
            dbc.Col(dbc.Row([
                html.H1(['MetaLogo']),
                html.Span(MetaLogo.__version__,style={'color':'grey'}),
                ])),
            ],
            style={'marginTop':'10px'}
        ),
        dbc.Row(nav)
    ]
)

footer_panel = html.Div([
    dbc.Row([
        dbc.Col(['© Developed by Yaowen Chen @ Beijing Institute of Basic Medical Sciences by using ', 
                html.A('Matplotlib',href='https://matplotlib.org/'),', ', html.A('Plotly Dash',href='https://dash.plotly.com/'), ' and ', 
                html.A('other great tools',href='https://github.com/labomics/MetaLogo/blob/main/requirements.txt')
                ],
                )
    ]),
    dbc.Row(dbc.Col('July, 2021'))
],style={"textAlign":"center","marginTop":"40px","fontSize":"10px","color":"grey"})


layout = dbc.Container(children=[
    toppanel
])

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    layout,
    html.Div(id='page-content'),
    footer_panel
])

# "complete" layout
app.validation_layout = html.Div([
    dcc.Location(id='url', refresh=False),
    layout,
    html.Div(id='page-content'),
    about.layout,
    results.layout,
    analysis.layout,
    msa.layout,
    tree.layout
])

@app.callback(
            [Output('jump_analysis','style'),
            Output('jump_about','style'),
            Output('jump_results','style')],
            Input('url','pathname'))
def highlight_btn(pathname):
    hightlighted_style = {'color':'#e517e5','fontWeight':'bold'}
    if 'analysis' in pathname:
        return hightlighted_style,None,None
    elif 'about' in pathname:
        return None,hightlighted_style,None
    elif 'results' in pathname:
        return None,None,hightlighted_style
    else:
        return None,None,None

@app.callback(Output('page-content', 'children'),
              Input('url', 'pathname'))
def display_page(pathname):
    if pathname == '/results':
        return results.layout
    elif pathname == '/analysis':
        return analysis.layout
    elif pathname == '/about':
        return about.layout
    elif pathname == '/':
        return about.layout
    elif '/results/' in pathname:
        return results.layout
    elif '/msa/' in pathname:
        return msa.layout
    elif '/tree/' in pathname:
        return tree.layout
    else:
        return '404'

if __name__ == '__main__':

    app.run_server(debug=True)
    