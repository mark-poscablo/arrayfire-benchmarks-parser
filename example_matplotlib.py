from afbench import Benchmark, BenchmarkInfo

import numpy as np
import matplotlib.pyplot as plt

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

np_fft1_x = np.asarray(fft1_x_vals)
np_fft1_y = np.asarray(fft1_y_vals)
np_fft2_x = np.asarray(fft2_x_vals)
np_fft2_y = np.asarray(fft2_y_vals)

plt.plot(np_fft1_x, np_fft1_y, 'bo-',
         np_fft2_x, np_fft2_y, 'go-'
)
plt.xscale('log')
plt.yscale('log')
plt.show()
