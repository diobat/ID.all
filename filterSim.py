from scipy import signal
import matplotlib.pyplot as plt
import numpy as np


samples = np.load("outfile_samples.npy")

sample_rate = 226000
symbol_rate = 3650

nyq_freq = sample_rate/2

filter_order = 2
low_cutoff = 15
high_cutoff = 3600


w1 = low_cutoff / nyq_freq          # For digital filters, Wn is normalized from 0 to 1, where 1 is the Nyquist frequency, pi radians/sample.
w2 = high_cutoff / nyq_freq         # (Wn is thus in half-cycles / sample.)

ratio = 10

b, a = signal.butter(filter_order, [w1, w2] , 'bandpass')
w, h = signal.freqz(b, a)


fig = plt.figure()


ax1 = fig.add_subplot(211)

plt.axvline(low_cutoff, color='green') # cutoff frequency
plt.axvline(high_cutoff, color='green') # cutoff frequency
plt.xlim([0, high_cutoff*ratio])
plt.psd(samples, NFFT=1024, Fs=sample_rate, Fc=0)




ax2 = fig.add_subplot(212)
plt.title('Digital filter frequency response')
plt.plot(w*nyq_freq, h, 'k')
plt.ylabel('Amplitude', color='k')
plt.xlabel('Frequency Hz')

plt.xlim([0, high_cutoff*ratio])
plt.axvline(low_cutoff, color='green')      # cutoff frequency
plt.axvline(high_cutoff, color='green')     # cutoff frequency

#ax2 = ax1.twinx()
#angles = np.unwrap(np.angle(h))
#plt.plot(w, angles, 'g')
#plt.ylabel('Angle (radians)', color='g')
plt.grid()
#plt.axis('tight')
plt.show()
