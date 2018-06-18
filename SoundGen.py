from pylab import *   	#Graphical capabilities
from rtlsdr import *	#SDR
import queue			#FIFO/queue
import threading		#Multi-threading
import time
import array
import sys
import pandas as pd
import pdata

########################################################################
### DECLARING VARIABLES
########################################################################


sdr = RtlSdr()


# configure SDR device
sdr.sample_rate = 226e3
sdr.center_freq = 90009978
sdr.gain = 20
global frame_size
frame_size = 16 * 1024 # 32


#signal characteristics

signal_frequency = 3650
bits_per_word = 32

signal_period = 1/signal_frequency
samples_per_bit = sdr.sample_rate * signal_period



buffer_size = 0  # Size of the FIFO (in bits) where the samples are stored between harvesting and plotting, zero means infinite size
n = 5
last_n_frames = zeros(frame_size * n)


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
debug = True

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
	global iteration_counter


	while iteration_counter < 5:
		sample_buffer.put_nowait(abs(sdr.read_samples(frame_size)))  ## Harvests samples and stores their ABSOLUTE VALUES into a FIFO
		iteration_counter += 1
		
	
	
def threadInit():
	global t_collector, t_plotter
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
	plotInit() # Initialize the frames, axes, lines and other visual stuff
	
	
	t_collector.start()

	
	while iteration_counter < 5:
		abs_samples = abs(samples)
		
		
		if sample_buffer.empty() == False: # Are there any samples in the harvesting FIFO?
			
			last_n_frames[0:-1*(frame_size+1)] = last_n_frames[frame_size:-1]  	# Python supports negative indexing, which means '-1' corresponds to the last element of the array
			this_frame = sample_buffer.get_nowait()								# '-2' to the second last, etc 
			last_n_frames[-1*(frame_size+1):-1] = this_frame			
					
			
			if debug == True:
				allsamples.extend(this_frame)
				
			
		#line1.set_ydata(last_n_frames)
		#fig.canvas.draw()
		#fig.canvas.flush_events()
		
	
	t_collector.join()
	#time.sleep(1)
	print("FINISHED   \nActive threads: " + str(threading.activeCount()) + "\nIterations: " +  str(iteration_counter) + "\nSamples processed: " + str(len(allsamples)))	
	
	if debug == True:
		save('outfile', allsamples) 
	
		
	sys.exit(main(sys.argv))

