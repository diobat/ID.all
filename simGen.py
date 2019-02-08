import random
import matplotlib.pyplot as plt
import parseGen
import numpy as np

#payloads = ([1,1,1,0,0,1,0,0], [1,1,0,0,0,1,1,1], [1,1,1,1,1,1,1,1], [0,0,0,0,0,0,0,0], [1,1,1,0,0,1,0,1], [0,0,0,0,0,0,1,0])


def genr_samples(Signal, Packet):

    payloads = ([1,1,1,0,0,1,0,0], [1,1,0,0,0,1,1,1], [1,1,1,1,1,1,1,1], [0,0,0,0,0,0,0,0], [1,1,1,0,0,1,0,1], [0,0,0,0,0,0,1,0])
    fake_signal = [0] * int(random.random() * Signal.silence_samples)
    payload_index = int((random.random() * len(payloads)) - 0.01)

    SPB = int(Signal.samples_per_symbol_raw)


    while len(fake_signal) < Signal.frame_size:

        payload_index = (payload_index+1)%len(payloads)

        for i in Packet.preamble:
            fake_signal.extend([i] * SPB)

        for i in payloads[payload_index]:
            fake_signal.extend([i] * SPB)

        CRC = parseGen.crc_make(list(payloads[payload_index]), Packet.CRC_divisor)

        for i in CRC:
            fake_signal.extend([i] * SPB)

        for i in Packet.STOP_bits:

            fake_signal.extend([i] * SPB)

        fake_signal.extend([0] * Signal.silence_samples)

        #print(payload_index)
        #print(payloads[payload_index])
        #print(CRC)

    noise = np.random.normal(0,0.2,len(fake_signal))
    # args:
    # first is the mean of the normal distribution you are choosing from
    # second is the standard deviation of the normal distribution
    # third is the number of elements you get in array noise

    #lt.subplot(211)
    #plt.plot(fake_signal)



    fake_signal += noise



    #plt.subplot(212)
    #plt.plot(fake_signal)
    #plt.show()

    return fake_signal[1:Signal.frame_size]
