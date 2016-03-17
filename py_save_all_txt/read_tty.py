#!/usr/bin/env python

import os, signal, sys, subprocess, serial, time
from pexpect import spawn, TIMEOUT, EOF

###################### SET PARAMETERTS ######################

#BOARD='native';
#BOARD='samr21-xpro';
#BOARD='arduino-due';
#BOARD='nucleo-l1';
#BOARD='arduino-due';
BOARD='iotlab-m3';
if BOARD == 'native':
	board_switch = 0
else:
	board_switch = 1


###################### xxxxxxxxxxxxxx ######################



subprocess.call(['rm read_tty.txt'], shell=True)

os.chdir("../")
path_vec = (os.getcwd()+'/plain_ip'); ########## here #################
os.chdir("py_save_all_txt/")

text_files = open( 'read_tty.txt', "a");

os.chdir("../")

if BOARD == 'native':
	native_elf_vec = [os.getcwd()+"/posix_udp/bin/native/gnrc_conn_udp.elf"];
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


try: 
	port.open()

except Exception, e:

	print "error open serial port: " + str(e)

	exit()

in_run = False

myenv = dict(os.environ) 
myenv["BOARD"] = BOARD


os.chdir("/home/kietzmann/Dokumente/RIOT_gnrc_measurements/experiments/plain_udp")
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


while(1):
	if BOARD != 'native':
		c = port.readline().strip()
		print c
	else:
		c = myproc.stdout.readline().strip()

	if c != 'DONE' and in_run:
		#print(c)
		text_files.write(c+'\n')

	if c == 'START':
		print '####################### Started run #######################'
		in_run = True

	if c == 'DONE':
		print 'Finished run'
		in_run = False
		text_files.write('\n')
		break



# !in_run
if BOARD == 'native':
	myproc.kill()


if BOARD != 'native':
	port.close();    # Just call this in the last iteration!

text_files.close()

print 'FINISHED ALL'
