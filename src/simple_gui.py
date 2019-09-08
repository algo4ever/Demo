import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

import plotly.graph_objs as go
import matplotlib.pyplot as plt


from tkinter import Tk
from tkinter import filedialog

import os
import numpy as np
import wave

'''
TODO:
1. find where to put the green rectangle.
2. understand why with maria'S records the graph is unreadable
'''

def get_data_from_audio_file(path_to_file):
    spf = wave.open(path_to_file, 'r')
    signal = spf.readframes(-1)
    signal = np.fromstring(signal, 'Int16')
    channels = [[] for channel in range(spf.getnchannels())]
    for index, datum in enumerate(signal):
        channels[index % len(channels)].append(datum)
    fs = spf.getframerate()
    return channels[0], fs


Tk().withdraw()
default_path = os.path.join(os.path.dirname(os.getcwd()),"records")
path = filedialog.askdirectory(initialdir=default_path)
only_files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f)) and f[-3:] == 'WAV']
audio_values, fs = get_data_from_audio_file(os.path.join(path, only_files[1]))

Time=np.linspace(0, len(audio_values)/fs, num=len(audio_values))

if False:
    plt.figure(1)
    plt.title('Signal Wave...')
    plt.plot(Time, audio_values)
    plt.show()


N_audio = 100000  # around 2 sec
x = np.linspace(0, N_audio / fs, num=N_audio)
Z1 = np.random.uniform(0.0, 2.0)
Z2 = np.random.uniform(0.0, 2.0)
if Z1 > Z2:
    t = Z1
    Z1 = Z2
    Z2 = t

y_rect = []
for i in range(N_audio):
    if i < Z1 * fs:
        z = 0
    elif i < Z2 * fs:
        z = 10000
    else:
        z = 0
    y_rect.append(z)


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div([
    html.Label('Dropdown'),
    dcc.Dropdown(
        id='drop_down_files',
        options=[{'label': f, 'value': f} for f in only_files],
        value=only_files[0]
    ),
    dcc.Graph(id='graph_up'),
    dcc.Graph(id='graph_down')
]
)

@app.callback(
    [Output(component_id='graph_up', component_property='figure'),
     Output(component_id='graph_down', component_property='figure')],
    [Input(component_id='drop_down_files', component_property='value')]
)
def update_graph(input_value):
    y, fs = get_data_from_audio_file(os.path.join(path, input_value))
    x = np.linspace(0, N_audio/fs, num=N_audio)
    fig_up = {
        "data": [go.Scatter(x=x, y=y[:N_audio],
                            mode='lines',
                            name='lines',
                            line={'color': 'black'})],
        "layout": {"title": {"text": "Up figure"}}
    }
    fig_down = {
        "data": [go.Scatter(x=x, y=[np.abs(y_val) for y_val in y[:N_audio]],
                            mode='lines',
                            name='lines',
                            line={'color': 'red'}),
                 go.Scatter(x=x, y=y_rect,
                            mode='lines',
                            name='lines',
                            line={'color': 'green'})],
        "layout": {"title": {"text": "down figure"}}
    }
    return fig_up, fig_down


if __name__ == '__main__':
    app.run_server(debug=False)
