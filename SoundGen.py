from pylab import *   	#Graphical capabilities
from rtlsdr import *	#SDR
import queue			#FIFO/queue
import threading		#Multi-threading
import time
import array
import sys
import pandas as pd
import pdata
#import scipy.signal

########################################################################
### DECLARING VARIABLES
########################################################################


sdr = RtlSdr()


# configure SDR device
sdr.sample_rate = 226e3
sdr.center_freq = 90010031
sdr.gain = 20
global frame_size
frame_size = 16 * 1024 # 32


#signal characteristics

decimation_factor = 1
signal_frequency = 3650 * decimation_factor
bits_per_word = 32

signal_period = 1/signal_frequency
samples_per_bit = sdr.sample_rate * signal_period



buffer_size = 0  # Size of the FIFO (in bits) where the samples are stored between harvesting and plotting, zero means infinite size
n = 5
last_n_frames = zeros(frame_size * n)

desired_result = [1,1,0,1,0,0,0,1,0,0,0,1,0,1,0,0,1,1,0,0,0,1,1,1,0,0,0,0,1,1,1,1]

global sample_buffer
sample_buffer = queue.Queue(buffer_size)


global data_ready
data_ready = 0

global samples
samples = zeros(frame_size)



global fig1
global ax1


## Flow control

global iteration_counter
iteration_counter = 0
debug = False

## Debugging variables

allsamples = array.array('f',[0])


########################################################################
### DEFINING OBJECTS
########################################################################

def main(args):
    return 0


def collectData(): 	#Collect samples

	global samples
	global frame_size
	global data_ready
	global iteration_counter, flag_end

	while iteration_counter < 25:
		sample_buffer.put_nowait(abs(sdr.read_samples(frame_size)))  ## Harvests samples and stores their ABSOLUTE VALUES into a FIFO
		#sample_buffer.put_nowait(scipy.signal.decimate(abs(sdr.read_samples(frame_size))), 10)  ## Harvests samples and stores their ABSOLUTE VALUES into a FIFO
		iteration_counter += 1
	print("##############TERMINEI A RECOLHA DE AMOSTRAS##############")
	flag_end = True
	
		
	
	
def threadInit():
	global t_collector, t_plotter, flag_end
	t_collector = threading.Thread(target=collectData, name="Collector", args=[])
	#print(str(threading.active_count()))
	#t_plotter = threading.Thread(target=plotData, name="Plotter", args=[])
	
def plotInit(): 
	
	global fig
	global ax
	global line1
	global samples
	global frame_size

	x = range(len(last_n_frames))
	
	fig = figure()
	ax = fig.add_subplot(1,1,1)
	line1, = ax.plot(x, last_n_frames, 'r')
	ax.set_xlim(0, len(last_n_frames))
	ax.set_ylim(0, 0.5)
	


if __name__ == "__main__":
	
	ion() # Turn on the interactive mode of PyLab, required in order to update the plots in real time
	threadInit()  # Initialize the required threads.
	#plotInit() # Initialize the frames, axes, lines and other visual stuff
	
	end_result = []
	t_collector.start()
	flag_end = False
	
	while flag_end == False or sample_buffer.empty() == False:
		
		
		if sample_buffer.empty() == False: # Are there any samples in the harvesting FIFO?
			  
			this_frame = sample_buffer.get_nowait()								
			
			demod_signal = pdata.process_data(this_frame, samples_per_bit, frame_size)
			print(demod_signal)
			end_result.extend(demod_signal)
			
			
			if debug == True:
				allsamples.extend(this_frame)
	
	sucesses = 0
	
	for x in range(len(end_result) - len(desired_result)):	
		if end_result[x:x+len(desired_result)] == desired_result:
			sucesses += 1
			

	
	t_collector.join()
	#time.sleep(1)
	print("FINISHED   \nActive threads: " + str(threading.activeCount()) + "\nIterations: " +  str(iteration_counter) + "\nSamples processed: " + str(len(allsamples)) + "\nSucesses: " + str(sucesses))	
	
	if debug == True:
		save('outfile', allsamples) 
	
		
	sys.exit(main(sys.argv))

