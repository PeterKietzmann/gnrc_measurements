#!/usr/bin/env python

import os, signal, sys, subprocess, serial, time
from pexpect import spawn, TIMEOUT, EOF

###################### SET PARAMETERTS ######################
NUM_PACKETS = 2000;
MIN_PACKET_SIZE = 10;
MAX_PACKET_SIZE = 1211;
STEP_SIZE = 100;

DELAY_PACKET_US = 0;
DELAY_SIZE_US = 0;

#BOARD='native';
BOARD='iotlab-m3';
if BOARD == 'native':
	board_switch = 0
else:
	board_switch = 1

#LOOPBACK_MODE = 0; # 0 = l2 loopback 1: ipv6 loopback

###################### xxxxxxxxxxxxxx ######################

subprocess.call(['rm py_config.txt'], shell=True)
text_config = open("py_config.txt", "w")

# write experiment configuration to text file
text_config.write('NUM_PACKETS '+str(NUM_PACKETS)+'\n')
text_config.write('MIN_PACKET_SIZE '+str(MIN_PACKET_SIZE)+'\n')
text_config.write('MAX_PACKET_SIZE '+str(MAX_PACKET_SIZE)+'\n')
text_config.write('STEP_SIZE '+str(STEP_SIZE)+'\n')
text_config.write('DELAY_PACKET_US '+str(DELAY_PACKET_US)+'\n')
text_config.write('DELAY_SIZE_US '+str(DELAY_SIZE_US)+'\n')
text_config.write('BOARD '+str(board_switch)+' \n')
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


subprocess.call(['rm ip_all.txt'], shell=True)
subprocess.call(['rm ip_mean.txt'], shell=True)
subprocess.call(['rm ip_mean_inc.txt'], shell=True)
subprocess.call(['rm l2_all.txt'], shell=True)
subprocess.call(['rm l2_mean.txt'], shell=True)
subprocess.call(['rm l2_mean_inc.txt'], shell=True)

text_files = [open("l2_all.txt", "a"), open("l2_mean.txt", "a"), open("l2_mean_inc.txt", "a"), 
			open("ip_all.txt", "a"), open("ip_mean.txt", "a"), open("ip_mean_inc.txt", "a")];


if BOARD == 'native':
	port = sys.stdin
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


if BOARD == 'iotlab-m3':
	try: 
		port.open()

	except Exception, e:

		print "error open serial port: " + str(e)

		exit()


print "Successfully opened port"

path_vec = [];
path_vec.append("/home/kietzmann/Dokumente/RIOT_gnrc_measurements/experiments/posix_udp");
path_vec.append("/home/kietzmann/Dokumente/RIOT_gnrc_measurements/experiments/gnrc_conn_udp");
path_vec.append("/home/kietzmann/Dokumente/RIOT_gnrc_measurements/experiments/plain_udp");


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

			# Pass the modified environment to the subprocess.
			subprocess.check_call(["make"], env=myenv)

			if BOARD == 'native':
				print 'now make the term\n'
				#signal.signal(signal.SIGUSR1, handler)
				#signal.alarm(2)
				#subprocess.call(['BOARD=native make term'], shell=True)

			else:
				# Flash to MCU by interactiong with shell
				subprocess.call(['make flash'], shell=True)


			print 'waiting for main and then continue'


			if port.readline(4) == 'main':
				port.readline()
				in_run = True

			while (in_run):
				c = port.readline()

				if c != 'DONE\n':
					print(c)
					text_files[(y +(k*3))].write(c)
				else:
					print 'finished run'
					in_run = False
					text_files[(y +(k*3))].write('\n')
			# !in_run
		print 'end  3 progs'

		time.sleep(1)

	print 'end 3 modes'
print 'end two loopback modes'

port.close();    # Just call this in the last iteration!
text_files[0].close()# Just call this in the last iteration!
text_files[1].close()
text_files[2].close()