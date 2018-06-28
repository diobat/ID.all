from pylab import *   	#Graphical capabilities
from rtlsdr import *	#SDR
import queue			#FIFO/queue
import threading		#Multi-threading
import time
import array
import sys
import pandas as pd
import pdata
import time
#import scipy.signal

########################################################################
### DECLARING VARIABLES
########################################################################


sdr = RtlSdr()

global frame_size

# configure SDR device
sdr.sample_rate = 226e3
sdr.center_freq = 90010000
sdr.gain = 12

frame_size = 16 * 1024 * 2# 32


#signal characteristics

decimation_factor = 1 									# It might be possible to increase efficiency by decimating the signal before it gets passed along to the pdata library, paceholder for now
signal_frequency = 3650 * decimation_factor				# Baseband frequency of the desired signal it should be no higher than one tenth of the SDR kit sampling rate
bits_per_word = 32										# How many bits of information will be arriving in burst in each recieved message

signal_period = 1/signal_frequency						
samples_per_bit = sdr.sample_rate * signal_period		# How many times each bit of information will be sampled by the SDR  kit as it arrives. Lower means faster code executing speeds, higher means lower error rate. Should never be lower than 2



n = 5
last_n_frames = zeros(frame_size * n)					# Important for plotting


desired_result = [1,0,1,0,0,0,1,0,0,0,1,0,1,1]			#This is the sequence of bits that the program will interpret as a "Success"
preamble = [0,0,0,0,1,0,1,0]							#This is the sequence of bits that the program will interpret as the start of a packet

buffer_size = 0  										# Size of the FIFO (in bits) where the samples are stored between harvesting and plotting, zero means infinite size
global sample_buffer
sample_buffer = queue.Queue(buffer_size)


## Flow control

global iteration_counter, stop_at
iteration_counter = 0									# Counts the number of frames collected so far
stop_at = 5												# How many frames of data the program will collect and process before it ends
debug = True											# Debug capabilities switch

## Debugging variables

allsamples = array.array('f',[0])


########################################################################
### FUNCTIONS
########################################################################

def main(args):
    return 0


def collectData(): 	#Collect samples

	global frame_size
	global iteration_counter, flag_end, stop_at
	
	t = time.time()
	while iteration_counter < stop_at:
		sample_buffer.put_nowait(abs(sdr.read_samples(frame_size)))  ## Harvests samples and stores their ABSOLUTE VALUES into a FIFO
		iteration_counter += 1
	print("\n###TERMINEI A RECOLHA DE AMOSTRAS EM " + str(round(time.time() -t, 3)) + ". TEMPO IDEAL = " +str(round((frame_size*stop_at)/sdr.sample_rate, 3)) + "###\n")
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
	
	t = time.time()
	
	#ion() # Turn on the interactive mode of PyLab, required in order to update the plots in real time
	threadInit()  # Initialize the required threads.
	#plotInit() # Initialize the frames, axes, lines and other visual stuff
	
	end_result = []
	t_collector.start()
	flag_end = False
	
	while flag_end == False or sample_buffer.empty() == False:
		
		
		if sample_buffer.empty() == False: # Are there any samples in the harvesting FIFO?
			  
			this_frame = sample_buffer.get_nowait()								
			
			demod_signal = pdata.process_data(this_frame, samples_per_bit, frame_size) 	# O sinal cru é desmodulado (ASK) através das funções da biblioteca pdata
			#print(demod_signal)
			end_result.extend(demod_signal)												# O resultado obtido da desmodulação é anexado ao fim do array end_result
			
			
			if debug == True:
				allsamples.extend(this_frame)
	
	flipped_endresult = [1 - x for x in end_result]
	
	sucesses = 0
	flipped_sucesses = 0
	preamble_detections = 0
	
	for x in range(len(end_result) - len(desired_result)):	
		if end_result[x:x+len(desired_result)] == desired_result:
			sucesses += 1
			
	for x in range(len(flipped_endresult) - len(desired_result)):	
		if flipped_endresult[x:x+len(desired_result)] == desired_result:
			flipped_sucesses += 1
			
	for x in range(len(end_result) - len(preamble)):	
		if end_result[x:x+len(preamble)] == preamble:
			preamble_detections += 1
	
	print(end_result)
	
	t_collector.join()
	#time.sleep(1)
	print("\nFINISHED   \n\nActive threads: " + str(threading.activeCount()) + "\nIterations: " +  str(iteration_counter) + "\nSamples processed: " + str(frame_size*stop_at) + "\nPreambles detected: " + str(preamble_detections) + "\nSucesses: " + str(sucesses) + "\nFlipped Sucesses: " + str(flipped_sucesses) + "\nRuntime: "  +  str(round(time.time() -t, 3)) )	
	
	if debug == True:
		save('outfile_samples', allsamples) 
		save('outfile_signal', end_result)
		save('outfile_SPB', samples_per_bit)
		
	sys.exit(main(sys.argv))

