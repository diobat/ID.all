import pylab
import pdata 
from rtlsdr import *	#SDR
import numpy as np



sample_rate = 226e3
frame_size = 16 * 1024 # 32
signal_frequency = 3650
bits_per_word = 32
signal_period = 1/signal_frequency
samples_per_bit = sample_rate * signal_period


#a = []
#b = range(5)

#c = range (7)
#a.append(b)
#a.append(c)

#print(a)




allsamples = pylab.load('outfile.npy')
print("Sample Size: " + str(len(allsamples)))

allsamples = allsamples[10000:-1]


allsamples_parsed = pdata.process_data(allsamples, samples_per_bit, frame_size)


print(allsamples_parsed)
