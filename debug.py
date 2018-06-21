import sys
import pylab   	#Graphical capabilities

def main(args):
    return 0

if __name__ == '__main__':
    
	allsamples = pylab.load('outfile_samples.npy')
	end_result = pylab.load('outfile_signal.npy')
	samples_per_bit = pylab.load('outfile_SPB.npy')
	print("Sample Size: " + str(len(allsamples)))
	
	demod_signal=[0.5 for x in allsamples]
	counter = 1
	
	
	for x in range(len(end_result)):
		a = int(round(samples_per_bit * (counter-1)))
		b = int(round(samples_per_bit * counter))
		for c in range(a,b):
			demod_signal[c] = end_result[x]
		counter += 1
			
	pylab.ioff()
	x = pylab.arange(len(allsamples))
	pylab.subplot(211)
	pylab.plot(x, allsamples)
	pylab.subplot(212)
	pylab.plot(x, demod_signal, 'r')
	
	
	pylab.show()
        
	sys.exit(main(sys.argv))
