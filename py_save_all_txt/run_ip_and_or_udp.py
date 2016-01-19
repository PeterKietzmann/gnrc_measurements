#!/usr/bin/env python

import os, signal, sys, subprocess, serial, time
from pexpect import spawn, TIMEOUT, EOF

###################### SET PARAMETERTS ######################
NUM_PACKETS = 1000;
MIN_PACKET_SIZE = 10;
MAX_PACKET_SIZE = 1211;
STEP_SIZE = 10;

DELAY_PACKET_US = 0;
DELAY_SIZE_US = 0;

#BOARD='native';
BOARD='iotlab-m3';
if BOARD == 'native':
	board_switch = 0
else:
	board_switch = 1


API_layer_mode = 'udp'; # udp: just run UDP layer simulations
						# ip:  just run  IP layer simulations
						# both: run  both


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


path_vec = [];

if API_layer_mode =='udp' or API_layer_mode =='ip':
	subprocess.call(['rm '+API_layer_mode+'_ip_all_'+str(NUM_PACKETS)+'_'+BOARD+'.txt'], shell=True)
	subprocess.call(['rm '+API_layer_mode+'_ip_mean_'+str(NUM_PACKETS)+'_'+BOARD+'.txt'], shell=True)
	subprocess.call(['rm '+API_layer_mode+'_ip_mean_inc_'+str(NUM_PACKETS)+'_'+BOARD+'.txt'], shell=True)
	subprocess.call(['rm '+API_layer_mode+'_l2_all_'+str(NUM_PACKETS)+'_'+BOARD+'.txt'], shell=True)
	subprocess.call(['rm '+API_layer_mode+'_l2_mean_'+str(NUM_PACKETS)+'_'+BOARD+'.txt'], shell=True)
	subprocess.call(['rm '+API_layer_mode+'_l2_mean_inc_'+str(NUM_PACKETS)+'_'+BOARD+'.txt'], shell=True)

	os.chdir("../")
	path_vec.append(os.getcwd()+'/posix_'+API_layer_mode);
	path_vec.append(os.getcwd()+'/gnrc_conn_'+API_layer_mode);
	path_vec.append(os.getcwd()+'/plain_'+API_layer_mode);
	os.chdir("py_save_all_txt/")

	text_files = [open( API_layer_mode+ '_l2_all_'+str(NUM_PACKETS)+'_'+BOARD+'.txt', "a"), open(API_layer_mode+ '_l2_mean_'+str(NUM_PACKETS)+'_'+BOARD+'.txt', "a"), 
				open(API_layer_mode+ '_l2_mean_inc_'+str(NUM_PACKETS)+'_'+BOARD+'.txt', "a"), open(API_layer_mode+ '_ip_all_'+str(NUM_PACKETS)+'_'+BOARD+'.txt', "a"), 
				open(API_layer_mode+ '_ip_mean_'+str(NUM_PACKETS)+'_'+BOARD+'.txt', "a"), open(API_layer_mode+ '_ip_mean_inc_'+str(NUM_PACKETS)+'_'+BOARD+'.txt', "a")];

if API_layer_mode =='both':
	subprocess.call(['rm *ip_all_'+str(NUM_PACKETS)+'_'+BOARD+'.txt'], shell=True)
	subprocess.call(['rm *ip_mean_'+str(NUM_PACKETS)+'_'+BOARD+'.txt'], shell=True)
	subprocess.call(['rm *ip_mean_inc_'+str(NUM_PACKETS)+'_'+BOARD+'.txt'], shell=True)
	subprocess.call(['rm *l2_all_'+str(NUM_PACKETS)+'_'+BOARD+'.txt'], shell=True)
	subprocess.call(['rm *l2_mean_'+str(NUM_PACKETS)+'_'+BOARD+'.txt'], shell=True)
	subprocess.call(['rm *l2_mean_inc_'+str(NUM_PACKETS)+'_'+BOARD+'.txt'], shell=True)

	os.chdir("../")
	path_vec.append(os.getcwd()+'/posix_udp');
	path_vec.append(os.getcwd()+'/gnrc_conn_udp');
	path_vec.append(os.getcwd()+'/plain_udp');
	path_vec.append(os.getcwd()+'/posix_ip');
	path_vec.append(os.getcwd()+'/gnrc_conn_ip');
	path_vec.append(os.getcwd()+'/plain_ip');
	os.chdir("py_save_all_txt/")

	text_files = [open('udp_l2_all_'+str(NUM_PACKETS)+'_'+BOARD+'.txt', "a"), open('udp_l2_mean_'+str(NUM_PACKETS)+'_'+BOARD+'.txt', "a"), 
				open('udp_l2_mean_inc_'+str(NUM_PACKETS)+'_'+BOARD+'.txt', "a"), open('udp_ip_all_'+str(NUM_PACKETS)+'_'+BOARD+'.txt', "a"), 
				open('udp_ip_mean_'+str(NUM_PACKETS)+'_'+BOARD+'.txt', "a"), open('udp_ip_mean_inc_'+str(NUM_PACKETS)+'_'+BOARD+'.txt', "a"),
				open('ip_l2_all_'+str(NUM_PACKETS)+'_'+BOARD+'.txt', "a"), open('ip_l2_mean_'+str(NUM_PACKETS)+'_'+BOARD+'.txt', "a"), 
				open('ip_l2_mean_inc_'+str(NUM_PACKETS)+'_'+BOARD+'.txt', "a"), open('ip_ip_all_'+str(NUM_PACKETS)+'_'+BOARD+'.txt', "a"), 
				open('ip_ip_mean_'+str(NUM_PACKETS)+'_'+BOARD+'.txt', "a"), open('ip_ip_mean_inc_'+str(NUM_PACKETS)+'_'+BOARD+'.txt', "a")];



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
	# Open serial port
	port = serial.Serial(
		port='/dev/ttyUSB1',
		baudrate=500000, 
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

loopback_mode_vec = [0, 1]; # 0 = l2 loopback 1: ipv6 loopback
print_loopback_mode = ['l2 reflector', 'ip loopback'];
measure_mean_vec = [0, 1, 2];
print_mean_mode = ['single', 'conjoint', 'increment'];

number_of_measurements = len(loopback_mode_vec) * len(measure_mean_vec) * len(path_vec)
measurements_counter = 0;

for k in range(0,2): # loopback modes ip and l2
	for y in range(0,3): # kinds of measurement regarding mean calculation

		MEASURE_MEAN = measure_mean_vec[y]; # 0: Measure each packet and save value
											# 1: Measure all packets and save value
											# 2: Measure each packet but increment all

		# Make a copy of the environment and modify that.
		myenv = dict(os.environ) 
		myenv["CFLAGS"] = ('-DNUM_PACKETS='+str(NUM_PACKETS)+' -DMIN_PACKET_SIZE='+str(MIN_PACKET_SIZE)+
		' -DMAX_PACKET_SIZE='+str(MAX_PACKET_SIZE)+' -DSTEP_SIZE='+str(STEP_SIZE)+' -DDELAY_PACKET_US='+str(DELAY_PACKET_US)+
		' -DDELAY_SIZE_US='+str(DELAY_SIZE_US)+' -DLOOPBACK_MODE='+str(loopback_mode_vec[k])+' -DMEASURE_MEAN='+str(MEASURE_MEAN)+' ')

		myenv["BOARD"] = BOARD

		for x in range(0,len(path_vec)): # measureing posix, conn and plain for udp and/or IP APIs

			measurements_counter+=1
			print '### Starting measurement ' +str(measurements_counter)+ ' of ' +str(number_of_measurements)+ ' ###'

			if ( API_layer_mode == 'both' and (len(path_vec)/2)-1 < x):
				switch_API_udp_ip = 6
			else:
				switch_API_udp_ip = 0


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
				subprocess.call(['make flash'], shell=True)

			while(1):
				if BOARD == 'iotlab-m3':
					c = port.readline().strip()
				else:
					c = myproc.stdout.readline().strip()

				if c != 'DONE' and in_run:
					#print(c)
					text_files[(y +(k*3))+switch_API_udp_ip].write(c+'\n')

				if c == 'START':
					in_run = True
					# string = print_loopback_mode[k]+' '+print_mean_mode[y]+' '+path_vec[x]+'\n'
					# text_files[(y +(k*3))+switch_API_udp_ip].write(string) #

				if c == 'DONE':
					print 'Finished run'
					in_run = False
					text_files[(y +(k*3))+switch_API_udp_ip].write('\n')
					break

				# else:
				# 	print c
				# 	text_files[(y +(k*3))+switch_API_udp_ip].write(c+'\n')

			# !in_run
			if BOARD == 'native':
				myproc.kill()

			time.sleep(1)

if BOARD == 'iotlab-m3':
	port.close();    # Just call this in the last iteration!

for a in range (0, len(text_files)):
	text_files[a].close()

print 'FINISHED ALL'
