from copy import deepcopy
import json

class Attributes:
    name = 'name'
    run_type = 'run_type'
    iterations = 'iterations'
    real_time = 'real_time'
    cpu_time = 'cpu_time'
    time_unit = 'time_unit'

class Params:
    elements = 'elements'
    dim0 = 'dim0'
    dim1 = 'dim1'
    dim2 = 'dim2'
    dim3 = 'dim3'

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
        name_str = self._result_json[Attributes.name]
        name_split = name_str.split('/')
        # Assumption: 'name' is always benchmark_name/dtype/param:val/param:val/...
        self._benchmark_name = name_split[0]
        self._dtype = name_split[1]
        for i in range(2, len(name_split)):
            param_str = name_split[i].split(':')
            # Ignore brackets around param names for now
            param_name = param_str[0].translate({ord(char): None for char in '[]'})
            # Assumption: param values are always ints
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
        return self._result_json[Attributes.run_type]

    @property
    def iterations(self):
        return self._result_json[Attributes.iterations]

    @property
    def real_time(self):
        return self._result_json[Attributes.real_time]

    @property
    def cpu_time(self):
        return self._result_json[Attributes.cpu_time]

    @property
    def time_unit(self):
        return self._result_json[Attributes.time_unit]

    def passes_filters(self, constraints):
        is_pass = True
        for k, v in constraints.items():
            if k in self._params:
                is_pass = is_pass and self._params[k] == v
            else:
                # Probably should throw an exception here
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

            if _result.benchmark_name == name:
                # Assumption: all param names within a benchmark are the same
                if self._first_iter:
                    self._avail_params = sorted(_result.params.keys())
                    self._first_iter = False

                # Assumption: each benchmark's dtypes may differ
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
        self._minparamval = {}
        self._first_iter = True

        json_doc = None
        with open(filepath) as bench_file:
            json_doc = json.load(bench_file)

        for result in json_doc['benchmarks']:
            _result = Result(result)

            # Assumption: all benchmark attributes within the file are the same
            if self._first_iter:
                self._attributes = sorted(result.keys())
                self._first_iter = False

            benchmark_name = _result.benchmark_name
            if benchmark_name not in self._benchmark_names:
                self._benchmark_names.append(benchmark_name)
                # Assumption: all param names within a benchmark are the same
                self._params[benchmark_name] = sorted(_result.params.keys())
                self._dtypes[benchmark_name] = []
                self._paramvals[benchmark_name] = {}
                self._minparamval[benchmark_name] = {}

            # Assumption: each benchmark's dtypes might be different
            if _result.dtype not in self._dtypes[benchmark_name]:
                self._dtypes[benchmark_name].append(_result.dtype)
                self._paramvals[benchmark_name][_result.dtype] = {}
                self._minparamval[benchmark_name][_result.dtype] = {}
                for param in self._params[benchmark_name]:
                    self._paramvals[benchmark_name][_result.dtype][param] = []
                    self._minparamval[benchmark_name][_result.dtype][param] = _result.params[param]

            for param in self._params[benchmark_name]:
                if _result.params[param] not in self._paramvals[benchmark_name][_result.dtype][param]:
                    self._paramvals[benchmark_name][_result.dtype][param].append(_result.params[param])
                if _result.params[param] < self._minparamval[benchmark_name][_result.dtype][param]:
                    self._minparamval[benchmark_name][param] = _result.params[param]

        self._benchmark_names.sort()
        for benchmark_name in self._benchmark_names:
            self._dtypes[benchmark_name].sort()
            for param in self._params[benchmark_name]:
                for dtype in self._dtypes[benchmark_name]:
                    self._paramvals[benchmark_name][dtype][param].sort()

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

    def paramvals(self, benchmark_name, dtype, param):
        return deepcopy(self._paramvals[benchmark_name][dtype][param])

    def minparamval(self, benchmark_name, dtype, param):
        return self._minparamval[benchmark_name][dtype][param]
