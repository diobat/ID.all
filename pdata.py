import pylab
import numpy as np
import pandas as pd


#global last_n_frames, n, SPF
#n = 5
#last_n_frames = pylab.zeros(n * SPF)


def process_data(signal, samples_per_bit, samples_per_frame):
	
	#global last_n_frames

	SPF = samples_per_frame
	
	word_frontiers = define_wordfrontiers(signal, samples_per_bit)
	
	sliced_signal = slice_signal(signal, word_frontiers)
	
	envelope = []
	envelope = enveloper(signal, SPF)
	threshold = np.mean(envelope)
	result = []
	
	for x in range(len(sliced_signal)):
		
		bit_frontier = define_bitfrontiers(sliced_signal[x], samples_per_bit, threshold)
		iavs = interval_average(sliced_signal[x], bit_frontier)
		demodulated_signal = demodulator(iavs, threshold)
		
		result.extend(demodulated_signal)
		
	
	return result
	

def variance(args,window):

	result = []
	window = int(window)

	
	for x in range(int(len(args)-window-1)):
		result.append(np.var(args[x:x+window]))
	
	result1 = [result[0]] * int(np.floor(window/2))
	result2 = [result[-1]] * int(np.floor(window/2))


	result1.extend(result)
	result1.extend(result2)
	
	print(len(result1))
	
	return result1
    
    
    
    
def enveloper(signal, SPF):
	
	
	#global last_n_frames 
	
	#last_n_frames[0:len(last_n_frames - SPF)] = last_n_frames[SPF:end]
	#last_n_frames[-SPF:end] = signal
	#I = np.nonzero(last_n_frames)
	#first_non_zero = I[0][0]
	
	
	yupper = np.percentile(signal, 85)
	ylower = np.percentile(signal, 15)
	
	envelope = [yupper, ylower]
	
	return envelope

def define_bitfrontiers(signal, samples_per_bit, threshold):
	
	rounded_samples = int(np.ceil(samples_per_bit))
	quality = np.zeros(rounded_samples)
	number_of_bits = int(np.floor((len(signal)/samples_per_bit)))
	
	for i in range(rounded_samples):
		
		amplitudeSum = 0
		
		for a in range(number_of_bits - 2):
		
			b1 = int(np.floor(a*samples_per_bit) + i)
			b2 = int(np.floor((a+1)*samples_per_bit) + i)
			
			signal_mean = np.mean(signal[b1:b2])
			amplitudeSum = abs(signal_mean - threshold)
			
			quality[i] = quality[i] + amplitudeSum
			
	offset_index = np.argmax(quality)	
	
	bit_frontiers = np.zeros(number_of_bits, dtype = int)
	
	for b in range(number_of_bits):	
			
		bit_frontiers[b] = offset_index + round(samples_per_bit*b)

		
	return bit_frontiers
	
	
def define_wordfrontiers(signal, samples_per_bit):
	
	window = samples_per_bit * 10
	
	window_variance = variance(signal, window)
	
	
	#stretched_variance = np.array(window_variance)*10
	#pylab.plot(signal, 'b')
	#pylab.plot(stretched_variance, 'r')
	#pylab.show()


	#split = max(window_variance) * 0.5
	split = np.percentile(window_variance, 0.5)
	print(split)
	word_map = (window_variance > split)
	word_frontiers_map = np.bitwise_xor(word_map[0:-2], word_map[1:-1])
	word_frontiers_map[0] = 1
	word_frontiers_map[-1] = 1
	
	
	nnz = np.count_nonzero(word_frontiers_map)
	
	
	word_frontiers = np.ndarray.nonzero(word_frontiers_map)


	#pylab.plot(window_variance)
	#pylab.show()
	
	
	#print("Word_Frontiers")
	#print(word_frontiers)
	
	return word_frontiers
	
def slice_signal(signal, indexes):
	
	sliced_signal = []
	
	#print("len indexes")
	#print(len(indexes[0])-1)

	
	for x in range(len(indexes[0])-1):
	
		a = indexes[0][x]
		b = indexes[0][x+1]

		
		sliced_signal.append(signal[a:b])
	
	result = np.asarray(sliced_signal)
	
	#print("Sinal Fatiado ") 
	#print(sliced_signal)
	#print(indexes)
		
	return result
	
def interval_average(signal, indexes):
	
	averages = np.zeros(max(len(indexes)-1, 0))
	
	#print(indexes)
	
	for x in range(len(averages)):
		averages[x] = np.mean(signal[indexes[x]:indexes[x+1]])
		
	return averages
	
def demodulator(iavs, threshold):

	result = np.asarray(iavs, dtype=int)
	
	result[iavs > threshold] = 1
	result[iavs < threshold] = 0
	
	result.tolist()
	
	return result
		
	

#if __name__ == '__main__':
#    import sys
#    sys.exit(main(sys.argv))
