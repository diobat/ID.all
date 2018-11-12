########################################################################
### NETWORK INTEGRATION
########################################################################
import os
import datetime			#timestamps for the outfiles
import numpy as np


def save_payload(message_result, debug_value, allsamples, end_result, samples_per_symbol):
	
	
	if debug_value == True:
		np.save('outfile_samples', allsamples)
		np.save('outfile_signal', end_result)
		np.save('outfile_SPB', samples_per_symbol)
	
	if not os.path.isdir(".outputs"):				#If the outputs folder does not exist, it will create it.
		os.makedirs(".outputs")
	
	output_list = os.listdir("./outputs")

	if len(output_list) >= 5:
		os.remove('./outputs/' + min(output_list))					#If there are 5 files or more in the outputs folder, delete the oldest file. Filenames are timestamps so its easy to find the oldest one.

	np.save('./outputs/' + str(datetime.datetime.now()), message_result)
	
