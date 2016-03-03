#!/usr/bin/env python

import os, signal, sys, subprocess, serial, time
from pexpect import spawn, TIMEOUT, EOF

###################### SET PARAMETERTS ######################

DELAY_PACKET_US = 0;
DELAY_SIZE_US = 0;

#BOARD='native';
#BOARD='samr21-xpro';
BOARD='iotlab-m3';
#BOARD='nucleo-l1';
#BOARD='stm32f4discovery';


NAME_STRING_ADD = '_V2';
#NAME_STRING_ADD = '';


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

loopback_mode_vec = [0, 1]#, 1]; # 0 = l2 loopback 1: ipv6 loopback 


payload_vec = np.arange(10, 31, 10)

number_of_measurements = len(loopback_mode_vec) * len(path_vec) * len(payload_vec)
measurements_counter = 0;

for k in range(0,len(loopback_mode_vec)): # loopback modes ip and l2
	for y in range(0,len(payload_vec)):

		# Make a copy of the environment and modify that.
		myenv = dict(os.environ) 
		myenv["CFLAGS"] = ('-DPACKET_SIZE='+str(payload_vec(y))+' -DLOOPBACK_MODE='+str(loopback_mode_vec[k]) ' ')

		myenv["BOARD"] = BOARD

		for x in range(0,len(path_vec)): # measureing posix, conn and plain for udp and/or IP APIs

			measurements_counter+=1

			print '### Starting measurement ' +str(measurements_counter)+ ' of ' +str(number_of_measurements)+ ' ###'

			os.chdir(path_vec[x])
			print os.getcwd()
			# Clean build environement by interacting with shell
			subprocess.call(['rm -rf bin/'], shell=True)

			# Pass the modified environment to the subprocess.
			subprocess.check_call(["make"], env=myenv)

			if BOARD == 'native':
				myproc = subprocess.Popen(native_elf_vec[x], stdout=subprocess.PIPE)

			else:
				# Flash to MCU by interactiong with shell
				subprocess.call(['make flash'], env=myenv, shell=True)

				string = print_loopback_mode[k]+' '+payload_vec(y)+' '+path_vec[x]+'\n'
				print string

			while(1):
				if BOARD != 'native':
					c = port.readline().strip()
					print c
				else:
					c = myproc.stdout.readline().strip()

				if c != 'DONE' and in_run:
					#print(c)
					#text_files[(y +(k*3))+switch_API_udp_ip].write(c+'\n')
					text_files[(k*len(path_vec))+x].write(c+'\n')

				if c == 'START':
					print 'START identified'
					in_run = True
					#string = print_loopback_mode[k]+' '+print_mean_mode[y]+' '+path_vec[x]+'\n'
					#text_files[(y +(k*3))+switch_API_udp_ip].write(string) #

				if c == 'DONE':
					print 'DONE identified'
					in_run = False
					#text_files[(y +(k*3))+switch_API_udp_ip].write('\n')
					text_files[(k*len(path_vec))+x].write(c+'\n')
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

for a in range (0, len(text_files)):
	text_files[a].close()

print 'FINISHED ALL'
