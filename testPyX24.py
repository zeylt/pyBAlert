#########################################################################
#	testPyX24.py
#	This file tests the communication with the ABM X24 headset using the python
#	wrapper PyABM.py to interact with the SDK supplied by Advanced Brain Monitoring Inc
#
#	Acquisition is initiated and Raw values and timestamps are saved in text files
#
#	Run this code by typing 'python testPyX24.py' at the command prompt in 
#		the appropriate directory
#		- directory must contain all the .dll files supplied by ABM
#
#	See: B-Alert Programmers Manual and B-Alert User's Manual for more information
#
#	Author: Tim Zeyl, August 2012
#########################################################################

from PyABM import *	# import all classes and functions from PyABM
import time			# for pausing and such
import numpy as np  # for math operations

#########################################################################
### Set up Device communication

print "Starting ABM Handler"
ABMengine = ABMHandler()

try:
	print "Getting Device Info"
	dinfo = ABMengine.GetDeviceInfo()
	print 'Device Detected: ' + dinfo.chDeviceName	
	print 'Number of Channels: ' + str(dinfo.nNumberOfChannel)
	nCh = dinfo.nNumberOfChannel
except NoDevice as e:
	print 'No Device Detected, # of Channels = ', e.value
	exit()

##########################################################################
### Set the path where files will be saved 

### Get input from the user
## subject number
#success = None
#while not success:
#	try:
#		user_session = int(raw_input('#Enter 4-digit session number: '))
#		if len(str(user_session))!=4:
#			raise Wronglen(len(str(user_session)))
#		success = 1
#	except ValueError:
#		print 'Invalid Number'
#	except Wronglen as e:
#		print 'Wrong number of digits, you entered string of length ', e.value

## Group
#success = None
#while not success:
#	try:
#		user_group = int(raw_input('#Enter 1-digit group number: '))
#		if len(str(user_group))!=1:
#			raise Wronglen(len(str(user_group)))
#		success = 1
#	except ValueError:
#		print 'Invalid Number'
#	except Wronglen as e:
#		print 'Wrong number of digits, you entered string of length ', e.value

## Session Iteration
#success = None
#while not success:
#	try:
#		user_iter = int(raw_input('#Enter 1-digit session iteration number: '))
#		if len(str(user_iter))!=1:
#			raise Wronglen(len(str(user_iter)))
#		success = 1
#	except ValueError:
#		print 'Invalid Number'
#	except Wronglen as e:
#		print 'Wrong number of digits, you entered string of length ', e.value

## Task Type
#success = None
#while not success:
#	try:
#		user_task = int(raw_input('#Enter 2-digit task type: '))
#		if len(str(user_task))!=2:
#			raise Wronglen(len(str(user_task)))
#		success = 1
#	except ValueError:
#		print 'Invalid Number'
#	except Wronglen as e:
#		print 'Wrong number of digits, you entered string of length ', e.value

## Task Iteration
#success = None
#while not success:
#	try:
#		user_taskiter = int(raw_input('#Enter 1-digit task iteration number: '))
#		if len(str(user_taskiter))!=1:
#			raise Wronglen(len(str(user_taskiter)))
#		success = 1
#	except ValueError:
#		print 'Invalid Number'
#	except Wronglen as e:
#		print 'Wrong number of digits, you entered string of length ', e.value

user_session = '1234' # subject number
user_group   = '1' #Group
user_iter    = '1' #Session Iteration
user_task    = '12' #Task Type
user_taskiter= '1' #Task Iteration

destinationFilepath = 'C:\\ABM\\EEG\\SDK\\Output Files\\PyRecord_' + str(user_session) + str(user_group) + str(user_iter) + str(user_task) + str(user_taskiter) + '.ebs'

try:
	pathset = ABMengine.SetDestinationFile(destinationFilepath)
except ValueError:
	print 'Path was not set, Invalid path name'
	exit()

if pathset:
	print "Files will be saved in " + destinationFilepath

#################################################################################
### Initialize the session

deviceType = 3 		# Values: ABM_DEVICE_X10Standard [0], ABM_DEVICE_X4APPT [2], ABM_DEVICE_X4BAlert [4], ABM_DEVICE_X24Standard [3]
sessionType = 0		# Values: ABM_SESSION_RAW [0] //For RAW & RAW-PSD data
					#			ABM_SESSION_DECON [1] //Additional DECON, DECON-PSD data
					#			ABM_SESSION_BSTATE [2] //Additional Brain State Classification data
					#			ABM_SESSION_WORKLOAD [3] //Additional B-Alert Workload data
deviceHandle = -1	# Value: -1 //Reserved
playEBS = 0			# bPlayEBS True or False

init = -1
tries = 1
print "Initializing Session"
while init != 1 & tries < 11:
	init = ABMengine.InitSession(deviceType,sessionType,deviceHandle,playEBS)
	if init != 1:
		if tries == 10:
			print 'Could not initialize Device, quitting program'
			exit()
		print 'Initialization Unsuccessful, Try #: ' + str(tries)
		tries += 1


print "Starting Acquisition"
stat = ABMengine.StartAcquisition()
print 'Acquisition started?: ' + str(stat)
if stat == -1:
	print 'Could not start acquisition, quitting program'
	quit()

mode = ABMengine.GetCurrentSDKMode()
print 'SDK mode: ' + str(mode)

####################################################################################
### Test getting RAW data and saving to files

# Open files for writing
fpTS = open('timeStamps.txt','wb')
fpRAW = open('RAWsamps.txt','wb')

# write file headers
fpRAW.write('Epoch, Offset, Hour, Min, Sec, mSec, F3, F1, Fz, F2, F4, C3, C1, Cz, C2, C4, CPz, P3, P1, Pz, P2, P4, POz, O1, Oz, O2, EKG, AUX1, AUX2, AUX3\n')
fpTS.write('Hexidecimal, Milliseconds\n')

RAW = []	# list for carrying raw signal
TSmult = np.array([pow(2,24),pow(2,16),pow(2,8),pow(2,0)])	# For converting timestamp to milliseconds

for i in range(10):
	time.sleep(0.5)
	
	### Get Raw Data and store in 2-D list
	(rData,nCount) = ABMengine.GetRawData()
	print str(nCount.value) + ' samples drawn'
	l = 0
	for j in range(nCount.value):		# loop through each sample
		RAW.append([])					# add new list entry for this time sample
		for k in range(nCh+6):			# loop through each channel and 6 header values for each sample
			RAW[j].append(rData[l])		# append each channel value to the sub-list corresponding to current time sample
			l+=1

	### Get Time stamps and store
	pTimeStamps = ABMengine.GetTimeStampsStreamData(0)
	l = 0
	for j in range(nCount.value):
		TS = np.array([])
		for k in range(4):							# loop through 4-byte time stamp information
			fpTS.write('%02x.' % pTimeStamps[l])	# write hexidecimal value to file
			TS = np.append(TS,pTimeStamps[l])
			l+=1
		TSmsec = (TS*TSmult).sum()					# convert timestamp to milliseconds
		fpTS.write(', ' + str(TSmsec) + '\n')
			
	## Write the raw samples to a file
	for j in range(nCount.value):
		fpRAW.write(str(RAW.pop(0)).strip('[]') + '\n')

######################################################################################
### Test Pausing, Resuming and Stopping Acquisition

print "Pausing Acquisition"
stat = ABMengine.PauseAcquisition()

print "Resuming Acquisition"
stat = ABMengine.ResumeAcquisition()

fpTS.close()
fpRAW.close()

print "Stopping Acquisition"
stat = ABMengine.StopAcquisition()
print 'Acquisition Stopped?: ' + str(stat)

exit()
