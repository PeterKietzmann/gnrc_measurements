#!/usr/bin/env python

import os, signal, sys, subprocess, serial, time
from pexpect import spawn, TIMEOUT, EOF
import numpy as np
import argparse

###################### SET PARAMETERTS ######################

DELAY_PACKET_US = 0;
DELAY_SIZE_US = 0;

#BOARD='native';
#BOARD='samr21-xpro';
BOARD='iotlab-m3';
#BOARD='nucleo-l1';
#BOARD='stm32f4discovery';


#NAME_STRING_ADD = '_V2';
NAME_STRING_ADD = '';


if BOARD == 'native':
	board_switch = 0
else:
	board_switch = 1



###################### xxxxxxxxxxxxxx ######################

path_vec = [];


subprocess.call(['rm *ip_stack_'+BOARD+NAME_STRING_ADD+'.txt'], shell=True)
subprocess.call(['rm *l2_stack_'+BOARD+NAME_STRING_ADD+'.txt'], shell=True)

os.chdir("../")
path_vec.append(os.getcwd()+'/posix_udp');
path_vec.append(os.getcwd()+'/gnrc_conn_udp');
path_vec.append(os.getcwd()+'/plain_udp');
# path_vec.append(os.getcwd()+'/posix_ip');
# path_vec.append(os.getcwd()+'/gnrc_conn_ip');
# path_vec.append(os.getcwd()+'/plain_ip');


os.chdir("py_save_all_txt/")


text_files = [
			open('posix_udp_l2_stack_'+BOARD+NAME_STRING_ADD+'.txt', "a"), 
			open('gnrc_conn_udp_l2_stack_'+BOARD+NAME_STRING_ADD+'.txt', "a"), 
			open('plain_udp_l2_stack_'+BOARD+NAME_STRING_ADD+'.txt', "a"), 

			open('posix_ip_l2_stack_'+BOARD+NAME_STRING_ADD+'.txt', "a"), 
			open('gnrc_conn_ip_l2_stack_'+BOARD+NAME_STRING_ADD+'.txt', "a"), 
			open('plain_ip_l2_stack_'+BOARD+NAME_STRING_ADD+'.txt', "a"), 

			open('posix_udp_ip_stack_'+BOARD+NAME_STRING_ADD+'.txt', "a"), 
			open('gnrc_conn_udp_ip_stack_'+BOARD+NAME_STRING_ADD+'.txt', "a"), 
			open('plain_udp_ip_stack_'+BOARD+NAME_STRING_ADD+'.txt', "a"), 

			open('posix_ip_ip_stack_'+BOARD+NAME_STRING_ADD+'.txt', "a"), 
			open('gnrc_conn_ip_ip_stack_'+BOARD+NAME_STRING_ADD+'.txt', "a"), 
			open('plain_ip_ip_stack_'+BOARD+NAME_STRING_ADD+'.txt', "a"), 
			];



os.chdir("../")

if BOARD == 'native':
	native_elf_vec = [];
	native_elf_vec.append(os.getcwd()+"/posix_udp/bin/native/posix_udp.elf");
	native_elf_vec.append(os.getcwd()+"/gnrc_conn_udp/bin/native/gnrc_conn_udp.elf");
	native_elf_vec.append(os.getcwd()+"/plain_udp/bin/native/plain_udp.elf");
	native_elf_vec.append(os.getcwd()+"/posix_ip/bin/native/posix_ip.elf");
	native_elf_vec.append(os.getcwd()+"/gnrc_conn_ip/bin/native/gnrc_conn_ip.elf");
	native_elf_vec.append(os.getcwd()+"/plain_ip/bin/native/plain_ip.elf");
else:
	if BOARD=='iotlab-m3':
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
	# ATTENTION: ALL THESE BOARDS HAVE BEEN TETED WITH EXTERNAL UART CONVERTERS
	if BOARD=='nucleo-l1':
		# Open serial port
		port = serial.Serial(
			port='/dev/ttyUSB0',
			baudrate=115200, 
			dsrdtr=0, 
			rtscts=0
		)
	if BOARD=='stm32f4discovery':
		# Open serial port
		port = serial.Serial(
			port='/dev/ttyUSB0',
			baudrate=115200, 
			dsrdtr=0, 
			rtscts=0
		)
	if BOARD=='arduino-due':
		# Open serial port
		port = serial.Serial(
			port='/dev/ttyUSB0',
			baudrate=115200, 
			dsrdtr=0, 
			rtscts=0
		)

	port.setDTR(0)
	port.setRTS(0)

	# Short delay to initialize port
	time.sleep(1)
	port.close()

	try: 
		port.open()

	except Exception, e:

		print "error open serial port: " + str(e)

		exit()

in_run = False

loopback_mode_vec = [0, 1]#, 1]; # 0 = l2 loopback 1: ipv6 loopback 
loopback_mode_vec_str=['L2 Reflector', 'IP Loopback'];

payload_vec = np.arange(10, 1211, 10);
print str(payload_vec)

number_of_measurements = len(loopback_mode_vec) * len(path_vec) * len(payload_vec)
measurements_counter = 0;


# Define some command line args
p = argparse.ArgumentParser()
p.add_argument("appdir", default="../RIOT/examples/hello-world", nargs="?", help="Full path to application dir")
p.add_argument("board", default="iotlab-m3", nargs="?", help="BOARD to analyze")
p.add_argument("-p", default="", help="Toolchain prefix, e.g. arm-none-eabi-")
p.add_argument("-v", action="store_true", help="Dump symbol sizes to STDIO")
args = p.parse_args()

count=0;

for k in range(0,len(loopback_mode_vec)): # loopback modes ip and l2
	for y in range(0,len(payload_vec)):

		# Make a copy of the environment and modify that.
		myenv = dict(os.environ) 
		myenv["CFLAGS"] = ('-DPACKET_SIZE='+str(payload_vec[y])+' -DLOOPBACK_MODE='+str(loopback_mode_vec[k]));

		myenv["BOARD"] = BOARD

		for x in range(0,len(path_vec)): # measureing posix, conn and plain for udp and/or IP APIs

			measurements_counter+=1

			print '### Starting measurement ' +str(measurements_counter)+ ' of ' +str(number_of_measurements)+ ' ###'

			os.chdir(path_vec[x])
			print os.getcwd()
			# Clean build environement by interacting with shell
			subprocess.call(['rm -rf bin/'], shell=True)

			# Pass the modified environment to the subprocess.
			myproc = subprocess.check_call(["make"], env=myenv)

			if BOARD == 'native':
				myproc = subprocess.Popen(native_elf_vec[x], stdout=subprocess.PIPE)

			else:
				# Flash to MCU by interactiong with shell
				subprocess.call(['make flash'], env=myenv, shell=True)

			while(1):
				if BOARD != 'native':
					c = port.readline().strip()
					print c
				else:
					c = myproc.stdout.readline().strip()

				if c != 'DONE' and in_run:
					text_files[(k*len(path_vec))+x].write(c+'\n')

				if c == 'START':
					print 'START identified'
					in_run = True
					#string = print_loopback_mode[k]+' '+print_mean_mode[y]+' '+path_vec[x]+'\n'
					#text_files[(y +(k*3))+switch_API_udp_ip].write(string) #

				if c == 'DONE':
					print 'DONE identified'
					in_run = False
					text_files[(k*len(path_vec))+x].write('\n')
					break



for a in range (0, len(text_files)):
	text_files[a].close()

print 'FINISHED ALL'
