import matplotlib.pyplot as plt
import numpy as np
import filterGen

pre_filter = np.load('outfile_samples.npy')


window = 65 * 8

start = 205100
start2 = 205100

sample_rate = 226000
symbol_rate = 3650

nyq_freq = sample_rate/2

filter_order = 2
low_cutoff = 1
high_cutoff = 3650

post_filter = filterGen.bp_butter(pre_filter, [low_cutoff, high_cutoff], filter_order, sample_rate)
#print('post filter lenght: ' + str(len(post_filter)))





post_filter = post_filter[start2:start2+window]

index = range(len(post_filter))
post_dcim = post_filter[::10]


fig = plt.figure()

fig.suptitle('Signal decimation simulator', fontsize=16)


SMALL_SIZE = 14
MEDIUM_SIZE = 10
BIGGER_SIZE = 16

plt.rc('font', size=SMALL_SIZE)          # controls default text sizes
plt.rc('axes', titlesize=BIGGER_SIZE)     # fontsize of the axes title
plt.rc('axes', labelsize=MEDIUM_SIZE)    # fontsize of the x and y labels
plt.rc('xtick', labelsize=SMALL_SIZE)    # fontsize of the tick labels
plt.rc('ytick', labelsize=SMALL_SIZE)    # fontsize of the tick labels
plt.rc('legend', fontsize=SMALL_SIZE)    # legend fontsize
plt.rc('figure', titlesize=24)  # fontsize of the figure title


plt.subplot(211)
plt.stem(index, post_filter)
plt.title('Signal excerpt pre decimation')
plt.xlabel('Sample Index')
plt.ylabel('Quantization')


plt.subplot(212)
plt.stem(index[::10], post_dcim)
plt.title('Signal excerpt post decimation')
plt.xlabel('Sample Index')
plt.ylabel('Quantization')

plt.show()
