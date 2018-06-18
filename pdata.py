import pylab
import numpy as np
import pandas as pd


#global last_n_frames, n, SPF
#n = 5
#last_n_frames = pylab.zeros(n * SPF)


def process_data(signal, samples_per_bit, samples_per_frame):
	
	#global last_n_frames

	
	SPF = samples_per_frame

	columns = ['ASV', 'var', 'env', 'thr', 'bfr', 'iav', 'dms']
	
		#Absolute signal value
		#Variance
		#Envelope
		#Threshold
		#Bit Frontiers
		#Intra Bit Frontiers average value
		#Demodulated signal

	alldata_Frame = pd.DataFrame(columns = columns)
	
	word_frontiers = define_wordfrontiers(signal, samples_per_bit)
	
	sliced_signal = slice_signal(signal, word_frontiers)
	
	print(len(sliced_signal))
	
	envelope = []
	envelope = enveloper(signal, SPF)
	threshold = (envelope[0] + envelope[1]) / 2
	
	
	bit_frontier = define_bitfrontiers(signal, samples_per_bit, threshold)
	
	
	
	
	
				
	
	alldata_Frame
	
	return alldata_Frame
	

def variance(args,window):

	result = []
	window = int(window)

	
	for x in range(int(len(args)-window-1)):
		result.append(np.var(args[x:x+window]))
	
	#result[0:floor(window/2)-1] = result[floor(window/2)]
	#result[-floor(window/2):end] = result[-floor(window/2)-1]
	
	return result
    
    
    
    
def enveloper(signal, SPF):
	
	
	#global last_n_frames          # A INCLUIR MAIS TARDE
	
	#last_n_frames[0:len(last_n_frames - SPF)] = last_n_frames[SPF:end]
	#last_n_frames[-SPF:end] = signal
	#I = np.nonzero(last_n_frames)
	#first_non_zero = I[0][0]
	
	
	yupper = np.percentile(signal, 90)
	ylower = np.percentile(signal, 10)
	
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
	
	bit_frontiers = np.zeros(number_of_bits)
	
	for b in range(number_of_bits):	
			
		bit_frontiers[b] = offset_index + samples_per_bit*b
		

		
	return bit_frontiers
	
	
def define_wordfrontiers(signal, samples_per_bit):
	
	window = samples_per_bit * 10
	
	window_variance = variance(signal, window)

	split = max(window_variance) * 0.5
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
	
	print("len indexes")
	print(len(indexes[0])-1)

	
	for x in range(len(indexes[0])-2):
	
		a = indexes[0][x]
		b = indexes[0][x+1]

		
		sliced_signal.append(signal[a:b])
	
	print("Sinal Fatiado ") 
	print(sliced_signal)
	print(indexes)
		
	return sliced_signal

#if __name__ == '__main__':
#    import sys
#    sys.exit(main(sys.argv))
