import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

import plotly.graph_objs as go

from tkinter import Tk
from tkinter import filedialog

from os import listdir
from os.path import isfile, join
import pandas as pd

import numpy as np

Tk().withdraw()
path = filedialog.askdirectory()
listdir(path)

onlyfiles = [f for f in listdir(path) if isfile(join(path, f)) and f[-2:] == 'py']

N = 100
random_x = np.linspace(0, 1, N)
random_y0 = np.random.randn(N) + 5

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div([
    html.Label('Dropdown'),
    dcc.Dropdown(
        id='drop_down_files',
        options=[{'label': f, 'value': f} for f in onlyfiles],
        value=onlyfiles[0]
    ),
    dcc.Graph(
        id='graph_up',
        figure={
            'data': [go.Scatter(x=random_x, y=random_y0,
                    mode='lines',
                    name='lines',
                    line={'color': 'blue'})]}),

    dcc.Graph(
        id='graph_down',
        figure={
            'data': [go.Scatter(x=random_x, y=random_y0,
                                mode='lines',
                                name='lines',
                                line={'color': 'red'})]})
]
)

@app.callback(
    [Output(component_id='graph_up', component_property='figure'),
     Output(component_id='graph_down', component_property='figure')],
    [Input(component_id='drop_down_files', component_property='value')]
)
def update_graph(input_value):

    random_x = np.linspace(0, 1, N)
    if input_value == onlyfiles[0]:
        random_y0 = np.random.randn(N) + 5
    else:
        random_y0 = np.random.randn(N) - 5
    traces_up = [go.Scatter(x=random_x, y=random_y0,
                            mode='lines',
                            name='lines',
                            line={'color': 'black'})]
    traces_down = [go.Scatter(x=random_x, y=random_y0,
                            mode='lines',
                            name='lines',
                            line={'color': 'red'})]
    return {'data': traces_up}, {'data': traces_down}


if __name__ == '__main__':
    app.run_server(debug=False)
