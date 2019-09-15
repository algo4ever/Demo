import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

import plotly.graph_objs as go

from tkinter import Tk
from tkinter import filedialog

import os
import numpy as np
import soundfile as sf


N_audio = 100000  # around 2 sec

def normalize_signal(audio):
    PERCENTILE = 98
    percentile_amp = np.percentile(audio, PERCENTILE)
    audio = audio/percentile_amp
    audio = list(map(lambda x: x if x < 1 else 1, audio))
    audio = list(map(lambda x: x if x > -1 else -1, audio))
    audio = audio - np.mean(audio)
    return audio
def get_data_from_audio_file(path_to_file):
    data, fs = sf.read(path_to_file, dtype='float32')
    channell = []
    channelr = []
    for l, r in enumerate(data):
        channell.append(l)
        channelr.append(r[0])
    return channelr, fs
def calculate_rectangle(audio, threshold=125):
    SKIP_BEGINNING = 100  # for wierd open the mic sounds
    AMP_FOR_TRUE_RECTANGLE = 0.2
    AMP_FOR_FALSE_RECTANGLE = 0
    WINDOW_SIZE = 2500
    y_rect = [AMP_FOR_FALSE_RECTANGLE]*SKIP_BEGINNING
    audio = normalize_signal(audio)

    for window in range(SKIP_BEGINNING,len(audio),WINDOW_SIZE):
        enr = calculate_energy(audio[window:window+WINDOW_SIZE])
        if enr > threshold:
            for i in range(WINDOW_SIZE):
                y_rect.append(AMP_FOR_TRUE_RECTANGLE)
        else:
            for i in range(WINDOW_SIZE):
                y_rect.append(AMP_FOR_FALSE_RECTANGLE)
    return y_rect
def fancy_measure(audio):
    return [np.abs(y_val) for y_val in audio]
def calculate_energy(audio):
    return sum(np.power(audio,2))


Tk().withdraw()
default_path = os.path.join(os.path.dirname(os.getcwd()),"records")
path = filedialog.askdirectory(initialdir=default_path)
only_files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f)) and f[-3:] == 'WAV']





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
    dcc.Graph(id='graph_down'),
    dcc.Slider(
        id='thr-slider',
        min=10,
        max=500,
        step=1,
        value=175,
    ),
    html.Div(id='slider-str')
]
)

@app.callback(
    [Output(component_id='graph_up', component_property='figure'),
     Output(component_id='graph_down', component_property='figure'),
     Output(component_id='slider-str', component_property='children')],
    [Input(component_id='drop_down_files', component_property='value'),
     Input(component_id='thr-slider', component_property='value')]
)
def update_graph(drop_down_name, thr):
    y, fs = get_data_from_audio_file(os.path.join(path, drop_down_name))
    y_rect = calculate_rectangle(y[:N_audio], thr)
    x = np.linspace(0, N_audio/fs, num=N_audio)
    fig_up = {
        "data": [go.Scatter(x=x, y=y[:N_audio],
                            mode='lines',
                            name='lines',
                            line={'color': 'black'})],
        "layout": {"title": {"text": "Up figure"}}
    }
    fig_down = {
        "data": [go.Scatter(x=x, y=fancy_measure(y[:N_audio]),
                            mode='lines',
                            name='lines',
                            line={'color': 'red'}),
                 go.Scatter(x=x, y=y_rect,
                            mode='lines',
                            name='lines',
                            line={'color': 'green'})],
        "layout": {"title": {"text": "down figure"}}
    }
    return fig_up, fig_down, 'threshold is "{}"'.format(thr)


if __name__ == '__main__':
    app.run_server(debug=False)
