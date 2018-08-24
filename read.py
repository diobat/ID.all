import os
import numpy as np


path = os.listdir("./outputs")

print(path)

to_open = './outputs/' + path[0]

print(to_open)

data = np.load(to_open)

print(data)

to_open = './outputs/' + path[1]

print(to_open)

data = np.load(to_open)

print(data)

to_open = './outputs/' + path[2]

print(to_open)

data = np.load(to_open)

print(data)

to_open = './outputs/' + path[3]

print(to_open)

data = np.load(to_open)

print(data)

to_open = './outputs/' + path[4]

print(to_open)

data = np.load(to_open)

print(data)
