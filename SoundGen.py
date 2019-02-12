### Made by Diogo Batista (diogobatista@ua.pt) as part of my Integrated Master's thesis

#### If any issues arise, try :

	# First time setup? Issues with SDR kit compatibility? Check:  https://gist.github.com/floehopper/99a0c8931f9d779b0998

	# Issues with numpy module? On terminal: pip3 install --upgrade --ignore-installed --install-option '--install-data=/usr/local' numpy

from pylab import *   	#Graphical capabilities, network and debug outfiles

#from rtlsdr import *	#SDR
from scipy import signal #Signal Filtering
import queue			#FIFO/queue
import threading		#Multi-threading
#import RPi.GPIO as GPIO	#LED's
import array
import sys
import DEEP_comparator, PBZ_comparator, FAST_comparator, filterGen, parseGen, fileGen, classGen		#demodulating library
import PBZS_comparator
#import gpioGen
import time				#time deltas
import argparse			#argumment management
#import scipy.signal


########################################################################
### PARSING INPUT ARGUMENTS
########################################################################

parser = argparse.ArgumentParser(prog = 'SoundGen', description='Made by Diogo Batista, diogobatista@ua.pt', epilog=' ',)

parser.add_argument('-f','--freq', help='Center Frequency',type=int, required=True)
parser.add_argument('-s','--samp', help='Sampling rate, default is 226kHz', type=int, required=False, default = 226000)
parser.add_argument('-g','--gain', help='Gain, [0 50], default is 15', type=int,required=False, default = 15)
parser.add_argument('-sf','--sfram', help='Frame size, default is 32k. An error will occurr it isnt set to a multiple of 512', type=int, required=False, default = 320*1024)#320*1024)
parser.add_argument('-ff','--fifo', help='FIFO size, default is 5, must be 5 or greater', type=int, required=False, default = 10)
parser.add_argument('-dc','--dcim', help='Decimation order.', type=int, required=False, default = 1)
parser.add_argument('-it','--itnum', help='Number of iterations before program ends, default is 1, must be 1 or greater', type=int, required=False, default = 1)
parser.add_argument('-db','--dbug', help='DebugMode, default is False', required=False, type=bool, default = False)
parser.add_argument('-i','--infi', help='InfiniteMode, default is True', required=False, default = True)
parser.add_argument('-sym','--symb', help='Symbol Rate of expected ASK signal', type=int, required=True, default = 3650)
parser.add_argument('-gen','--genr', help='Generate signal internally using a simulator', type=bool, required=False, default = False)
parser.add_argument('-cp', '--comp', help='Comparator (DEEP, PBZ, FAST). See docs for details', type=str, required=False, default='FAST')
args = vars(parser.parse_args())

#args['freq'] will contain the value of arg '-f'
#args['samp'] will contain the value of optional argument '-s' if any value was passed, otherwise revert to default
#etc

print(args)

########################################################################
### DECLARING VARIABLES
########################################################################


#Signal characteristics
Signal = classGen.Signal(args['genr'], args['freq'], args['samp'], args['gain'], args['sfram'], args['fifo'], args['symb'], 0.0152, args['dcims'])		# carrier_freq, sample_rate, software gain, frame_size, frames_per_iteration, symbol_rate, silence_time, decimation_factor, simulator_mode

#Packet characteristics
Packet = classGen.Packet([1,0,1,0], 8, [1,0,1,0], [1])				# preamble, payload_size, CRC_divisor, STOP bits

## Flow control
global iteration_counter, debug
iteration_counter = 0									# Counts the number of frames collected so far
infinite_loop = True									# Flag that controls wether the program will leave the main loop
debug = args['dbug']									# Debug capabilities switch

## Led Setup
USE_LEDS = False
heartbeat = True




## Debugging variables
allsamples = array.array('f',[0])


########################################################################
### FUNCTIONS
########################################################################


def parityOf(int_type): # Check parity

	x = 0
	for bit in int_type:
		x = (x << 1) | bit

	parity = False
	while (x):
		parity = ~parity
		x = x & (x - 1)
	return(parity)


def threadInit():	#Initialize threads
	global t_collector
	t_collector = threading.Thread(target=Signal.collect_data, name="Collector", args=[Packet])
	if t_collector.isAlive() == False:
		t_collector.start()
		#print('True Thread init')


if __name__ == "__main__":


	delta_st = int(1)
	threadInit()
	threadInit()


	while infinite_loop == True:
		t = time.time()


		if not Signal.samples_FIFO.full():
			#print(str(Signal.samples_FIFO.qsize()) +' < '+ str(Signal.FIFO_size))
			#print('Thread init')
			threadInit()  				# Initialize the data source required threads.


		Signal.demod_signal = []		# Flush the previous iteration's demodulation
		iteration_end = False       	# At the end of the main cycle's iteration this flag turns true if the desired number of iterations has been reached
		iteration_count = 0

		while Signal.samples_FIFO.empty():
			#print(Signal.samples_FIFO.empty)
			pass


		#print('pré if : ' + str(Signal.samples_FIFO.qsize()))
		#if not Signal.samples_FIFO.empty():   # Prevent fetching from a potentially empty FIFO

		this_frame1 = Signal.samples_FIFO.get(True, 0.1)
		Signal.samples_FIFO.task_done()
		#this_frame = this_frame1[2000:-1]

		#offset = min(this_frame1[5000:])
		#this_frame1 = [(x-offset) for x in this_frame1]

		this_frame =  filterGen.bp_butter(this_frame1, [1, 3650], 2, Signal.sample_rate_adj)	# Apply butterworth, 2nd order band pass filter. The filter order should be changed with care, a simulation can be run with the help of the "filterSim.py" script

		this_frame = this_frame[45000:]



		if Signal.decimation_factor > 1:
			 this_frame = signal.decimate(this_frame, Signal.decimation_factor)					# Decimate if decimation order > 1.   Signal != signal, Signal is a class native to this project, while signal is an imported function library from the 3rd party Scipy library

		#Fix this by removing the first sample earlier?
								# Filtering the frame introduces artifacts in the first few samples, those samples are removed here in order to facilitate the comparator work.

		#demod_signal = DEEP_comparator.compare_signal(this_frame, Signal.samples_per_symbol) 								#Deep Demodulation

		st = time.time()
		if args['comp'] == 'FAST':
			Signal.demod_signal.extend(FAST_comparator.compare_signal(this_frame, Signal.samples_per_symbol, Packet))
		elif args['comp'] == 'PBZ':
			Signal.demod_signal.extend(PBZ_comparator.compare_signal(this_frame, Signal.samples_per_symbol))	# The comparator's output is concatenated to the array end_result
		elif args['comp'] == 'PBZS':
			Signal.demod_signal.extend(PBZS_comparator.compare_signal(this_frame, Signal.samples_per_symbol, Packet.packet_size, Signal.silence_samples))
		else:
			Signal.demod_signal.extend(DEEP_comparator.compare_signal(this_frame, Signal.samples_per_symbol))
		delta_st = time.time() - st

		if debug == True:
			allsamples.extend(this_frame)           			# Keep storing samples for later dump if demod is activated

                if debug == True:
                    allsamples.extend(this_frame)           # Keep storing samples for later dump if demod is activated


########################################################################
### INFORMATION PARSING
########################################################################


		message_result, sucesses, preamble_detections = parseGen.binary_parse(Signal.demod_signal, Packet.preamble , Packet.packet_size , Packet.payload_size, Packet.STOP_bits)


		# Count the number of sucesses

        for x in range(len(end_result) - len(desired_result)):
            if end_result[x:x+len(desired_result)] == desired_result:
                sucesses += 1

        for x in range(len(flipped_endresult) - len(desired_result)):
            if flipped_endresult[x:x+len(desired_result)] == desired_result:
                flipped_sucesses += 1


		fileGen.save_payload(message_result, debug, allsamples, Signal.demod_signal, Signal.samples_per_symbol)


########################################################################
### RPI GPIO UPDATING
########################################################################


		temporal_window = (1/Signal.sample_rate)*Signal.frame_size
		Signal.silence_time = 0.0152									# Time in seconds between start of consecutive packets,


		success_ratio = sucesses / (temporal_window/Signal.silence_time)

		#if USE_LEDS == True:

			#gpioGen.update(success_ratio)


########################################################################
### VERBOSE
########################################################################

		ideal_harvest_time = Signal.frame_size/Signal.sample_rate

		runtime = round(time.time() -t, 3)
		print("\n ==================  \n\nTemporal Window 	" + str(round(temporal_window, 3)) + "\nIterations: 		" +  str(iteration_counter) + "\nSamples processed: 	" + str(Signal.frame_size) + "\nPreambles detected: 	" + str(preamble_detections) + "\nSucesses: 		" + str(sucesses) +  "\nTotal Runtime: 		"  +  str(runtime)  + "\nPackets per second: 	"  +  str(round(sucesses / max(temporal_window,runtime), 2) ))
		print('Ideal harvest time:	' + str(round(ideal_harvest_time,3)))
		print('Real harvest time:	' + str(round(Signal.harvest_delta,3)))
		print('Comparator runtime:	' + str(round(delta_st, 3)))
		print('Deafness period:	' + str(round(max(1-(ideal_harvest_time/delta_st),0), 3)))
		print('\n\nActive comparator is ' + args['comp'])
		print('Debug value is ' + str(debug))
		print('Loop value is ' + str(args['infi']))


########################################################################




    sys.exit(main(sys.argv))
