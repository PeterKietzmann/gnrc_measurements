#!/usr/bin/env python

import os, signal, sys, subprocess, serial, time
from pexpect import spawn, TIMEOUT, EOF
import numpy as np
import argparse

from shutil import copyfile

###################### SET PARAMETERTS ######################

NUM_PACKETS = 1000;
MIN_PACKET_SIZE = 10;
MAX_PACKET_SIZE = 1211;
STEP_SIZE = 10;

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


subprocess.call(['rm *ip_mem_'+BOARD+NAME_STRING_ADD+'.txt'], shell=True)
subprocess.call(['rm *l2_mem_'+BOARD+NAME_STRING_ADD+'.txt'], shell=True)

os.chdir("../")
path_vec.append(os.getcwd()+'/posix_udp');
path_vec.append(os.getcwd()+'/gnrc_conn_udp');
path_vec.append(os.getcwd()+'/plain_udp');
path_vec.append(os.getcwd()+'/posix_ip');
path_vec.append(os.getcwd()+'/gnrc_conn_ip');
path_vec.append(os.getcwd()+'/plain_ip');

app_vec=[];
app_vec.append('posix_udp');
app_vec.append('gnrc_conn_udp');
app_vec.append('plain_udp');
app_vec.append('posix_ip');
app_vec.append('gnrc_conn_ip');
app_vec.append('plain_ip');

os.chdir("py_save_all_txt/")



text_files = [
			open('posix_udp_l2_mem_'+BOARD+NAME_STRING_ADD+'.txt', "a"), 
			open('gnrc_conn_udp_l2_mem_'+BOARD+NAME_STRING_ADD+'.txt', "a"), 
			open('plain_udp_l2_mem_'+BOARD+NAME_STRING_ADD+'.txt', "a"), 

			open('posix_ip_l2_mem_'+BOARD+NAME_STRING_ADD+'.txt', "a"), 
			open('gnrc_conn_ip_l2_mem_'+BOARD+NAME_STRING_ADD+'.txt', "a"), 
			open('plain_ip_l2_mem_'+BOARD+NAME_STRING_ADD+'.txt', "a"), 

			open('posix_udp_ip_mem_'+BOARD+NAME_STRING_ADD+'.txt', "a"), 
			open('gnrc_conn_udp_ip_mem_'+BOARD+NAME_STRING_ADD+'.txt', "a"), 
			open('plain_udp_ip_mem_'+BOARD+NAME_STRING_ADD+'.txt', "a"), 

			open('posix_ip_ip_mem_'+BOARD+NAME_STRING_ADD+'.txt', "a"), 
			open('gnrc_conn_ip_ip_mem_'+BOARD+NAME_STRING_ADD+'.txt', "a"), 
			open('plain_ip_ip_mem_'+BOARD+NAME_STRING_ADD+'.txt', "a"), 
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


in_run = False

loopback_mode_vec = [0, 1]; # 0 = l2 loopback 1: ipv6 loopback
loopback_mode_vec_str=['L2Reflector', 'IPLoopback'];



number_of_measurements = len(loopback_mode_vec) * len(path_vec)
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
#for k in range(0,1): # loopback modes ip and l2

	myenv = dict(os.environ) 
	myenv["CFLAGS"] = ('-DNUM_PACKETS='+str(NUM_PACKETS)+' -DMIN_PACKET_SIZE='+str(MIN_PACKET_SIZE)+
	' -DMAX_PACKET_SIZE='+str(MAX_PACKET_SIZE)+' -DSTEP_SIZE='+str(STEP_SIZE))
	myenv["LOOPBACK_MODE"] = str(loopback_mode_vec[k]);
	myenv["BOARD"] = BOARD;

	for x in range(0,len(path_vec)): # measureing posix, conn and plain for udp and/or IP APIs
	#for x in range(0,1): # measureing posix, conn and plain for udp and/or IP APIs

		measurements_counter+=1

		print '### Starting measurement ' +str(measurements_counter)+ ' of ' +str(number_of_measurements)+ ' ###'

		os.chdir(path_vec[x])
		print os.getcwd()
		# Clean build environement by interacting with shell
		subprocess.call(['rm -rf bin/'], shell=True)

		# Pass the modified environment to the subprocess.
		myproc = subprocess.call(["make iotlab-exp"], shell = True, env=myenv)

		copyfile(path_vec[x]+'/bin/'+BOARD+'/'+app_vec[x]+'.elf', '../elf_files/'+app_vec[x]+'_' +loopback_mode_vec_str[k]+ '.elf');
		debug_string = 'Path: '+path_vec[x]+' ' +loopback_mode_vec_str[k]+' Board: '+BOARD
		print debug_string+'\n'



print 'FINISHED ALL'
