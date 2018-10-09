### Made by Diogo Batista (diogobatista@ua.pt) as part of my Integrated Master's thesis

#### If any issues arise, try :

	# First time setup? Issues with SDR kit compatibility? Check:  https://gist.github.com/floehopper/99a0c8931f9d779b0998

	# Issues with numpy module? On terminal: pip3 install --upgrade --ignore-installed --install-option '--install-data=/usr/local' numpy

from pylab import *   	#Graphical capabilities, network and debug outfiles
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
import argparse			#argumment management
#import scipy.signal

########################################################################
### PARSING INPUT ARGUMENTS
########################################################################

parser = argparse.ArgumentParser(prog = 'SoundGen', description='Made by Diogo Batista, diogobatista@ua.pt', epilog=' ',)

parser.add_argument('-f','--freq', help='Center Frequency',type=int, required=True)
parser.add_argument('-s','--samp', help='Sampling rate, default is 226kHz', type=int, required=False, default = 226000)
parser.add_argument('-g','--gain', help='Gain, [0 50], default is 15', type=int,required=False, default = 15)
parser.add_argument('-sf','--sfram', help='Frame size, default is 32k', type=int, required=False, default = 32*1024)
parser.add_argument('-nf','--nfram', help='Number of frames to be collected before program ends, default is 1, must be 1 or greater', type=int, required=False, default = 1)
parser.add_argument('-db','--dbug', help='DebugMode, default is False', required=False, type=bool, default = False)
parser.add_argument('-i','--infi', help='InfiniteMode, default is True', required=False, default = True)
parser.add_argument('-sym','--symb', help='Symbol Rate of expected ASK signal', type=int, required=True, default = 3650)
args = vars(parser.parse_args())

#args['freq'] will contain the value of arg '-f'
#args['samp'] will contain the value of optional argument '-s' if any value was passed
#etc

print(args)

########################################################################
### DECLARING VARIABLES
########################################################################


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
signal_frequency = 2800 * decimation_factor				# Baseband frequency of the desired signal it should be no higher than one tenth of the SDR kit sampling rate
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
global sample_buffer
sample_buffer = queue.Queue(buffer_size)


## Flow control

global iteration_counter, stop_at, debug
iteration_counter = 0									# Counts the number of frames collected so far
stop_at = args['nfram']									# How many frames of data the program will collect and process before it ends
infinite_loop = True									# Flag that controls wether the program will leave the main loop
debug = args['dbug']									# Debug capabilities switch

## Led Setup

USE_LEDS = True
heartbeat = True
max_packages = stop_at * 10;

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(3, GPIO.OUT)
GPIO.setup(5, GPIO.OUT)
GPIO.setup(7, GPIO.OUT)
GPIO.setup(11, GPIO.OUT)
GPIO.setup(13, GPIO.OUT)


## Debugging variables

allsamples = array.array('f',[0])


########################################################################
### FUNCTIONS
########################################################################

def main(args):
    return 0

def parityOf(int_type): # Check parity

	x = 0
	for bit in int_type:
		x = (x << 1) | bit

	parity = False
	while (x):
		parity = ~parity
		x = x & (x - 1)
	return(parity)


def collectData(): 	#Collect samples

	global frame_size
	global iteration_counter, flag_end, stop_at
	iteration_counter = 0
	t = time.time()
	while iteration_counter < stop_at:
		sample_buffer.put_nowait(abs(sdr.read_samples(frame_size))**2)  ## Harvests samples and stores their ABSOLUTE VALUES into a FIFO
		iteration_counter += 1
	print("\n###TERMINEI A RECOLHA DE AMOSTRAS EM " + str(round(time.time() -t, 3)) + ". TEMPO IDEAL = " +str(round((frame_size*stop_at)/sdr.sample_rate, 3)) + "###\n")
	flag_end = True


def threadInit():	#Initialize threads
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



	while infinite_loop == True:

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

		# Count the number of sucesses

		for x in range(len(end_result) - len(desired_result)):
			if end_result[x:x+len(desired_result)] == desired_result:
				sucesses += 1

		for x in range(len(flipped_endresult) - len(desired_result)):
			if flipped_endresult[x:x+len(desired_result)] == desired_result:
				flipped_sucesses += 1

		message_result = []

		for x in range(len(end_result) - len(preamble)):				#Detects preambles
			if end_result[x:x+len(preamble)] == preamble:
				preamble_detections += 1
				if parityOf(end_result[x:x+packet_size]):
					message_result.append(end_result[x+len(preamble)-1:x+len(preamble)+info_size-1])

		output_list = os.listdir("./outputs")

		if len(output_list) >= 5:
			os.remove('./outputs/' + min(output_list))	#If there are 5 files or more in the outputs folder, delete the oldest file. Filenames are timestamps so its easy to find the oldest one.

		save('./outputs/' + str(datetime.datetime.now()), message_result)



		if USE_LEDS == True:

			max_sucesses = max(sucesses, flipped_sucesses)
			success_ratio = max_sucesses/max_packages

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

		infinite_loop = args['infi'] 			# Update the flow control variable to match the user argument

	sys.exit(main(sys.argv))
