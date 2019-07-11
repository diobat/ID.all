import sys
import pylab   	#Graphical capabilities
import DEEP_comparator, PBZ_comparator, FAST_comparator #data recovery abilities

if __name__ == '__main__':

    allsamples = pylab.load('outfile_samples.npy')
    end_result = pylab.load('outfile_signal.npy')
    #samples_per_bit = pylab.load('outfile_SPB.npy')
    samples_per_bit = 61.917808219178085
    print(sys.version)
    print("Sample Size: " + str(len(allsamples)))



    demod_signal = PBZ_comparator.compare_signal(allsamples, samples_per_bit)

    pylab.ioff()
    x = pylab.arange(len(allsamples))
    pylab.subplot(211)
    pylab.plot(x, allsamples)
    pylab.subplot(212)
    pylab.plot(x, demod_signal, 'r')


    pylab.show()

    sys.exit(main(sys.argv))
