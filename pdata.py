import pylab
import numpy as np
#import pandas as pd
import time
import matplotlib.pyplot as plt



global debug, debug1, debug2

debug = True 	# Should execution be halted at every step to generate graphs?
debug1 = False 	# Should step by step timestamps be printed?
debug2 = False	# Should a global timestamp be printed?

def process_data(signal, samples_per_bit, samples_per_frame):

	t = time.time()

	global debug, debug1, debug2

	SPF = samples_per_frame

	word_frontiers = define_wordfrontiers(signal, samples_per_bit)

	sliced_signal = slice_signal(signal, word_frontiers)

	envelope = []
	envelope = enveloper(signal, SPF)
	#threshold = abs(envelope[1] - envelope[0]) * 0.50 + envelope[1]
	threshold = np.mean(envelope)
	result = []

	allbit_frontier = []
	alliavs = []
	extended_alliavs = []
	alldemodulated_signal = []
	counter = 0

	for x in range(len(sliced_signal)):


		bit_frontier = define_bitfrontiers(sliced_signal[x], samples_per_bit, threshold)
		iavs = interval_average(sliced_signal[x], bit_frontier)
		demodulated_signal = demodulator(iavs, threshold)

		result.extend(demodulated_signal)

		if debug == True:
			allbit_frontier.extend([x+counter for x in bit_frontier])
			alliavs.extend(iavs)

			counter += len(sliced_signal[x])

	for x in range(len(alliavs)):
		a = [alliavs[x]] * round(samples_per_bit)
		extended_alliavs.extend(a)

	if debug == True:
		pylab.plot(signal, 'b')
		#pylab.plot(extended_alliavs, 'red')

		#for xv in word_frontiers[0]:
			#plt.axvline(x=xv, color='red')

		for xc in allbit_frontier:
			plt.axvline(x=xc)

		plt.axhline(y=threshold, color ='k')



		pylab.show()
		input("Press space to continue")

	if debug1 == True or debug2 == True:
		delta_t = time.time() -t
		print("TOTAL TIME				" + str(delta_t))
		#input("Enter to proceed")
	return result


def variance(args,window):

	t = time.time()

	global debug, debug1

	result = []
	window = int(window)
	y = range(int(len(args)-window-1))
	step = 50
	step2 = 0

	#for x in range(int(len(args)-window-1)):
	for x in y[0:-1:step]:
		result.extend([np.var(args[x:x+window:step2])] * step)

	result1 = [result[0]] * int(np.floor(window/2))
	result2 = [result[-1]] * int(np.floor(window/2))


	result1.extend(result)
	result1.extend(result2)

	if debug1 == True:
		delta_t = time.time() -t
		print("variance			" + str(delta_t))
	return result1




def enveloper(signal, SPF):

	t = time.time()

	global debug, debug1

	#last_n_frames[0:len(last_n_frames - SPF)] = last_n_frames[SPF:end]
	#last_n_frames[-SPF:end] = signal
	#I = np.nonzero(last_n_frames)
	#first_non_zero = I[0][0]


	yupper = np.percentile(signal, 97)
	ylower = np.percentile(signal, 3)

	envelope = [yupper, ylower]

	if debug1 == True:
		delta_t = time.time() -t
		print("enveloper			" + str(delta_t))
	return envelope

def define_bitfrontiers(signal, samples_per_bit, threshold):

	t = time.time()

	global debug, debug1

	rounded_samples = int(np.ceil(samples_per_bit))
	quality = np.zeros(rounded_samples)
	number_of_bits = int(np.floor((len(signal)/samples_per_bit)))
	range_number_of_bits = range(number_of_bits - 1)
	step = 2
	#step = int(samples_per_bit/32)

	for i in range(rounded_samples):

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


	if debug1 == True:
		delta_t = time.time() -t
		print("define_bitfrontiers		" + str(delta_t))
	return bit_frontiers


def define_wordfrontiers(signal, samples_per_bit):

	global debug, debug1

	t = time.time()

	window = round(samples_per_bit * 10)

	window_variance = variance(signal, window)


	stretched_variance = np.array(window_variance)*10

	split = max(window_variance) * 0.5
	#split = np.percentile(window_variance, 0.4)
	word_map = (window_variance > split)
	word_frontiers_map = np.bitwise_xor(word_map[0:-2], word_map[1:-1])
	word_frontiers_map[0] = 1
	word_frontiers_map[-1] = 1




	nnz = np.count_nonzero(word_frontiers_map)


	word_frontiers = np.ndarray.nonzero(word_frontiers_map)



	if debug == True:
		print(word_map)
		print(word_frontiers_map)
		print("Word Frontiers: " + str(word_frontiers[0]))
		print(nnz)

		pylab.plot(signal, 'b')
		pylab.plot(window_variance, 'r')
		print("Valor do split: " + str(split))
		plt.axhline(y = split, color='black')

		pylab.show()

		input("carrega para seguir")

	if debug1 == True:
		delta_t = time.time() -t
		print("define_wordfrontiers		" + str(delta_t))
	return word_frontiers

def slice_signal(signal, indexes):

	t = time.time()

	global debug, debug1

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

	if debug1 == True:
		delta_t = time.time() -t
		print("slice_signal			" + str(delta_t))
	return result

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



#if __name__ == '__main__':
#    import sys
#    sys.exit(main(sys.argv))
