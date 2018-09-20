from afbench import Benchmark, BenchmarkInfo

import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go

fft_info = BenchmarkInfo('fft.json')
print('Available benchmarks: {}'.format(fft_info.benchmark_names))
for bench in fft_info.benchmark_names:
    print('{} parameters:'.format(bench))
    for param in fft_info.params(bench):
        print('{}: {}'.format(param, fft_info.paramvals(bench, 'f32', param)))

fft1 = Benchmark(
    filepath='fft.json',
    name='fft1',
    filters={
        'dim1': 1,
        'dim2': 1,
        'fft_dim': 1
    }
)
fft1_x_vals = fft1.collect_param_vals('dim0', 'f32')
fft1_y_vals = fft1.collect_real_times('f32')

fft2 = Benchmark(
    filepath='fft.json',
    name='fft2',
    filters={
        'dim1': 16,
        'dim2': 1,
        'fft_dim': 2
    }
)
fft2_x_vals = fft2.collect_param_vals('dim0', 'f32')
for i in range(len(fft2_x_vals)):
    fft2_x_vals[i] *= 16
fft2_y_vals = fft2.collect_real_times('f32')

graph = dcc.Graph(
    id='graph',
    figure={
        'data': [{
            'name': 'fft1',
            'x': fft1_x_vals,
            'y': fft1_y_vals
        }, {
            'name': 'fft2',
            'x': fft2_x_vals,
            'y': fft2_y_vals
        }],
        'layout': go.Layout(
            xaxis={
                'type' : 'log'
            },
            yaxis={
                'type' : 'log'
            }
        )
    }
)

app = dash.Dash('FFT Benchmarks')
app.layout = html.Div(
    children=[graph],
    id='body'
)

if __name__ == '__main__':
    app.run_server()
