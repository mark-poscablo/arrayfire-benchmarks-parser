# ArrayFire Benchmarks Parser
Provides a package to parse results from [arrayfire-benchmarks](https://github.com/umar456/arrayfire-benchmarks). Also includes front-end examples of visualizing the results, using [Dash by Plotly](https://plot.ly/products/dash/)

### Dependencies
Run `pip install -r requirements.txt` to get all the necessary Dash dependencies

### Parsing and Plotting
`afbench.py` provides Python classes to simplify parsing a JSON benchmark results file from arrayfire-benchmarks. See `quick_example.py` to get an idea on how to use it to make a simple graph of an ArrayFire FFT benchmark. For a more interactive tool, try running `python viz.py <benchmark_filepath>`, although it's still buggy and only works perfectly for `fft.json`
