.. SoundGen documentation master file, created by
   sphinx-quickstart on Thu Oct  4 20:37:05 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to SoundGen's documentation!
====================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`


What is SoundGen:
=================

| SoundGen is a flexible burst mode ASK signal demodulator and frame processer, created with DVB-T in mind.
| This software couples an easy setup with the advantage of the flexible tuning mechanism included in the SDR kit. It includes the possibility of network integration.
| The script has been tested only for scenarios where an emitter is transmitting ASK encoded frames in bursts, spaced by periods of silence. It is very unlikely successful demodulations will occur in any other scenario.
| This user guide is oriented towards the final user, if you are a developer who wishes to contribute please read the master thesis associated with this project. Furthermore, all the detail in this document assume you are working with a clone of the SD card.

Example:

Demodulating a signal with a 5kHz symbol rate riding on a 95MHz carrier wave is as simple as::

 python3 SoundGen.py -f 95000000 -sym 5000

The repository can be found at https://github.com/Espigao25/SoundGen_Python3

How to install:
===============

1. First of all, install all the dependencies. This step is not necessary if you have been provided with a cloned microSD card.

|   PyLab
|   RtlSdr
|   argparse
|   numpy
|   matplotlib


2. Connect the receiver/SDR kit to your platform via USB, run rtl_test on the command line to check if the kit was properly detected. Remember to use an adequate antenna to the carrier wave you intend to sniff.

3. "python3 SoundGen.py -h" on the terminal will give you a list of all the arguments you can pass into the script. They are:

+---------------+--------------------------------------------------------------------------+
| Argument name | Argument description                                                     |
+---------------+--------------------------------------------------------------------------+
| -f            |  Center frequency tuning, should equal the freq of your carrier wave     |
+---------------+--------------------------------------------------------------------------+
| -samp         |  Sampling rate                                                           |
+---------------+--------------------------------------------------------------------------+
| -sym          |  Symbol rate                                                             |
+---------------+--------------------------------------------------------------------------+
| -sf           |  Frame size in samples                                                   |
+---------------+--------------------------------------------------------------------------+
| -nf           |  Number of frames to process before exiting (unless inf mode is enabled) |
+---------------+--------------------------------------------------------------------------+
| -gain         |  Software gain, must belong to interval [0 50]                           |
+---------------+--------------------------------------------------------------------------+
| -i            |  Infinite mode, runs the program indefinitely if True                    |
+---------------+--------------------------------------------------------------------------+
|-db            |  Debug mode, dumps debugging info into three distinct outfiles           |
+---------------+--------------------------------------------------------------------------+



Demodulation
===============

Simply providing the program with

Frame processing
=================

Not only will this package demodulate ASK frames, it will also process them according to the following protocol.
PREAMBLE + DATA + PARITY + STOP BIT


Network integration
====================

During normal

Debugging mode
===============

WARNING: ENABLING INFINITE MODE AND DEBUGGING MODE IN THE SAME EXECUTION IS NOT ADVISABLE.

| When the argument -db is set to 'True', the program will produce three aditional .npy files in parallel to it's normal outputs. These files will be placed in the script's root folder. Any debugging files from previous executions of the script still present in the destination folder will be overwritten.
| They contain the following information:

outfile_samples.npy
  A list with all the samples collected during the programs execution. This file can get very big very fast. After a few minutes of continuous execution this will become a major resource hog, it will slowdown the script considerably.

outfile_signal.npy
  A list with the demodulation result of the entire program execution. If multiple frames were processed the results will be concatenated into a single list.

outfile_SPB.npy
  A numeric value which equals the ratio: SamplingRate/SymbolRate

Infinite mode
===============

WARNING: DO NOT USE DEBUGGING MODE AND INFINITE MODE AT THE SAME TIME DURING PROLONGUED PERIODS OF TIME. (>2 MINS)

GPIO
===============

Some GPIO pins are configured into feedback generators.

[FAZER ESQUEMA NO VISIO]

SSH connection
===============

The main outputs produced by the program are printed via terminal fully compatible with remote SSH connections. FTP is also possible in order to acess all the outfiles.
The Raspberry PI will by default create a hotspot called RPI2. The password to connect is password123

Autonomous mode
===============
