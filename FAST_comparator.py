

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
<<<<<<< Updated upstream
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
=======
    cooldown = -1 * packet_size_samples

    signal_amplitude = max(signal) - min(signal)

    signal_zero_centered = [(x * 2 - signal_amplitude) for x in signal]
    signal_zero_centered = signal_zero_centered[0:-packet_size_samples]
    transitions = np.where(np.diff(np.signbit(signal_zero_centered)))[0]

    RPrP = []       #Relative preamble harvest positions
    RPaP = []       #Relative payload harvest positions

    y = int(SPB/2)
    for w in range(Packet.preamble_len):
        RPrP.append((w*SPB)+y)

    for w in range(Packet.packet_size):
        RPaP.append((w*SPB)+y)

    print(transitions)
    for x in transitions:
        match = True
        for i in range(len(RPrP)):
            match = match and (signal[x + RPrP[i]] == Packet.preamble[i])
        if match == True and x - cooldown > packet_size_samples:
            for i in range(len(RPaP)):
                position = x + RPaP[i]
                position2 = int(position/SPB)
                end_result[position2] = signal[position]
            cooldown = i

>>>>>>> Stashed changes
    return end_result
