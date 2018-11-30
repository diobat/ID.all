# This comparator was designed to work for a packet preamble of exactly [1,1,1,0], it was not tested under any other cases.


import numpy as np
import matplotlib.pyplot as plt
import time



def compare_signal(signal, samples_per_bit, Packet):

	t = time.time()

	SPB = int(samples_per_bit)
	ratio = 0.3
	threshold =  max(signal)*ratio

	index = -1
	end_result = [0] * int(len(signal)/SPB)

	packet_size_samples = Packet.packet_size * SPB
	cooldown_margin = int(packet_size_samples * 1.2)
	cooldown = -1 * packet_size_samples


	signal_zero_centered = [(x - threshold) for x in signal]
	signal_zero_centered = signal_zero_centered[0:-packet_size_samples]

	transitions = np.where(np.diff(np.signbit(signal_zero_centered)))[0]

	RPrP = []       #Relative preamble harvest positions
	RPaP = []       #Relative packet harvest positions

	y = int(SPB/2)
	for w in range(Packet.preamble_len):
		RPrP.append((w*SPB)+y)

	for w in range(Packet.packet_size):
		RPaP.append((w*SPB)+y)

	real_transitions = []
	#print(SPB)
	#print(RPaP)

	for x in transitions:
		if x - cooldown > cooldown_margin:
			real_transitions.append(x)
			preamble_match = []
			for i in range(len(RPrP)):
				preamble_match.append(binary_threshold(signal[x + RPrP[i]],threshold))
			if preamble_match == Packet.preamble :
				for i in range(len(RPaP)):
					position = x + RPaP[i]
					position2 = int(position/SPB)
					end_result[position2] = binary_threshold(signal[position], threshold)
				cooldown = x

	plt.plot(signal)

	POC = []  # Points of collection
	for y in real_transitions:
		for u in RPaP:
			POC.append(y+u)


	t_threshold = [threshold] * len(real_transitions)
	t2_signal = [(signal[x]) for x in POC]

	plt.scatter(real_transitions, t_threshold, color='black')
	plt.scatter(POC, t2_signal, color='orange')

	plt.axhline(y= threshold, color='k')
	plt.show()



	return end_result


def binary_threshold(value, threshold):
	if value>threshold:
		return 1
	else:
		return 0
