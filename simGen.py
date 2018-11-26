

payloads = ([1,1,1,0,0,1,0,0], [1,1,0,0,0,1,1,1], [1,1,1,1,1,1,1,1], [0,0,0,0,0,0,0,0], [1,1,1,0,0,1,0,1], [0,0,0,0,0,0,1,0])


def generate_signal(Signal):
    pass



def generate_packet(Signal, Packet):

    signal = [0] * int(random.random() * Signal.silence_samples)
    payload_index = int((random.random() * (len(payloads)+1)) - 0.5)

    while len(signal)< Signal.frame_size:           

        for i in payloads[payload_index]
            signal.extend([i] * Signal.samples_per_symbol)
