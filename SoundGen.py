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
parser.add_argument('-sf','--sfram', help='Frame size, default is 32k', type=int, required=False, default = 320*1024)
parser.add_argument('-nf','--nfram', help='Number of frames to be collected before program ends, default is 1, must be 1 or greater', type=int, required=False, default = 1)
parser.add_argument('-it','--itnum', help='Number of iterations before program ends, default is 1, must be 1 or greater', type=int, required=False, default = 1)
parser.add_argument('-db','--dbug', help='DebugMode, default is False', required=False, type=bool, default = False)
parser.add_argument('-i','--infi', help='InfiniteMode, default is True', required=False, default = True)
parser.add_argument('-sym','--symb', help='Symbol Rate of expected ASK signal', type=int, required=True, default = 3650)
parser.add_argument('-cp', '--comp', help='Comparator (DEEP, PBZ, FAST). See docs for details', type=str, required=False, default='FAST')
args = vars(parser.parse_args())

#args['freq'] will contain the value of arg '-f'
#args['samp'] will contain the value of optional argument '-s' if any value was passed
#etc

print(args)

########################################################################
### DECLARING VARIABLES
########################################################################


# Initialize SDR kit
#SDR = RtlSdr()

# configure SDR device
#SDR.sample_rate = int(args['samp'])						#These are default values, will be overriden in any case of user input, 'SoundGen -h' for help
#SDR.center_freq = args['freq']
#SDR.gain = args['gain']

#Signal characteristics
Signal = classGen.Signal(args['samp'], args['sfram'], args['nfram'], args['symb'], 0.0152, 1, True)		# sample_rate, frame_size, frames_per_iteration, symbol_rate, silence_time, decimation_factor, simulator_mode

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

#GPIO.setwarnings(False)
#GPIO.setmode(GPIO.BOARD)
#GPIO.setup(3, GPIO.OUT)
#GPIO.setup(5, GPIO.OUT)
#GPIO.setup(7, GPIO.OUT)
#GPIO.setup(11, GPIO.OUT)
#GPIO.setup(13, GPIO.OUT)


## Debugging variables
allsamples = array.array('f',[0])


########################################################################
### FUNCTIONS
########################################################################



def threadInit():	#Initialize threads
	global t_collector
	#t_collector = threading.Thread(target=Signal.collect_data, name="Collector", args=[SDR])
	t_collector = threading.Thread(target=Signal.generate_data, name="Collector", args=[Packet])
	t_collector.start()


if __name__ == "__main__":

	while infinite_loop == True:
		t = time.time()

		threadInit()  # Initialize the data source required threads.

		Signal.demod_signal = []		# Flush the previous iteration's demodulation
		iteration_end = False       	# At the end of the main cycle's iteration this flag turns true if the desired number of iterations has been reached
		iteration_count = 0

		while Signal.samples_FIFO.empty == True:   # Wait until there is at least 1 item in the FIFO
			pass

		while t_collector.isAlive() or Signal.samples_FIFO.empty() == False:  	# Cycle until collector thread is alive OR FIFO isn't empty


			if Signal.samples_FIFO.empty() == False: # Are there any samples in the harvesting FIFO?

				this_frame = Signal.samples_FIFO.get_nowait()
				this_frame = this_frame[5:-1]
				this_frame =  filterGen.bp_butter(this_frame, [10, 3650], 2, Signal.sample_rate)	# Apply butterworth, 2nd order band pass filter. The filter order should be changed with care, a simulation can be run with the help of the "ZXC.py" script

				if Signal.decimation_factor > 1:
					 this_frame = signal.decimate(this_frame, decimation_factor)					# Decimate if decimation order > 1.   Signal != signal, Signal is a class native to this project, while signal is an imported function library from the 3rd party Scipy library

				#Fix this by removing the first sample earlier?
				#this_frame = this_frame[int(33500/decimation_factor):-1]							# Filtering the frame introduces artifacts in the first few samples, those samples are removed here in order to facilitate the comparator work.

				#demod_signal = DEEP_comparator.compare_signal(this_frame, Signal.samples_per_symbol) 								#Deep Demodulation

				st = time.time()
				if args['comp'] == 'FAST':
					Signal.demod_signal.extend(FAST_comparator.compare_signal(this_frame, Signal.samples_per_symbol, Packet))
				elif args['comp'] == 'PBZ':
					Signal.demod_signal.extend(PBZ_comparator.compare_signal(this_frame, Signal.samples_per_symbol))	# The comparator's output is concatenated to the array end_result
				else:
					Signal.demod_signal.extend(DEEP_comparator.compare_signal(this_frame, Signal.samples_per_symbol))
				delta_st = time.time() - st

				if debug == True:
					allsamples.extend(this_frame)           			# Keep storing samples for later dump if demod is activated



########################################################################
### INFORMATION PARSING
########################################################################

		message_result, sucesses, preamble_detections = parseGen.binary_parse(Signal.demod_signal, Packet.preamble , Packet.packet_size , Packet.payload_size)


########################################################################
### NETWORK INTEGRATION
########################################################################


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

		harvest_time = Signal.frame_size/Signal.sample_rate

		runtime = round(time.time() -t, 3)
		print("\n ==================  \n\nTemporal Window 	" + str(round(temporal_window, 3)) + "\nIterations: 		" +  str(iteration_counter) + "\nSamples processed: 	" + str(Signal.frame_size) + "\nPreambles detected: 	" + str(preamble_detections) + "\nSucesses: 		" + str(sucesses) +  "\nSuccess Rate: 		" +str(round(success_ratio,1)) + "\nRuntime: 		"  +  str(runtime)  + "\nPackets per second: 	"  +  str(round(sucesses / max(temporal_window,runtime), 2) ))
		print('Ideal harvest time:	' + str(round(harvest_time,3)))
		print('Comparator runtime:	' + str(round(delta_st, 3)))
		print('Deafness period:	' + str(round(harvest_time/delta_st, 3)))
		print('\n\nActive comparator is ' + args['comp'])
		print('Debug value is ' + str(debug))
		print('Loop value is ' + str(args['infi']))



########################################################################


		iteration_counter += 1
		if iteration_counter >= args['itnum']:
			infinite_loop = False

		infinite_loop = args['infi'] 			# -i argument takes precedente over -it argument, thus is updated later, in order to overwrite.

	sys.exit(main(sys.argv))
