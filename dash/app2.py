from plotly.tools import mpl_to_plotly
from matplotlib import pyplot as plt
import dash
import dash_html_components as html
import dash_core_components as dcc

app= dash.Dash()

fig= plt.figure()
ax= fig.add_subplot(111)
ax.plot(range(10), [i**2 for i in range(10)])
ax.grid(True)
plotly_fig = mpl_to_plotly(fig)

app.layout= html.Div([
        dcc.Graph(id= 'matplotlib-graph', figure=plotly_fig)

        ])

app.run_server(debug=True, port=8010, host='localhost')

