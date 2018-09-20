# ArrayFire Benchmarks Parser
Provides a package to parse results from
[arrayfire-benchmarks](https://github.com/umar456/arrayfire-benchmarks). Also
includes front-end examples of visualizing the results, using
[Dash by Plotly](https://plot.ly/products/dash/) and Matplotlib

### Dependencies
Run `pip install -r requirements.txt` to get all the necessary Dash dependencies

### Parsing and Plotting
- `afbench.py` provides Python classes to simplify parsing a JSON benchmark
results file from arrayfire-benchmarks.
- `example_dash.py` is a Dash-based example to get an idea on how to use the
parser. This plots a simple graph an ArrayFire FFT benchmark
- `example_matplotlib.py` is a Matplotlib-based version of the same example.
- `viz.py` runs a more interactive tool, for visualizing any ArrayFire benchmark
JSON file (at least in concept). Run it as `python viz.py <benchmark_filepath>`.
However, it's still kinda buggy at this point, and only works perfectly for
`fft.json`
