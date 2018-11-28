

# This comparator was designed to work for a packet preamble of exactly [1,1,1,0], it was not tested under any other cases.


import numpy as np
import matplotlib.pyplot as plt
import time



def compare_signal(signal, samples_per_bit, Packet):

    SPB = int(samples_per_bit)

    threshold =  max(signal)/2

    raw_signal = signal
    signal = np.where(np.asarray(signal) > threshold, 1, 0)

    cooldown = 0
    index = -1
    end_result = [0] * int(len(signal)/SPB)
    this_packet = []

    packet_size_samples = Packet.packet_size * SPB
    max_index = len(signal) - packet_size_samples
    window = int(SPB * 2.5)
    windowz = [0] * window
    window1 = [1] * window

    for index in range(max_index):
        cooldown -= 1
        windowz.pop(0)
        windowz.append(signal[index])
        if cooldown < 0:
            if windowz == window1:
                cooldown = packet_size_samples
                offset = next((i for i, x in enumerate(signal[index:index+packet_size_samples]) if (not x)))
                offset += int(3/2 * SPB)

                for x in range(Packet.packet_size - Packet.preamble_len):
                    position = index + offset + (x*SPB)
                    position2 = int(position/SPB)
                    end_result[position2] = signal[position]


    #plt.show()
    return end_result
