import dash
from flask import Flask
import dash_bootstrap_components as dbc
from .config import GOOGLE_ANALYTICS_ID
server = Flask(__name__)

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
external_scripts = [f'https://www.googletagmanager.com/gtag/js?id={GOOGLE_ANALYTICS_ID}'] 

#app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app = dash.Dash(
    __name__,
    title="MetaLogo",
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    external_scripts=external_scripts,
    server=server,
    update_title=None,
    meta_tags=[{
        'name': 'description',
        'content': 'A website to plot and align multiple sequences logos on one single figure,it can integrate the logo images of sequece of different lengths, and align them through algorithms, so as to display the samples in a more macroscopic view.'
    }]

)
app.title = "MetaLogo: a heterogeneity-aware sequence logo generator and aligner"
