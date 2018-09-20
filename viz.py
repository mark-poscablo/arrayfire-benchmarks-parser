from afbench import Benchmark, BenchmarkInfo

from dash.dependencies import Input, Output, State, Event
from dash.exceptions import CantHaveMultipleOutputs
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import sys

app = dash.Dash('ArrayFire Benchmarks POC')
app.config['suppress_callback_exceptions'] = True

if len(sys.argv) > 2:
    print('Usage: ./viz.py <benchmark_filepath>')
    exit(-1)

# Parse benchmark JSON file
__benchmark_filepath = sys.argv[1]
__bench_info = BenchmarkInfo(__benchmark_filepath)

##################
# Initialization
##################

__init_bench = __bench_info.benchmark_names[0]
__init_dtype = __bench_info.dtypes(__init_bench)[0]
__init_indep_var = __bench_info.params(__init_bench)[0]
__bench_select_opts = [{'label': benchname, 'value': benchname}
                    for benchname in __bench_info.benchmark_names]
__dtype_select_opts = [{'label': dtype, 'value': dtype}
                     for dtype in __bench_info.dtypes(__init_bench)]
__sliders = []
__paramselect_opts = []
for param in __bench_info.params(__init_bench):
    is_disabled = False
    if param == __init_indep_var:
        is_disabled = True

    paramvals = __bench_info.paramvals(__init_bench, __init_dtype, param)
    __sliders.append(
        html.Div(
            children=[
                html.Label(param),
                dcc.Slider(
                    id='slider_' + param,
                    disabled=is_disabled,
                    min=0,
                    max=len(paramvals) - 1,
                    marks={i: paramvals[i] for i in range(len(paramvals))},
                    value=0
                )
            ],
            id = 'div_slider_' + param,
            style={
                'width': '90%',
                'border-bottom': '20px solid white'
            }
        )
    )

    __paramselect_opts.append({'value': param})

######################
# Webpage components
######################

header = html.Header(
    children=[
        html.H1('ArrayFire Benchmarks')
    ],
    style={
        'text-align': 'center'
    }
)

div_graph_benchmark = html.Div(
    children=[
        dcc.Graph(
            id='graph_benchmark'
        )
    ],
    id = 'div_graph_benchmark',
    style={
        'float': 'left',
        'width': '60%'
    }
)

div_sliders = html.Div(
    children=__sliders,
    id='div_sliders',
    style={
        'float': 'right',
        'width': '90%'
    }
)

div_radio_paramselect = html.Div(
    children=[
        dcc.RadioItems(
            id='radio_paramselect',
            options=[],
            value=None,
            inputStyle={
                'margin-bottom': '41px'
            }
        )
    ],
    id='div_radio_paramselect',
    style={
        'float': 'left',
        'width': '10%',
        'margin-top': '21px'
    }
)

div_param_adj = html.Div(
    children=[
        div_sliders,
        div_radio_paramselect
    ],
    id='div_param_adj',
    style={
        'column-count': '2'
    }
)

div_dropdown_benchmarks = html.Div(
    children=[
        dcc.Dropdown(
            id='dropdown_benchmarks',
            options=__bench_select_opts,
            value=__bench_select_opts[0]['value'],
            clearable=False,
            searchable=False
        )
    ],
    id='div_dropdown_benchmarks',
    style={
        'width': '70%',
        'float': 'left',
        'margin-bottom': '10px'
    }
)

div_dropdown_dtypes = html.Div(
    children=[
        dcc.Dropdown(
            id='dropdown_dtypes',
            options=__dtype_select_opts,
            value=__dtype_select_opts[0]['value'],
            clearable=False,
            searchable=False
        )
    ],
    id='div_dropdown_dtypes',
    style={
        'width': '30%',
        'float': 'right',
        'margin-bottom': '10px'
    }
)

div_dropdowns = html.Div(
    children=[
        div_dropdown_benchmarks,
        div_dropdown_dtypes
    ],
    id = 'div_dropdowns',
    style={
        'width': '40%',
        'column-count': '2'
    }
)

div_button_update_graph = html.Div(
    children=[
        html.Button(
            children='Update graph',
            id='button_update_graph')
    ],
    id='div_button_update_graph',
    style={
        'margin-bottom': '10px'
    }
)

div_controls = html.Div(
    children=[
        div_button_update_graph,
        div_dropdowns,
        div_param_adj
    ],
    id='div_controls',
    style={
        'float': 'right',
        'width': '40%',
    }
)

div_graph_and_controls = html.Div(
    children=[
        div_graph_benchmark,
        div_controls
    ],
    id='div_graph_and_controls',
    style={
        'column-count': '2'
    }
)

# Register all webpage components with Dash app object
app.layout = html.Div(
    children=[
        header,
        div_graph_and_controls
    ],
    id='body',
    style={
        'box-sizing': 'content-box'
    }
)

###############
# Callbacks
###############

# Ideally, the graph would listen to all the events coming from all of the
# controls, but when some controls are regenerated dynamically (because of
# changing the selected benchmark, for example), the callback cannot be
# reassigned
@app.callback(Output('graph_benchmark', 'figure'),
              [],
              [
                  State('dropdown_benchmarks', 'value'),
                  State('dropdown_dtypes', 'value'),
                  State('radio_paramselect', 'value'),
                  State('div_sliders', 'children'),
              ],
              [Event('div_button_update_graph', 'click')])
def update_graph(curr_bench, curr_dtype, indep_var, sliders_container):
    param_filters = {}
    for slider_div in sliders_container:
        # label text, which should be the same as the param name
        param = slider_div['props']['children'][0]['props']['children']
        slider_val = slider_div['props']['children'][1]['props']['value']
        paramval = __bench_info.paramvals(curr_bench, curr_dtype, param)[slider_val]
        if param != indep_var:
            param_filters[param] = paramval

    benchmark = Benchmark(
        filepath=__benchmark_filepath,
        name=curr_bench,
        filters=param_filters
    )

    indepvar_vals = benchmark.collect_param_vals(indep_var, curr_dtype)
    real_times = benchmark.collect_real_times(curr_dtype)

    return {
        'data': [{
            'name': curr_dtype,
            'x': indepvar_vals,
            'y': real_times
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

@app.callback(Output('radio_paramselect', 'options'), [Input('dropdown_benchmarks', 'value')])
def update_radio_paramselect_options(dropdown_value):
    return [{'value': param} for param in __bench_info.params(dropdown_value)]

@app.callback(Output('dropdown_dtypes', 'options'), [Input('dropdown_benchmarks', 'value')])
def update_dropdown_dtypes_options(dropdown_value):
    return [{'label': dtype, 'value': dtype} for dtype in __bench_info.dtypes(dropdown_value)]

@app.callback(Output('dropdown_dtypes', 'value'), [Input('dropdown_dtypes', 'options')])
def update_dropdown_dtypes_value(dropdown_options):
    return dropdown_options[0]['value']

@app.callback(Output('radio_paramselect', 'value'), [Input('dropdown_benchmarks', 'value')])
def update_radio_paramselect_value(dropdown_value):
    return __bench_info.params(dropdown_value)[0]

# There is no fixed set of sliders, so register the callbacks in runtime
def update_slider_disabled(radio_value, slider_id):
    return True if radio_value in slider_id else False

for slider_div in __sliders:
    slider = slider_div.children[1]

    app.callback(Output(slider.id, 'disabled'),
                 [
                     Input('radio_paramselect', 'value'),
                     Input(slider.id, 'id')
                 ]
    )(update_slider_disabled)

@app.callback(Output('radio_paramselect', 'style'),
              [Input('div_sliders', 'children')],
              [State('dropdown_benchmarks', 'value')])
def set_sliders_callback(sliders_container, radio_value):
    for slider_div in sliders_container:
        slider_id = slider_div['props']['children'][1]['props']['id']
        try:
            app.callback(Output(slider_id, 'disabled'),
                         [
                             Input('radio_paramselect', 'value'),
                             Input(slider_id, 'id')
                         ]
               )(update_slider_disabled)
        except CantHaveMultipleOutputs:
            pass

# Different benchmarks may have different parameters, so recreate the sliders
# for the different parameters when another benchmark is chosen
@app.callback(Output('div_sliders', 'children'),
              [Input('dropdown_benchmarks', 'value'), Input('dropdown_dtypes', 'value')])
def change_sliders(curr_bench, curr_dtype):
    slider_divs = []
    indep_var = __bench_info.params(curr_bench)[0]
    graph_inputs = []
    for param in __bench_info.params(curr_bench):
        is_disabled = False
        if param == indep_var:
            is_disabled = True

        paramvals = __bench_info.paramvals(curr_bench, curr_dtype, param)
        slider_div = html.Div(
            children=[
                html.Label(param),
                dcc.Slider(
                    id='slider_' + param,
                    disabled=is_disabled,
                    min=0,
                    max=len(paramvals) - 1,
                    marks={i: paramvals[i] for i in range(len(paramvals))},
                    value=0
                )
            ],
            id = 'slider_div_' + param,
            style={
                'width': '90%',
                'border-bottom': '20px solid white'
            }
        )

        slider = slider_div.children[1]
        slider_divs.append(slider_div)

    return slider_divs

app.css.append_css({'external_url': 'https://codepen.io/chriddyp/pen/bWLwgP.css'})

if __name__ == '__main__':
    app.run_server()
