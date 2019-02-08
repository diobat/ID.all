### Made by Diogo Batista (diogobatista@ua.pt) as part of my Integrated Master's thesis

#### If any issues arise, try :

	# First time setup? Issues with SDR kit compatibility? Check:  https://gist.github.com/floehopper/99a0c8931f9d779b0998

	# Issues with numpy module? On terminal: pip3 install --upgrade --ignore-installed --install-option '--install-data=/usr/local' numpy

from pylab import *   	#Graphical capabilities, network and debug outfiles
<<<<<<< HEAD
from rtlsdr import *	#SDR
import queue			#FIFO/queue
import threading		#Multi-threading
import datetime			#timestamps for the outfiles
import os				#file management
import array
import sys
import pdata			#demodulating library
import time				#timestamps
import RPi.GPIO as GPIO	#LED's
=======
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
>>>>>>> Testing
import argparse			#argumment management
#import scipy.signal


########################################################################
### PARSING INPUT ARGUMENTS
########################################################################

parser = argparse.ArgumentParser(prog = 'SoundGen', description='Made by Diogo Batista, diogobatista@ua.pt', epilog=' ',)

parser.add_argument('-f','--freq', help='Center Frequency',type=int, required=True)
parser.add_argument('-s','--samp', help='Sampling rate, default is 226kHz', type=int, required=False, default = 226000)
parser.add_argument('-g','--gain', help='Gain, [0 50], default is 15', type=int,required=False, default = 15)
<<<<<<< HEAD
parser.add_argument('-sf','--sfram', help='Frame size, default is 32k', type=int, required=False, default = 32*1024)
parser.add_argument('-nf','--nfram', help='Number of frames to be collected before program ends, default is 1, must be 1 or greater', type=int, required=False, default = 1)
=======
parser.add_argument('-sf','--sfram', help='Frame size, default is 32k. An error will occurr it isnt set to a multiple of 512', type=int, required=False, default = 320*1024)#320*1024)
parser.add_argument('-ff','--fifo', help='FIFO size, default is 5, must be 5 or greater', type=int, required=False, default = 10)
parser.add_argument('-dc','--dcim', help='Decimation order.', type=int, required=False, default = 1)
>>>>>>> Testing
parser.add_argument('-it','--itnum', help='Number of iterations before program ends, default is 1, must be 1 or greater', type=int, required=False, default = 1)
parser.add_argument('-db','--dbug', help='DebugMode, default is False', required=False, type=bool, default = False)
parser.add_argument('-i','--infi', help='InfiniteMode, default is True', required=False, default = True)
parser.add_argument('-sym','--symb', help='Symbol Rate of expected ASK signal', type=int, required=True, default = 3650)
parser.add_argument('-gen','--genr', help='Generate signal internally using a simulator', type=bool, required=False, default = False)
parser.add_argument('-cp', '--comp', help='Comparator (DEEP, PBZ, FAST). See docs for details', type=str, required=False, default='FAST')
args = vars(parser.parse_args())

#args['freq'] will contain the value of arg '-f'
#args['samp'] will contain the value of optional argument '-s' if any value was passed
#etc

print(args)

########################################################################
### DECLARING VARIABLES
########################################################################


<<<<<<< HEAD
# Initialize SDR kit
sdr = RtlSdr()

# configure SDR device
sdr.sample_rate = int(args['samp'])						#These are default values, will be overriden in any case of user input, 'SoundGen -h' for help
sdr.center_freq = args['freq']
#sdr.gain = 'auto'
sdr.gain = args['gain']


global frame_size
frame_size = args['sfram']


#signal characteristics

decimation_factor = 1 									# It might be possible to increase efficiency by decimating the signal before it gets passed along to the pdata library, paceholder for now
signal_frequency = args['symb'] * decimation_factor				# Baseband frequency of the desired signal it should be no higher than one tenth of the SDR kit sampling rate

bits_per_word = 32										# How many bits of information will be arriving in burst in each recieved message

signal_period = 1/signal_frequency
samples_per_bit = sdr.sample_rate * signal_period		# How many times each bit of information will be sampled by the SDR kit as it arrives. Lower means faster code executing speeds, higher means lower error rate. Should never be lower than 2

n = 2
last_n_frames = zeros(frame_size * n)					# Important for plotting

desired_result = [1,0,1,0,0,0,1,0,0,0,1,0,1,1]			# This is the sequence of bits that the program will interpret as a "Success"
preamble = [1,0,1,0]									# This is the sequence of bits that the program will interpret as the start of a packet

info_size = 8											# The information part of the packet consists of 2 hexadecimal chars, 8 bits
packet_size = len(preamble) + info_size + 2				# Parity + 2 hexa chars + parity bit + stop bit

message_result = []										# Reserving space for the message to be extracted from received frames
oufile_number = 0										#

buffer_size = 0  										# Size of the FIFO (in bits) where the samples are stored between harvesting and plotting, zero means infinite size
global sample_FIFO
sample_FIFO = queue.Queue(buffer_size)
=======
#Signal characteristics
Signal = classGen.Signal(args['genr'], args['freq'], args['samp'], args['gain'], args['sfram'], args['fifo'], args['symb'], 0.0152, args['dcims'])		# carrier_freq, sample_rate, software gain, frame_size, frames_per_iteration, symbol_rate, silence_time, decimation_factor, simulator_mode
>>>>>>> Testing

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
max_packages = stop_at * 10;

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


def parityOf(int_type): # Check parity

	x = 0
	for bit in int_type:
		x = (x << 1) | bit

	parity = False
	while (x):
		parity = ~parity
		x = x & (x - 1)
	return(parity)


<<<<<<< HEAD
def collectData(): 	#Collect samples

    global frame_size
    global stop_at
    frame_counter = 0
    t = time.time()
    while frame_counter < stop_at :
        sample_FIFO.put_nowait(abs(sdr.read_samples(frame_size))**2)  ## Harvests samples and stores their ABSOLUTE VALUES into a FIFO
        #print("\n###   TERMINEI A RECOLHA DE AMOSTRAS EM " + str(round(time.time() -t, 2)) + ". TEMPO IDEAL = " +str(round((frame_size*stop_at)/sdr.sample_rate, 2)) + "   ###\n")
        frame_counter += 1


=======
>>>>>>> Testing
def threadInit():	#Initialize threads
	global t_collector
	t_collector = threading.Thread(target=Signal.collect_data, name="Collector", args=[Packet])
	if t_collector.isAlive() == False:
		t_collector.start()
		#print('True Thread init')


if __name__ == "__main__":

<<<<<<< HEAD
    while infinite_loop == True:
        t = time.time()

        threadInit()  # Initialize the required threads.

        t_collector.start()

        end_result = []
        iteration_end = False        # At the end of the main cycle's iteration this flag turns true if the desired number of iterations has been reached
        iteration_count = 0

        while sample_FIFO.empty == True:   # Wait until there is at least 1 item in the FIFO
            pass

        while t_collector.isAlive() or sample_FIFO.empty() == False:  # Cycle until collector thread is alive OR FIFO isn't empty


            if sample_FIFO.empty() == False: # Are there any samples in the harvesting FIFO?

                this_frame = sample_FIFO.get_nowait()

                demod_signal = pdata.process_data(this_frame, samples_per_bit, frame_size) 	# Demodulation

                end_result.extend(demod_signal)												# O resultado obtido da desmodulação é anexado ao fim do array end_result

=======

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
>>>>>>> Testing

                if debug == True:
                    allsamples.extend(this_frame)           # Keep storing samples for later dump if demod is activated

        flipped_endresult = [1 - x for x in end_result]

########################################################################
### INFORMATION PARSING
########################################################################

<<<<<<< HEAD
        sucesses = 0
        flipped_sucesses = 0
        preamble_detections = 0
        message_result = []
=======
		message_result, sucesses, preamble_detections = parseGen.binary_parse(Signal.demod_signal, Packet.preamble , Packet.packet_size , Packet.payload_size, Packet.STOP_bits)
>>>>>>> Testing

		# Count the number of sucesses

        for x in range(len(end_result) - len(desired_result)):
            if end_result[x:x+len(desired_result)] == desired_result:
                sucesses += 1

        for x in range(len(flipped_endresult) - len(desired_result)):
            if flipped_endresult[x:x+len(desired_result)] == desired_result:
                flipped_sucesses += 1

<<<<<<< HEAD


        for x in range(len(end_result) - len(preamble)):				# Detects preambles
            if end_result[x:x+len(preamble)] == preamble:
                preamble_detections += 1                                # Counts them
                if parityOf(end_result[x:x+packet_size-1]):             # Checks for parity in the whole packet
                    message_result.append(end_result[x+len(preamble):x+len(preamble)+info_size])        #if validaded adds to the output batch


        output_list = os.listdir("./outputs")

        if len(output_list) >= 5:
            os.remove('./outputs/' + min(output_list))	#If there are 5 files or more in the outputs folder, delete the oldest file. Filenames are timestamps so its easy to find the oldest one.

        save('./outputs/' + str(datetime.datetime.now()), message_result)

        if USE_LEDS == True:
=======
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
>>>>>>> Testing

            max_sucesses = max(sucesses, flipped_sucesses)
            success_ratio = max_sucesses/max_packages

<<<<<<< HEAD
            heartbeat = not heartbeat
            GPIO.output(13, heartbeat)



            if success_ratio >= 0 and success_ratio < 0.25:

                GPIO.output(3, False)
                GPIO.output(5, False)
                GPIO.output(7, False)
                GPIO.output(11, False)

            elif success_ratio >= 0.25 and success_ratio < 0.5:

                GPIO.output(3, True)
                GPIO.output(5, False)
                GPIO.output(7, False)
                GPIO.output(11, False)

            elif success_ratio >= 0.5 and success_ratio < 0.75:

                GPIO.output(3, True)
                GPIO.output(5, True)
                GPIO.output(7, False)
                GPIO.output(11, False)

            elif success_ratio >= 0.75 and success_ratio < 0.9:

                GPIO.output(3, True)
                GPIO.output(5, True)
                GPIO.output(7, True)
                GPIO.output(11, False)

            elif success_ratio >= 0.9 and success_ratio <= 1:

                GPIO.output(3, True)
                GPIO.output(5, True)
                GPIO.output(7, True)
                GPIO.output(11, True)

            else:

                GPIO.output(3, False)
                GPIO.output(5, True)
                GPIO.output(7, True)
                GPIO.output(11, False)


        print(end_result)

        t_collector.join()
        #time.sleep(1)

        print("\nFINISHED   \n\nActive threads: " + str(threading.activeCount()) + "\nIterations: " +  str(iteration_counter) + "\nSamples processed: " + str(frame_size*stop_at) + "\nPreambles detected: " + str(preamble_detections) + "\nSucesses: " + str(sucesses) + "\nFlipped Sucesses: " + str(flipped_sucesses) + "\nSuccess: " +str(success_ratio) + "\nRuntime: "  +  str(round(time.time() -t, 3)) )

        print('Debug value is ' + str(debug))
        print('Loop value is ' + str(args['infi']))


        if debug == True:
            save('outfile_samples', allsamples)
            save('outfile_signal', end_result)
            save('outfile_SPB', samples_per_bit)

        iteration_counter += 1
        if iteration_counter >= args['itnum']:
            infinite_loop = False

        infinite_loop = args['infi'] 			# -i argument takes precedente over -it argument, thus is updated later, in order to overwrite.
=======

########################################################################
>>>>>>> Testing




    sys.exit(main(sys.argv))
