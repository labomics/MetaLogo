import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from .app import app
from .apps import app1, app2


app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])

# "complete" layout
app.validation_layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content'),
    app1.layout,
    app2.layout,
])



@app.callback(Output('page-content', 'children'),
              Input('url', 'pathname'))
def display_page(pathname):
    if pathname == '/results':
        return app1.layout
    elif pathname == '/':
        return app2.layout
    else:
        return '404'

if __name__ == '__main__':


    app.run_server(debug=True)

