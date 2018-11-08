import pylab
import numpy as np
#import pandas as pd
import time
import matplotlib.pyplot as plt



global debug, debug1, debug2

debug = False 	# Should execution be halted at every step to generate graphs?
debug1 = False 	# Should step by step timestamps be printed?
debug2 = False	# Should a global timestamp be printed?

def compare_signal(signal, samples_per_bit):
	
	s
	signal_ceil = max(signal)
	signal_floor = min(signal)
	#print("\n\namplitude" + str(signal_ceil - signal_floor) + "\n\n")
	

	t = time.time()

	global debug, debug1, debug2

	
	SPF = len(signal)

	word_frontiers, window_variance, variance_split = define_wordfrontiers(signal, samples_per_bit)

	sliced_signal, packet_start_index = slice_signal(signal, word_frontiers, window_variance, variance_split)

	envelope = []
	envelope = enveloper(sliced_signal, SPF)
	#threshold = abs(envelope[1] - envelope[0]) * 0.50 + envelope[1]
	
	#print('envelope = ' + str(envelope))
	
	threshold = []
	for x in range(len(envelope[0])):
		threshold.append((envelope[0][x] + envelope[1][x]) * 0.3)
	
	#print('threshold = ' + str(threshold))
	
	result = []

	allbit_frontier = []
	alliavs = []
	extended_alliavs = []
	alldemodulated_signal = []
	counter = 0

	#print('sliced signal lenght')
	#print(len(sliced_signal))
	#print('number of thresholds')
	#print(len(threshold))
	
	for x in range(len(sliced_signal)):


		bit_frontier = define_bitfrontiers(sliced_signal[x], samples_per_bit, threshold[x])
		iavs = interval_average(sliced_signal[x], bit_frontier)
		demodulated_signal = demodulator(iavs, threshold[x])

		result.extend(demodulated_signal)

		if debug == True:
			allbit_frontier.extend([x+counter for x in bit_frontier])
			alliavs.extend(iavs)

			counter += len(sliced_signal[x])

	for x in range(len(alliavs)):
		a = [alliavs[x]] * round(samples_per_bit)
		extended_alliavs.extend(a)

	if debug == True:
		full_thresholds = []
		sliced_signal2 = []
		for x in range(len(sliced_signal)):
			one_threshold = [threshold[x]] * len(sliced_signal[x])
			full_thresholds.extend(one_threshold)
			sliced_signal2.extend(sliced_signal[x])
		
		print(len(full_thresholds))
		pylab.plot(full_thresholds,'k')
		pylab.plot(sliced_signal2, 'b')
		#pylab.plot(extended_alliavs, 'red')

		for xc in allbit_frontier:
			plt.axvline(x=xc)
			
		for xv in packet_start_index:
			plt.axvline(x=xv, color='red')
		

		pylab.show()
		input("Press space to continue")

	if debug1 == True or debug2 == True:
		delta_t = time.time() -t
		print("TOTAL TIME				" + str(delta_t))
	return result


def variance(args,window):

	t = time.time()

	global debug, debug1

	result = []
	window = int(window)
	y = range(int(len(args)-window-1))
	step1 = 50		# We don't have to calculate the variance at every sample, so we define a step of 50
	step2 = 10 		# When we DO calculate the variance, we don't have to take into account every sample inside the [x: x+window] interval, thus we can define a second step1

	#Both of these steps are to reduce processing power usage, they have a MASSIVE influence. The higher they are the faster the program goes, if they go too high everything stops working, handle with care.

	#for x in range(int(len(args)-window-1)):
	for x in y[0:-1:step1]:
		#print(len(args[x:x+window]))
		#print(len(args[x:x+window:step2]))
		result.extend([np.var(args[x:x+window:step2])] * step1)  #This multiplication is to turn a number into an array with a length of step

	result1 = [result[0]] * int(np.floor(window/2))
	result2 = [result[-1]] * int(np.floor(window/2))


	result1.extend(result)
	result1.extend(result2)

	if debug1 == True:
		delta_t = time.time() -t
		print("variance			" + str(delta_t))
	return result1

def enveloper(signal_sliced, SPF):

	t = time.time()

	global debug, debug1

	#last_n_frames[0:len(last_n_frames - SPF)] = last_n_frames[SPF:end]
	#last_n_frames[-SPF:end] = signal
	#I = np.nonzero(last_n_frames)
	#first_non_zero = I[0][0]
	
	yupper = []
	ylower = []	
	
	for x in range(len(signal_sliced)):
		#print(len(signal_sliced[x]))
		#print(type(signal_sliced[x]))
		#print(type(np.percentile(signal_sliced[x], 97)))
		
		yupper.append(np.percentile(signal_sliced[x], 97))
		ylower.append(np.percentile(signal_sliced[x],  3))

	#print(yupper)
	#print(ylower)
	envelope = [yupper, ylower]
	#print(envelope)

	if debug1 == True:
		delta_t = time.time() -t
		print("enveloper			" + str(delta_t))
	return envelope

def define_bitfrontiers(signal, samples_per_bit, threshold):

	t = time.time()

	global debug, debug1

	rounded_SPB = int(np.ceil(samples_per_bit))
	quality = np.zeros(rounded_SPB)
	number_of_bits = int(np.floor((len(signal)/samples_per_bit)))
	range_number_of_bits = range(number_of_bits - 1)
	step = 2
	#step = int(samples_per_bit/32)

	for i in range(rounded_SPB):

		amplitudeSum = 0

		for a in range_number_of_bits[0:-1:step] :

			b1 = int(np.floor(a*samples_per_bit) + i)
			b2 = int(np.floor((a+1)*samples_per_bit) + i)

			signal_mean = np.mean(signal[b1:b2])
			amplitudeSum = abs(signal_mean - threshold)

			quality[i] = quality[i] + amplitudeSum

	offset_index = np.argmax(quality)

	bit_frontiers = np.zeros(number_of_bits, dtype = int)

	for b in range(number_of_bits):

		bit_frontiers[b] = offset_index + round(samples_per_bit*b)
	np.append(bit_frontiers,len(signal))

	if debug1 == True:
		delta_t = time.time() -t
		print("define_bitfrontiers		" + str(delta_t))
	return bit_frontiers

def define_wordfrontiers(signal, samples_per_bit):

	global debug, debug1

	t = time.time()

	window = round(samples_per_bit * 10)

	window_variance = variance(signal, window)


	split = max(window_variance) * 0.25

	word_map = (window_variance > split)
	word_frontiers_map = np.bitwise_xor(word_map[0:-2], word_map[1:-1])
	word_frontiers_map[0] = 1
	word_frontiers_map[-1] = 1

	nnz = np.count_nonzero(word_frontiers_map)

	word_frontiers = np.ndarray.nonzero(word_frontiers_map)

	if debug == True:
		#print(word_map)
		#print(word_frontiers_map)
		#print("Word Frontiers: " + str(word_frontiers[0]))
		#print(nnz)
		
		scale = 50
		wv_toplot = [x * scale for x in window_variance]
		pylab.plot(signal, 'b')
		pylab.plot(wv_toplot, 'r')
		print("Valor do split: " + str(split))
		plt.axhline(y = split*scale, color='black')

		pylab.show()

		input("Press space to continue")

	if debug1 == True:
		delta_t = time.time() -t
		print("define_wordfrontiers		" + str(delta_t))
	return word_frontiers, window_variance, split

def slice_signal(signal, word_boundaries, window_variance, variance_split):

	t = time.time()

	global debug, debug1

	sliced_signal = []

	#print("len indexes")
	#print(len(indexes[0])-1)

	packet_start_index = []
	for x in range(len(word_boundaries[0])-1):

		a = word_boundaries[0][x]
		b = word_boundaries[0][x+1]


		if window_variance[word_boundaries[0][x]+1] > variance_split:
			packet_start_index.append(sum(len(l) for l in sliced_signal))
			sliced_signal.append(signal[a:b])

	#print(packet_start_index)
	result = np.asarray(sliced_signal)

	#print("Sinal Fatiado ")
	#print(sliced_signal)
	#print(indexes)

	if debug1 == True:
		delta_t = time.time() -t
		print("slice_signal			" + str(delta_t))
	return result, packet_start_index

def interval_average(signal, indexes):

	t = time.time()

	global debug, debug1

	averages = np.zeros(max(len(indexes)-1, 0))

	#print(indexes)

	for x in range(len(averages)):
		tempbuffer = signal[indexes[x]:indexes[x+1]]
		averages[x] = np.mean(tempbuffer[round(len(tempbuffer)*0.3):round(len(tempbuffer)*0.9)])

		#averages[x] = np.mean(signal[indexes[x]:indexes[x+1]])


	if debug1 == True:
		delta_t = time.time() -t
		print("interval_averages		" + str(delta_t))
	return averages

def demodulator(iavs, threshold):

	t = time.time()

	global debug, debug1

	result = np.asarray(iavs, dtype=int)

	result[iavs > threshold] = 1
	result[iavs < threshold] = 0

	result.tolist()

	#if debug == True:
		#pylab.plot(iavs, 'red')
		#pylab.plot(threshold, 'black')
		#pylab.show()

	if debug1 == True:
		delta_t = time.time() - t
		print("demodulator			" + str(delta_t))
	return result
