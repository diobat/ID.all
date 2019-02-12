import os
import numpy as np



#This script reads and prints in text format all the files in the ./outputs/ folder

path = os.listdir("./outputs")

print(path)



##### FILE 1

to_open = './outputs/' + path[0]

print(to_open)

data = np.load(to_open)

print(data)




##### FILE 2

to_open = './outputs/' + path[1]

print(to_open)

data = np.load(to_open)

print(data)



##### FILE 3

to_open = './outputs/' + path[2]

print(to_open)

data = np.load(to_open)

print(data)




##### FILE 4

to_open = './outputs/' + path[3]

print(to_open)

data = np.load(to_open)

print(data)




##### FILE 5

to_open = './outputs/' + path[4]

print(to_open)

data = np.load(to_open)

print(data)
