import sys
import pylab   	#Graphical capabilities

def main(args):
    return 0

if __name__ == '__main__':
    
	allsamples = pylab.load('outfile.npy')
	print("Sample Size: " + str(len(allsamples)))
	
	pylab.ioff()
	x = pylab.arange(len(allsamples))
	pylab.plot(x, allsamples)
	pylab.show()
        
	sys.exit(main(sys.argv))
