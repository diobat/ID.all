########################################################################
### SIGNAL PARSING
########################################################################



def binary_parse(symbol_list, preamble, packet_size, payload_size, STOP_bits):

	flipped_symbol_list = [1 - x for x in symbol_list]

	sucesses = 0
	preamble_detections = 0
	message_result = []

	# CRC
	CRC_divisor = [1,0,1,0]

	xv = -1 * packet_size

	for x in range(len(symbol_list) - packet_size) :
		
		if symbol_list[x:x+len(preamble)] == preamble:						# Detects preambles
			preamble_detections += 1                                										# Counts them
			if crc_check(symbol_list[x+len(preamble):x+packet_size],CRC_divisor, payload_size, STOP_bits):
				validated_payload =  symbol_list[x+len(preamble):x+len(preamble)+payload_size]

				if x > (xv + packet_size + 5):
					xv = x
					message_result.append(validated_payload)											        	# If validaded adds to the output batch
					sucesses += 1
					cooldown = x

	return message_result, sucesses, preamble_detections

def crc_check(payload_crc_stop, binary_divisor, payload_size, expected_STOP_bits):	#CRC validation

	#print("payload + crc = " + str(payload_crc))
	
	payload_crc = payload_crc_stop[:payload_size + len(binary_divisor)-1]
	stop_bits = payload_crc_stop[payload_size + len(binary_divisor)-1:]
	
	#print('\n\n\n\nPayload + CRC: ' + str(payload_crc))
	#print('Stop Bits: ' + str(stop_bits))
	#print('Expected Stop Bits: ' + str(expected_STOP_bits))
		

	validity = [0 for x in range(len(binary_divisor)-1)]
	validity.extend(expected_STOP_bits)

	for x in range(len(payload_crc) - (len(binary_divisor)-1)):			# For an indepth explanation of this function visit the wikipedia page: Cyclic Redundancy Check
		if payload_crc[x] == 1:
			for y in range(len(binary_divisor)-1):
				payload_crc[x+y] = payload_crc[x+y] ^ binary_divisor[y]		# ^ = XOR


	result = payload_crc[-3:] + stop_bits

	#print("\nFINAL CRC = " + str(result))
	#print("validity = " + str(validity))

	return result == validity
	#return True


def crc_make(payload, binary_divisor):

	validity = [0 for x in range(len(binary_divisor)-1)]
	payload_crc = payload
	payload_crc.extend(validity)

	for x in range(len(payload_crc) - (len(binary_divisor)-1)):			# For an indepth explanation of this function visit the wikipedia page: Cyclic Redundancy Check
		if payload_crc[x] == 1:
			for y in range(len(binary_divisor)-1):
				payload_crc[x+y] = payload_crc[x+y] ^ binary_divisor[y]		# ^ = XOR

	return payload_crc[-3:]

def parityOf(int_type): 							#Parity validation


	for bit in int_type:
		x = (x << 1) | bit

	parity = False
	while (x):
		parity = ~parity
		x = x & (x - 1)
	return(parity)
