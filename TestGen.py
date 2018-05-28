from pylab import *   	#Graphical capabilities
from rtlsdr import *	#SDR
import queue			#FIFO/queue
import threading		#Multi-threading
import time


sdr = RtlSdr()


########################################################################
### DECLARING VARIABLES
########################################################################


#private variables
buffer_size = 10000
global sample_buffer
sample_buffer = queue.Queue(buffer_size)




# configure SDR device
sdr.sample_rate = 0.3e6
sdr.center_freq = 1000073000
sdr.gain = 25
global frame_size
frame_size = 32*1024


global data_ready
data_ready = 0
global x
x = range(frame_size)
global samples
samples = zeros(frame_size)


global fig1
global ax1





########################################################################
### DEFINING OBJECTS
########################################################################


def collectData(): 	#Collect samples

	global samples
	global frame_size
	global data_ready


	while True:
	#if data_ready == 0:
		samples = sdr.read_samples(frame_size)
		data_ready = 1
		print("RECOLHI DADOS")
		time.sleep(2)
	
	
#def plotData():		#Plot samples
#	
#	global samples
#	global x
#	global fig
#	global ax
#	global line1
#	global data_ready
#	
#	while True:
#		# use matplotlib to estimate and plot the PSD
#		if data_ready == 1:
#			abs_samples = abs(samples)
#			for step in x:
#				line1.set_ydata(abs_samples[step])
#				fig.canvas.draw()
#				fig.canvas.flush_events()
#			data_ready = 0
		
	
	
def threadInit():
	print("ESTOU AQUI")
	global t_collector, t_plotter
	t_collector = threading.Thread(target=collectData, name="Collector", args=[])
	#print(str(threading.active_count()))
	#t_plotter = threading.Thread(target=plotData, name="Plotter", args=[])
	
def plotInit(): 
	
	global fig
	global ax
	global line1
	global samples
	global x
	global frame_size

	
	fig = figure()
	ax = fig.add_subplot(1,1,1)
	line1, = ax.plot(x, samples, 'r-')
	ax.set_xlim(0, frame_size)
	ax.set_ylim(0, 0.5)
	



if __name__ == "__main__":
	
	ion() # Turn on the interactive mode of PyLab, required in order to update the plots in real time
	threadInit()  # Initialize the required threads.
	plotInit()
	

	t_collector.start()
	#t_collector.run()
	
	#t_plotter.start()
	#t_plotter.run
	
	
	
	while True:
				# use matplotlib to estimate and plot the PSD
		if data_ready == 1:
			abs_samples = abs(samples)
			#for step in x:
			line1.set_ydata(abs_samples)
			fig.canvas.draw()
			fig.canvas.flush_events()
			data_ready = 0
			print("IMPRIMI DADOS")
		

