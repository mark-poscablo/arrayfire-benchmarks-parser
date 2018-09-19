import dash
from dash.dependencies import Input, Output, State, Event
import dash_core_components as dcc
import dash_html_components as html
from dash.exceptions import CantHaveMultipleOutputs

import json
import plotly.graph_objs as go

from datetime import datetime as dt

from copy import deepcopy

class Attributes:
    NAME = 'name'
    RUN_TYPE = 'run_type'
    ITERATIONS = 'iterations'
    REAL_TIME = 'real_time'
    CPU_TIME = 'cpu_time'
    TIME_UNIT = 'time_unit'

class Params:
    ELEMENTS = 'elements'
    DIM0 = 'dim0'
    DIM1 = 'dim1'
    DIM2 = 'dim2'
    DIM3 = 'dim3'

class Dtypes:
    f32 = 'f32'
    c32 = 'c32'
    f64 = 'f64'
    c64 = 'c64'
    b8  = 'b8'
    s32 = 's32'
    u32 = 'u32'
    u8  = 'u8'
    s64 = 's64'
    u64 = 'u64'
    s16 = 's16'
    u16 = 'u16'

class Result:
    def __init__(self, result_json):
        self._result_json = result_json
        self._params = {}
        name_str = self._result_json[Attributes.NAME]
        name_split = name_str.split('/')
        self._benchmark_name = name_split[0]
        self._dtype = name_split[1]
        # if self._benchmark_name == 'randuDimsBench':
        #     print('Result.__init__: name_split: {}'.format(name_split))
        for i in range(2, len(name_split)):
            param_str = name_split[i].split(':')
            param_name = param_str[0].translate({ord(char): None for char in '[]'})
            self._params[param_name] = int(param_str[1])

    @property
    def benchmark_name(self):
        return self._benchmark_name

    @property
    def dtype(self):
        return self._dtype

    @property
    def params(self):
        return deepcopy(self._params)

    def __getitem__(self, key):
        return self._result_json[key]

    @property
    def run_type(self):
        return self._result_json[Attributes.RUN_TYPE]

    @property
    def iterations(self):
        return self._result_json[Attributes.ITERATIONS]

    @property
    def real_time(self):
        return self._result_json[Attributes.REAL_TIME]

    @property
    def cpu_time(self):
        return self._result_json[Attributes.CPU_TIME]

    @property
    def time_unit(self):
        return self._result_json[Attributes.TIME_UNIT]

    def passes_filters(self, constraints):
        is_pass = True
        for k, v in constraints.items():
            if k in self._params:
                is_pass = is_pass and self._params[k] == v
            else:
                is_pass = False
            if not is_pass:
                break
        return is_pass

class Benchmark:
    def __init__(self, filepath, name, filters={}):
        self._name = name
        self._filters = filters

        self._avail_dtypes = []
        self._avail_params = None

        self._param_vals = {}
        self._run_types = {}
        self._iterations = {}
        self._real_times = {}
        self._cpu_times = {}
        self._time_units = {}

        self._first_iter = True

        json_doc = None
        with open(filepath) as bench_file:
            json_doc = json.load(bench_file)

        for result in json_doc['benchmarks']:
            _result = Result(result)

            # print('Benchmark.__init__: name: {}'.format(_result.benchmark_name))
            # print('Benchmark.__init__: filters: {}'.format(filters))
            if _result.benchmark_name == name:
                # print('Benchmark.__init__: elem found!')
                if self._first_iter:
                    self._avail_params = sorted(_result.params.keys())
                    # print('Benchmark.__init__: self._avail_params: {}'.format(self._avail_params))
                    self._first_iter = False

                if _result.dtype not in self._avail_dtypes:
                    self._avail_dtypes.append(_result.dtype)
                    self._param_vals[_result.dtype] = {}
                    for param in self._avail_params:
                        self._param_vals[_result.dtype][param] = []
                    self._run_types[_result.dtype] = []
                    self._iterations[_result.dtype] = []
                    self._real_times[_result.dtype] = []
                    self._cpu_times[_result.dtype] = []
                    self._time_units[_result.dtype] = []

                if _result.passes_filters(filters):
                    for param in self._avail_params:
                        self._param_vals[_result.dtype][param].append(_result.params[param])
                    self._run_types[_result.dtype].append(_result.run_type)
                    self._iterations[_result.dtype].append(_result.iterations)
                    self._real_times[_result.dtype].append(_result.real_time)
                    self._cpu_times[_result.dtype].append(_result.cpu_time)
                    self._time_units[_result.dtype].append(_result.time_unit)

        self._avail_dtypes.sort()

    @property
    def name(self):
        return self._name

    @property
    def filters(self):
        return deepcopy(self._filters)

    @property
    def avail_names(self):
        return deepcopy(self._avail_names)

    @property
    def avail_dtypes(self):
        return deepcopy(self._avail_dtypes)

    @property
    def avail_params(self):
        return deepcopy(self._avail_params)

    def collect_param_vals(self, param_name, dtype):
        print('collect_param_vals: self._param_vals: {}'.format(self._param_vals))
        print('collect_param_vals: param_name: {}'.format(param_name))
        print('collect_param_vals: dtype: {}'.format(dtype))
        return deepcopy(self._param_vals[dtype][param_name])

    def collect_run_types(self, dtype):
        return deepcopy(self._run_types[dtype])

    def collect_iterations(self, dtype):
        return deepcopy(self._iterations[dtype])

    def collect_real_times(self, dtype):
        return deepcopy(self._real_times[dtype])

    def collect_cpu_times(self, dtype):
        return deepcopy(self._cpu_times[dtype])

    def collect_time_units(self, dtype):
        return deepcopy(self._time_units[dtype])

class BenchmarkInfo():
    def __init__(self, filepath):
        self._benchmark_names = []
        self._dtypes = {}
        self._params = {}
        self._attributes = []
        self._paramvals = {}
        self._minparamvals = {}
        self._first_iter = True

        json_doc = None
        with open(filepath) as bench_file:
            json_doc = json.load(bench_file)

        for result in json_doc['benchmarks']:
            _result = Result(result)

            if self._first_iter:
                self._attributes = sorted(result.keys())
                self._first_iter = False

            benchmark_name = _result.benchmark_name
            if benchmark_name not in self._benchmark_names:
                self._benchmark_names.append(benchmark_name)
                self._params[benchmark_name] = sorted(_result.params.keys())
                self._dtypes[benchmark_name] = []
                self._paramvals[benchmark_name] = {}
                self._minparamvals[benchmark_name] = {}
                for param in self._params[benchmark_name]:
                    self._paramvals[benchmark_name][param] = []
                    self._minparamvals[benchmark_name][param] = _result.params[param]

            if _result.dtype not in self._dtypes[benchmark_name]:
                self._dtypes[benchmark_name].append(_result.dtype)

            for param in self._params[benchmark_name]:
                # print('benchmark_name: {}'.format(benchmark_name))
                # print('param: {}'.format(param))
                # print('_result.params: {}'.format(_result.params))
                # print('_result.params[{}]: {}'.format(param, _result.params[param]))
                # print('self._minparamvals[{}][{}]: {}'.format(benchmark_name, param,
                #                                               self._minparamvals[benchmark_name][param]))
                # print()
                if _result.params[param] < self._minparamvals[benchmark_name][param]:
                    self._minparamvals[benchmark_name][param] = _result.params[param]
                if _result.params[param] not in self._paramvals[benchmark_name][param]:
                    self._paramvals[benchmark_name][param].append(_result.params[param])

        self._benchmark_names.sort()
        for benchmark_name in self._benchmark_names:
            self._dtypes[benchmark_name].sort()
            for param in self._params[benchmark_name]:
                self._paramvals[benchmark_name][param].sort()

    @property
    def benchmark_names(self):
        return deepcopy(self._benchmark_names)

    def dtypes(self, benchmark_name):
        return deepcopy(self._dtypes[benchmark_name])

    def params(self, benchmark_name):
        return deepcopy(self._params[benchmark_name])

    @property
    def attributes(self):
        return deepcopy(self._attributes)

    def paramvals(self, benchmark_name, param):
        return deepcopy(self._paramvals[benchmark_name][param])

    def minparamval(self, benchmark_name, param):
        return self._minparamvals[benchmark_name][param]

app = dash.Dash('ArrayFire Benchmarks POC')
app.config['suppress_callback_exceptions'] = True

__benchmark_filepath = 'fft.json'
__bench_info = BenchmarkInfo(__benchmark_filepath)
curr_bench = __bench_info.benchmark_names[0]
indep_var = __bench_info.params(curr_bench)[0]
benchselect_opts = [{'label': benchname, 'value': benchname}
                    for benchname in __bench_info.benchmark_names]
sliders = []
paramselect_opts = []
for param in __bench_info.params(curr_bench):
    is_disabled = False
    if param == indep_var:
        is_disabled = True

    paramvals = __bench_info.paramvals(curr_bench, param)
    sliders.append(
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

    paramselect_opts.append({'value': param})

header = html.Header(
    children=[
        html.H1('ArrayFire Benchmarks')
    ],
    style={
        'text-align': 'center'
    }
)

graph_pane = html.Div(
    children=[
        dcc.Graph(
            id='graph_benchmark',
            style={
            }
        )
    ],
    id = 'div_graph_pane',
    style={
        'float': 'left',
        'width': '60%'
    }
)

div_sliders = html.Div(
    children=sliders,
    id='div_sliders',
    style={
        'float': 'right',
        'width': '90%'
    }
)

div_selector = html.Div(
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
        div_selector
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
            options=benchselect_opts,
            value=benchselect_opts[0]['value'],
            clearable=False,
            searchable=False
        )
    ],
    id='div_dropdown_benchmarks',
    style={
        'width': '30%',
        'margin-bottom': '10px'
    }
)

div_button_update_graph = html.Div(
    children=[
        html.Button('Update graph', id='button_update_graph')
    ],
    id='div_button_update_graph',
    style={
        'margin-bottom': '10px'
    }
)

div_controls = html.Div(
    children=[
        div_button_update_graph,
        div_dropdown_benchmarks,
        div_param_adj
    ],
    id='div_controls',
    style={
        'float': 'right',
        'width': '40%',
    }
)

graph_and_controls = html.Div(
    children=[
        graph_pane,
        div_controls
    ],
    id='graph_and_controls',
    style={
        'column-count': '2',
        'width': '100%'
    }
)

app.layout = html.Div(
    children=[
        header,
        graph_and_controls
    ],
    id='body',
    style={
        'box-sizing': 'content-box'
    }
)

graph_inputs = []
for slider_div in sliders:
    slider = slider_div.children[1]
    graph_inputs.append(Input(slider.id, 'value'))
graph_inputs.append(Input('radio_paramselect', 'value'))
graph_inputs.append(Input('dropdown_benchmarks', 'value'))

@app.callback(Output('graph_benchmark', 'figure'),
              [],
              [
                  State('dropdown_benchmarks', 'value'),
                  State('radio_paramselect', 'value'),
                  State('div_sliders', 'children'),
              ],
              [Event('div_button_update_graph', 'click')])
def update_graph(curr_bench, indep_var, sliders_container):
    print('update_graph inputs:')
    # for arg in args:
    #     print(arg)
    # sliders_len = len(sliders)
    # indep_var = args[sliders_len + 0]
    # curr_bench = args[sliders_len + 1]
    print('Selected benchmark: {}'.format(curr_bench))
    print('Selected indep_var: {}'.format(indep_var))
    param_filters = {}
    for slider_div in sliders_container:
        # label text, which should be the same as the param name
        param = slider_div['props']['children'][0]['props']['children']
        slider_val = slider_div['props']['children'][1]['props']['value']
        paramval = __bench_info.paramvals(curr_bench, param)[slider_val]
        if param != indep_var:
            print('Selected {}: {}'.format(
                param,
                paramval
            ))
            param_filters[param] = paramval

    benchmark = Benchmark(
        filepath=__benchmark_filepath,
        name=curr_bench,
        filters=param_filters
    )

    sizes = benchmark.collect_param_vals(indep_var, Dtypes.f32)
    f32_times = benchmark.collect_real_times(Dtypes.f32)

    return {
        'data': [{
            'name': Dtypes.f32,
            'x': sizes,
            'y': f32_times
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
    return [{'label': param, 'value': param} for param in __bench_info.params(dropdown_value)]

@app.callback(Output('radio_paramselect', 'value'), [Input('dropdown_benchmarks', 'value')])
def update_radio_paramselect_value(dropdown_value):
    return __bench_info.params(dropdown_value)[0]

def update_slider_disabled(radio_value, slider_id):
    print('update_slider_disabled: [{}] radio_value:{}'.format(slider_id, radio_value))
    return True if radio_value in slider_id else False

for slider_div in sliders:
    slider = slider_div.children[1]
    print(slider.id)

    app.callback(Output(slider.id, 'disabled'),
                 [
                     Input('radio_paramselect', 'value'),
                     Input(slider.id, 'id')
                 ]
    )(update_slider_disabled)

@app.callback(Output('radio_paramselect', 'style'),
              [Input('div_sliders', 'children')],
              [State('dropdown_benchmarks', 'value')])
def set_slider_disable_callback(sliders_container, radio_value):
    for slider_div in sliders_container:
        slider_id = slider_div['props']['children'][1]['props']['id']
        print('set_slider_disable_callback: {}'.format(slider_id))
        try:
            app.callback(Output(slider_id, 'disabled'),
                         [
                             Input('radio_paramselect', 'value'),
                             Input(slider_id, 'id')
                         ]
               )(update_slider_disabled)
        except CantHaveMultipleOutputs:
            pass

    for k, v in app.callback_map.items():
        print('{}: {}'.format(k, v))
        print()

@app.callback(Output('div_sliders', 'children'), [Input('dropdown_benchmarks', 'value')])
def update_sliders(dropdown_value):
    print('update_sliders: curr_bench: {}'.format(dropdown_value))
    print('update_sliders: params available: {}'.format(__bench_info.params(dropdown_value)))

    slider_divs = []
    indep_var = __bench_info.params(dropdown_value)[0]
    graph_inputs = []
    for param in __bench_info.params(dropdown_value):
        is_disabled = False
        if param == indep_var:
            is_disabled = True

        paramvals = __bench_info.paramvals(dropdown_value, param)
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
        print(slider.id)

        # app.callback(Output(slider.id, 'disabled'),
        #              [
        #                  Input('radio_paramselect', 'value'),
        #                  Input(slider.id, 'id')
        #              ]
        # )(update_slider_disabled)

        # graph_inputs.append(Input(slider.id, 'value'))
        slider_divs.append(slider_div)

    # graph_inputs.append(Input('radio_paramselect', 'value'))
    # graph_inputs.append(Input('dropdown_benchmarks', 'value'))
    # app.callback(Output('graph_benchmark', 'figure'), graph_inputs)(update_graph)

    return slider_divs

app.css.append_css({'external_url': 'https://codepen.io/chriddyp/pen/bWLwgP.css'})

if __name__ == '__main__':
    # main()
    app.run_server()
