import random
import matplotlib.pyplot as plt
import parseGen

#payloads = ([1,1,1,0,0,1,0,0], [1,1,0,0,0,1,1,1], [1,1,1,1,1,1,1,1], [0,0,0,0,0,0,0,0], [1,1,1,0,0,1,0,1], [0,0,0,0,0,0,1,0])


def genr_samples(Signal, Packet):

    payloads = ([1,1,1,0,0,1,0,0], [1,1,0,0,0,1,1,1], [1,1,1,1,1,1,1,1], [0,0,0,0,0,0,0,0], [1,1,1,0,0,1,0,1], [0,0,0,0,0,0,1,0])
    fake_signal = [0] * int(random.random() * Signal.silence_samples)
    payload_index = int((random.random() * len(payloads)) - 0.01)

    SPB = int(Signal.samples_per_symbol)

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



    #plt.plot(fake_signal)
    #plt.show()

    return fake_signal[1:Signal.frame_size]
