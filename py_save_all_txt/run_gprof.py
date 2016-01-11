#!/usr/bin/env python

import os, signal, sys, subprocess, serial, time, shlex
from pexpect import spawn, TIMEOUT, EOF

###################### SET PARAMETERTS ######################
NUM_PACKETS = 1;
MIN_PACKET_SIZE = 10;
MAX_PACKET_SIZE = 1211;
STEP_SIZE = 10;

DELAY_PACKET_US = 0;
DELAY_SIZE_US = 0;

BOARD='native';
#BOARD='iotlab-m3';
if BOARD == 'native':
	board_switch = 0
else:
	board_switch = 1

#LOOPBACK_MODE = 0; # 0 = l2 loopback 1: ipv6 loopback

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
#text_config.write('LOOPBACK_MODE '+str(LOOPBACK_MODE)+' \n')

text_config.close()

print 'NUM_PACKETS = ', NUM_PACKETS
print 'MIN_PACKET_SIZE = ', MIN_PACKET_SIZE
print 'MAX_PACKET_SIZE = ', MAX_PACKET_SIZE
print 'STEP_SIZE = ', STEP_SIZE
print 'DELAY_PACKET_US = ', DELAY_PACKET_US
print 'DELAY_SIZE_US = ', DELAY_SIZE_US
print 'BOARD = ', BOARD
#print 'LOOPBACK_MODE = ', LOOPBACK_MODE


subprocess.call(['rm ip_all_'+str(NUM_PACKETS)+'_'+BOARD+'.txt'], shell=True)
subprocess.call(['rm ip_mean_'+str(NUM_PACKETS)+'_'+BOARD+'.txt'], shell=True)
subprocess.call(['rm ip_mean_inc_'+str(NUM_PACKETS)+'_'+BOARD+'.txt'], shell=True)
subprocess.call(['rm l2_all_'+str(NUM_PACKETS)+'_'+BOARD+'.txt'], shell=True)
subprocess.call(['rm l2_mean_'+str(NUM_PACKETS)+'_'+BOARD+'.txt'], shell=True)
subprocess.call(['rm l2_mean_inc_'+str(NUM_PACKETS)+'_'+BOARD+'.txt'], shell=True)

text_files = [open('l2_all_'+str(NUM_PACKETS)+'_'+BOARD+'.txt', "a"), open('l2_mean_'+str(NUM_PACKETS)+'_'+BOARD+'.txt', "a"), 
			open('l2_mean_inc_'+str(NUM_PACKETS)+'_'+BOARD+'.txt', "a"), open('ip_all_'+str(NUM_PACKETS)+'_'+BOARD+'.txt', "a"), 
			open('ip_mean_'+str(NUM_PACKETS)+'_'+BOARD+'.txt', "a"), open('ip_mean_inc_'+str(NUM_PACKETS)+'_'+BOARD+'.txt', "a")];

os.chdir("../")


native_elf_vec = [];
native_elf_vec.append(os.getcwd()+"/posix_udp/bin/native/posix_udp.elf");
native_elf_vec.append(os.getcwd()+"/gnrc_conn_udp/bin/native/gnrc_conn_udp.elf");
native_elf_vec.append(os.getcwd()+"/plain_udp/bin/native/plain_udp.elf");


path_vec = [];
path_vec.append(os.getcwd()+"/posix_udp");
path_vec.append(os.getcwd()+"/gnrc_conn_udp");
path_vec.append(os.getcwd()+"/plain_udp");

in_run = False

LOOPBACK_MODE = [0, 1]; # 0 = l2 loopback 1: ipv6 loopback

for k in range(0,2): # loopback modes ip and l2
	for y in range(0,3): # kinds of measurement regarding mean calculation

		MEASURE_MEAN = y; # ToDO document!

		# Make a copy of the environment and modify that.
		myenv = dict(os.environ) 
		myenv["CFLAGS"] = ('-DNUM_PACKETS='+str(NUM_PACKETS)+' -DMIN_PACKET_SIZE='+str(MIN_PACKET_SIZE)+
		' -DMAX_PACKET_SIZE='+str(MAX_PACKET_SIZE)+' -DSTEP_SIZE='+str(STEP_SIZE)+' -DDELAY_PACKET_US='+str(DELAY_PACKET_US)+
		' -DDELAY_SIZE_US='+str(DELAY_SIZE_US)+' -DLOOPBACK_MODE='+str(LOOPBACK_MODE[k])+' -DMEASURE_MEAN='+str(MEASURE_MEAN)+' ')

		myenv["BOARD"] = BOARD

		for x in range(0,3): # measureing posix, conn and plain

			os.chdir(path_vec[x])

			# Clean build environement by interacting with shell
			subprocess.call(['rm -rf bin/'], shell=True)
			subprocess.call(['rm gmon.out'], shell=True)

			# Pass the modified environment to the subprocess.
			print 'BUILD'
			subprocess.check_call(['make all-gprof'], env=myenv, shell=True)
			time.sleep(1)

			print 'EXECUTE'
			#myproc = subprocess.Popen(native_elf_vec[x], stdout=subprocess.PIPE, shell=True)
			#myproc = os.system(native_elf_vec[x])
			myproc = subprocess.call(native_elf_vec[x], stdout=subprocess.PIPE)

			time.sleep(3)
			myproc.kill()

#			while(1):

#				c = myproc.stdout.readline().strip()

#				if c != 'DONE' and in_run:
#					#print(c)
#					text_files[(y +(k*3))].write(c+'\n')

#				if c == 'START':
#					in_run = True

#				if c == 'DONE':
#					print 'finished run'
#					in_run = False
#					text_files[(y +(k*3))].write('\n')
#					break
#			# !in_run
#			print 'KILL'
#			time.sleep(1)
#			myproc.kill()

			print 'EVAL'
			subprocess.call(['make eval-gprof'], env=myenv, shell=True)

		print 'end  3 progs'

		time.sleep(1)

	print 'end 3 modes'
print 'end two loopback modes'

text_files[0].close()# Just call this in the last iteration!
text_files[1].close()
text_files[2].close()
