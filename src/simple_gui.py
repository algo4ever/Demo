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
1. fix the fancy_measure function. which measure to use for audio files? what the technion guys used?
2. understand why with maria'S records the graph is unreadable
'''
N_audio = 100000  # around 2 sec

def get_data_from_audio_file(path_to_file):
    spf = wave.open(path_to_file, 'r')
    signal = spf.readframes(-1)
    signal = np.fromstring(signal, 'Int16')
    channels = [[] for channel in range(spf.getnchannels())]
    for index, datum in enumerate(signal):
        channels[index % len(channels)].append(datum)
    fs = spf.getframerate()
    return channels[0], fs
def calculate_rectangle(fancy_measure_audio):
    MAX_CUTTER = 0.95   # avoiding picks
    MIN_CUTTER = 0.0   # avoiding noise
    FLAG_COUNTER = 10000  # for cold done
    SKIP_BEGINNING = 100  # for wierd open the mic sounds
    AMP_FOR_TRUE_RECTANGLE = 10000
    AMP_FOR_FALSE_RECTANGLE = 0

    max_amplitude = max(fancy_measure_audio[SKIP_BEGINNING:]) * MAX_CUTTER
    threshold = max_amplitude * MIN_CUTTER
    print(threshold, np.mean(fancy_measure_audio), max_amplitude, np.std(fancy_measure_audio))
    y_rect = [AMP_FOR_FALSE_RECTANGLE]*SKIP_BEGINNING
    flag = 0
    for amp in fancy_measure_audio:
        if 0 < flag:  # in cold-down
            if flag == FLAG_COUNTER -1:
                y_rect.append(AMP_FOR_FALSE_RECTANGLE)
                flag = 0
            else:
                y_rect.append(AMP_FOR_FALSE_RECTANGLE)
                flag += 1
            continue
        # here flag is 0
        if amp < threshold and y_rect[-1]==1:  # exiting from a rectangle
            y_rect.append(AMP_FOR_FALSE_RECTANGLE)
            flag += 1
        elif amp >= threshold:
            y_rect.append(AMP_FOR_TRUE_RECTANGLE)
        y_rect.append(AMP_FOR_FALSE_RECTANGLE)
    return y_rect
def fancy_measure(audio):
    return [np.abs(y_val) for y_val in audio]



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
    y_rect = calculate_rectangle(fancy_measure(y[:N_audio]))
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
    return fig_up, fig_down


if __name__ == '__main__':
    app.run_server(debug=False)
