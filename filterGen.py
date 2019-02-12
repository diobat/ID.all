########################################################################
### FILTER CHARACTERIZATION
########################################################################

from scipy import signal #Signal Filtering


def bp_butter(s, cutoffs , filter_order, sampling_rate):

	[cutoff_low, cutoff_high] = cutoffs

	nyq = 0.5 * sampling_rate

	wn2 = (cutoff_high)  / (nyq)   					#HIGH Cutoff frequency for band pass filter, in half-radians per sample
	wn1 = (cutoff_low)  / (nyq)			#LOW Cutoff frequency for band pass filter, in half-radians per sample

	zb1,za1 = signal.butter(filter_order, [wn1, wn2] , 'bandpass')			## band pass filter

	filtered_signal = abs(signal.lfilter(zb1, za1, s))

	return filtered_signal
