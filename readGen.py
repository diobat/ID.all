import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import time


path = os.listdir("./outputs")
fig = plt.figure()
ax = fig.add_subplot(111)
plt.title('Validated payloads during last 5 iterations of SoundGen')
plt.xticks(rotation = 45)


def read_payload(path):

	total_data = []
	
	for x in range(len(path)):
		to_open = './outputs/' + path[x]
		#print(to_open)
		data = np.load(to_open).tolist()
		#print(data)
		for y in range(len(data)):
			total_data.append(str(data[y]))

			
	return total_data

def process(total_data):
	total_data_set = set(total_data)
	total_data_set_list = []

	for a in total_data_set:
		total_data_set_list.append(a)
	
	
	repetitions = [[''.join(c for c in total_data_set_list[x] if c.isdigit()),0] for x in range(len(total_data_set))]

	for x in range(len(total_data)):
		for y in range(len(total_data_set_list)):
			if total_data[x] == total_data_set_list[y]:
				repetitions[y][1] += 1


	for x in range(len(repetitions)):		
		print(str(repetitions[x][0]) + "	" + str(repetitions[x][1]))

	return repetitions

def update(i):
	print('\n\n\n ')
	
	path = os.listdir("./outputs")
	total_data = read_payload(path)
	repetitions = process(total_data)
	payloads = [row[0] for row in repetitions]
	frequency = [row[1] for row in repetitions]
	ax.clear()
	ax.bar(range(len(repetitions)), frequency, tick_label=payloads)
	
	plt.title('Validated payloads during last 5 iterations of SoundGen')
	plt.xticks(rotation = 45)
	plt.xlabel('Payloads')
	plt.ylabel('Number of repetitions')
	plt.ylim([0, 150])
	
	
	
		
path = os.listdir("./outputs")
total_data = read_payload(path)
repetitions = process(total_data)
payloads = [row[0] for row in repetitions]
frequency = [row[1] for row in repetitions]
ax.bar(range(len(repetitions)), frequency, tick_label=payloads)


ani = animation.FuncAnimation(fig, update, interval=5000)
plt.show()
