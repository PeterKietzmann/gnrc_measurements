#!/usr/bin/env python

import os, signal, sys, subprocess, serial, time
from pexpect import spawn, TIMEOUT, EOF

###################### SET PARAMETERTS ######################
NUM_PACKETS = 10000;
MIN_PACKET_SIZE = 10;
MAX_PACKET_SIZE = 1211;
STEP_SIZE = 10;

DELAY_PACKET_US = 0;
DELAY_SIZE_US = 0;

BOARD='native';
#BOARD='samr21-xpro';
#BOARD='arduino-due';
#BOARD='nucleo-l1';
#BOARD='arduino-due';
#BOARD='iotlab-m3';
if BOARD == 'native':
	board_switch = 0
else:
	board_switch = 1


###################### xxxxxxxxxxxxxx ######################

subprocess.call(['rm py_config_'+str(NUM_PACKETS)+'_'+BOARD+'.txt'], shell=True)
text_config = open('py_config_'+str(NUM_PACKETS)+'_'+BOARD+'.txt', "w")

# write experiment configuration to text file
text_config.write('NUM_PACKETS '+str(NUM_PACKETS)+'\n')
text_config.write('MIN_PACKET_SIZE '+str(MIN_PACKET_SIZE)+'\n')
text_config.write('MAX_PACKET_SIZE '+str(MAX_PACKET_SIZE)+'\n')
text_config.write('STEP_SIZE '+str(STEP_SIZE)+'\n')
text_config.write('DELAY_PACKET_US '+str(DELAY_PACKET_US)+'\n')
text_config.write('DELAY_SIZE_US '+str(DELAY_SIZE_US)+'\n')
#text_config.write('BOARD '+str(board_switch)+' \n')

text_config.close()

print 'NUM_PACKETS = ', NUM_PACKETS
print 'MIN_PACKET_SIZE = ', MIN_PACKET_SIZE
print 'MAX_PACKET_SIZE = ', MAX_PACKET_SIZE
print 'STEP_SIZE = ', STEP_SIZE
print 'DELAY_PACKET_US = ', DELAY_PACKET_US
print 'DELAY_SIZE_US = ', DELAY_SIZE_US
print 'BOARD = ', BOARD





subprocess.call(['rm single_measure_temp.txt'], shell=True)

os.chdir("../")
path_vec = (os.getcwd()+'/posix_udp'); ########## here #################
os.chdir("py_save_all_txt/")

text_files = open( 'single_measure_temp.txt', "a");

os.chdir("../")

if BOARD == 'native':
	native_elf_vec = [os.getcwd()+"/posix_udp/bin/native/posix_udp.elf"];
else:
	if BOARD=='iotlab-m3':
		# Open serial port
		port = serial.Serial(
			port='/dev/ttyUSB1',
			baudrate=500000, 
			dsrdtr=0, 
			rtscts=0
		)
	if BOARD=='samr21-xpro':
		port = serial.Serial(
			port='/dev/ttyACM0',
			baudrate=115200, 
			dsrdtr=0, 
			rtscts=0
		)
	if BOARD=='arduino-due':
		# Open serial port
		port = serial.Serial(
			port='/dev/ttyACM0',
			baudrate=115200, 
			dsrdtr=0, 
			rtscts=0
		)

	port.setDTR(0)
	port.setRTS(0)

	# Short delay to initialize port
	time.sleep(1)
	port.close()

#	try: 
#		port.open()
#
#	except Exception, e:
#
#		print "error open serial port: " + str(e)
#
#		exit()

in_run = False

loopback_mode_vec = [0, 1]; # 0 = l2 loopback 1: ipv6 loopback
print_loopback_mode = ['l2 reflector', 'ip loopback'];
measure_mean_vec = [0, 1, 2];
print_mean_mode = ['single', 'conjoint', 'increment'];


for k in range(1,2): # loopback 2oes ip and l2 #0, 2
	for y in range(0,1): # kinds of measurement regarding mean calculation #0,3

		MEASURE_MEAN = measure_mean_vec[y]; # 0: Measure each packet and save value
											# 1: Measure all packets and save value
											# 2: Measure each packet but increment all
		print 'MEASURE_MEAN_'+str(MEASURE_MEAN)
		# Make a copy of the environment and modify that.
		myenv = dict(os.environ) 
		myenv["CFLAGS"] = ('-DNUM_PACKETS='+str(NUM_PACKETS)+' -DMIN_PACKET_SIZE='+str(MIN_PACKET_SIZE)+
		' -DMAX_PACKET_SIZE='+str(MAX_PACKET_SIZE)+' -DSTEP_SIZE='+str(STEP_SIZE)+' -DDELAY_PACKET_US='+str(DELAY_PACKET_US)+
		' -DDELAY_SIZE_US='+str(DELAY_SIZE_US)+' -DLOOPBACK_MODE='+str(loopback_mode_vec[k])+' -DMEASURE_MEAN='+str(MEASURE_MEAN)+' ')

		myenv["BOARD"] = BOARD


		switch_API_udp_ip = 0

		os.chdir(path_vec)
		print os.getcwd()
		# Clean build environement by interacting with shell
		subprocess.call(['rm -rf bin/'], shell=True)

		# Pass the modified environment to the subprocess.
		subprocess.check_call(["make"], env=myenv)

		time.sleep(1)


		if BOARD == 'native':
			myproc = subprocess.Popen(native_elf_vec, stdout=subprocess.PIPE)

		else:
			# Flash to MCU by interactiong with shell
			subprocess.call(['make flash'],env=myenv, shell=True)
			
			try: 
				port.open()

			except Exception, e:

				print "error open serial port: " + str(e)

				exit()

		while(1):
			if BOARD != 'native':
				c = port.readline().strip()
			else:
				c = myproc.stdout.readline().strip()

			if c != 'DONE' and c!= 'test' and in_run:
				#print(c)
				text_files.write(c+'\n')

			if c == 'START':
				print str(int(time.time()))
				in_run = True
				#string = print_loopback_mode[k]+' '+print_mean_mode[y]+' '+path_vec+'\n'
				#text_files.write(string) #

			if c == 'DONE':
				print str(int(time.time()))
				print 'Finished run'
				in_run = False
				text_files.write('\n')
				break

			# else:
			# 	print c
			# 	text_files[(y +(k*3))+switch_API_udp_ip].write(c+'\n')

		# !in_run
		if BOARD == 'native':
			myproc.kill()

		time.sleep(1)

if BOARD != 'native':
	port.close();    # Just call this in the last iteration!

text_files.close()

print 'FINISHED ALL'
