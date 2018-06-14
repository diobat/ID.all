import pylab
import numpy as np
import pandas as pd


global last_n_frames, n
n = 5
last_n_frames = pylab.zeros(n * SPF)


def process_data(raw_signal, samples_per_bit, SPF):
	
	global last_n_frames
	
	window = samples_per_bit * 10
	
	window_variance = variance(raw_signal, window)
	
	
	
	envelope = envelope(signal, SPF)
	
	threshold = (envelope[0] + envelope[1]) / 2
	
	bit_frontier = define_bitfrontiers(signal, samples_per_bit, threshold)
	
	
	allData = { 'ASV' : [signal],
				'var' : [window_variance],
				'env' : [envelope],
				'thr' : [threshhold],
				'bfr' : [bit_frontier],
				'iav' : [ifr_avg_value],
				'dms' : [demodulated_signal] }
	
	return allData
	

def variance(args,window):

	result = []
	
	for x in range(len(args)-window):
		result[x+floor(window/2)] = np.var(args[x:x+window])
	
	result[0:floor(window/2)-1] = result[floor(window/2)]
	result[-floor(window/2):end] = result[-floor(window/2)-1]
	
    return result
    
    
    
    
def envelope(signal, SPF):
	
	global last_n_frames
	
	last_n_frames[0:len(last_n_frames - SPF)] = last_n_frames[SPF:end]
	I = np.nonzero(last_n_frames)
	first_non_zero = I[0][0]
	
	yupper = np.percentile(signal, 90)
	ylower = np.percentile(signal, 10)
	
	envelope = [yupper, ylower]
	
	return envelope

def define_bitfrontiers(signal, SPB, threshold)
	
	quality = np.zeros(ceil(samples_per_bit))
	number_of_bits = np.floor(len(signal)/SPB)
	
	for i in range(len(quality)):
		amplitudeSum = 0;
		
		for a in range(number_of_bits - 2):
		
			b1 = np.floor(a*samples_per_bit) + i
			b2 = np.floor((a+1)*samples_per_bit) + i;
			
			signal_mean = np.mean(signal[b1:b2])
			amplitudeSum = abs(signal_mean - threshold)
			
			quality[i] = quality[i] + amplitudeSum
			
	offset_index = np.argmax(quality)	
	
		bit_frontiers = np.zeros(number_of_bits)
	
	for b in range(number_of_bits+1):	
			
		bit_frontiers[b] = offset_index + SPB*b
		
	return bit_frontiers
	
    

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
