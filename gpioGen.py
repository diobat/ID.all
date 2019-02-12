########################################################################
### RPI GPIO UPDATING
########################################################################



import RPi.GPIO as GPIO	#LED's

def update(success_ratio):


	heartbeat = not GPIO.input(13)
	GPIO.output(13, heartbeat)			#Toggle the heartbeat value


	if success_ratio >= 0 and success_ratio < 0.25:

		GPIO.output(3, False)
		GPIO.output(5, False)
		GPIO.output(7, False)
		GPIO.output(11, False)

	elif success_ratio >= 0.25 and success_ratio < 0.5:

		GPIO.output(3, True)
		GPIO.output(5, False)
		GPIO.output(7, False)
		GPIO.output(11, False)

	elif success_ratio >= 0.5 and success_ratio < 0.75:

		GPIO.output(3, True)
		GPIO.output(5, True)
		GPIO.output(7, False)
		GPIO.output(11, False)

	elif success_ratio >= 0.75 and success_ratio < 0.9:

		GPIO.output(3, True)
		GPIO.output(5, True)
		GPIO.output(7, True)
		GPIO.output(11, False)

	elif success_ratio >= 0.9 and success_ratio <= 1:

		GPIO.output(3, True)
		GPIO.output(5, True)
		GPIO.output(7, True)
		GPIO.output(11, True)

	else:

		GPIO.output(3, False)
		GPIO.output(5, True)
		GPIO.output(7, True)
		GPIO.output(11, False)
