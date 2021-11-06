import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc

from .app import app
from .apps import app1, app2,about
import MetaLogo


nav = dbc.Nav(
    [
        dbc.NavItem(dbc.NavLink("Analysis",  href="/analysis", id='jump_analysis')),
        dbc.NavItem(dbc.NavLink("Tutorial",  href="https://github.com/labomics/MetaLogo/wiki/Web-server/",target='_blank')),
        dbc.NavItem(dbc.NavLink("Python package", href="https://github.com/labomics/MetaLogo",target='_blank')),
        dbc.NavItem(dbc.NavLink("Paper",  target="_blank",href='https://www.biorxiv.org/content/10.1101/2021.08.12.456038v1')),
        dbc.NavItem(dbc.NavLink("Lab",  href="http://omicsnet.org",target='_blank')),
        dbc.NavItem(dbc.NavLink("Feedback", href="mailto:achenge07@163.com", target='_blank')),
        dbc.NavItem(dbc.NavLink("About", href="/about",id='jump_about')),
    ]
)
toppanel = html.Div(
    [
        dbc.Row([
            dbc.Col(dbc.Row([html.H1(['MetaLogo']),html.Span(MetaLogo.__version__,style={'color':'grey'})])),
            ],
            style={'marginTop':'10px'}
        ),
        dbc.Row(nav)
    ]
)

layout = dbc.Container(children=[
    toppanel
])

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    layout,
    html.Div(id='page-content')
])

# "complete" layout
app.validation_layout = html.Div([
    dcc.Location(id='url', refresh=False),
    layout,
    html.Div(id='page-content'),
    about.layout,
    app1.layout,
    app2.layout,
])

@app.callback(
            [Output('jump_analysis','style'),
            Output('jump_about','style')],
            Input('url','pathname'))
def highlight_btn(pathname):
    hightlighted_style = {'color':'#e517e5','fontWeight':'bold'}
    if 'analysis' in pathname:
        return hightlighted_style,None
    else:
        return None,hightlighted_style

@app.callback(Output('page-content', 'children'),
              Input('url', 'pathname'))
def display_page(pathname):
    if pathname == '/results':
        return app1.layout
    if pathname == '/analysis':
        return app2.layout
    elif pathname == '/about':
        return about.layout
    elif pathname == '/':
        return about.layout
    else:
        return '404'

if __name__ == '__main__':


    app.run_server(debug=True)

