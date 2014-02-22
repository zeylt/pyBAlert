#########################################################################
#	PyABM.py
#	This is a python wrapper to communicate with the SDK provided by Advanced
#	Brain Monitoring (ABM) inc. 
#
#	See testPyX24.py for usage examples
#
#	Only some of the functions defined in ABM's SDK are used here. To make use of other
#	functions, follow the format seen here and refer to 'B-Alert Programmers Manual.pdf'
#
#	Author: Tim Zeyl, August 2012
#########################################################################

from ctypes import *

MAX_PATH = 260
ARRAY_MAX_PATH = c_char * MAX_PATH
ARRAY256 = c_char * 256

##########################################################################
### Error Codes
ERRCODE = {'ABM_ERROR_SDK_ACQUISITION_STOPPED'					: 100,
           'ABM_ERROR_SDK_NO_DATA_ARRIVING'						: 101,
           'ABM_ERROR_SDK_CREATE_MAIN_WINDOW_FAILED'    		: 110,
           'ABM_ERROR_SDK_COULDNT_FIND_DEVICE'        			: 120,
           'ABM_ERROR_SDK_COULDNT_CONNECT_DEVICE'            	: 121,
           'ABM_ERROR_SDK_COULDNT_START_REALTIME'               : 150,
           'ABM_ERROR_SDK_COULDNT_START_SAVING'					: 151,
           'ABM_ERROR_SDK_COULDNT_STOP_REAL_TIME'              	: 170,
           'ABM_ERROR_SDK_COULDNT_LOAD_CHANNEL_MAP'             : 180,
           'ABM_ERROR_SDK_WRONG_SESSION_TYPE'    				: 190,
           'ABM_ERROR_SDK_WRONG_INPUT_SETTINGS'   				: 191,
           'ABM_ERROR_SDK_WRONG_FILE_PATHS'      				: 192,
           'ABM_ERROR_SDK_CLASSIFICATION_INIT_FAILED'         	: 193,
           'ABM_ERROR_SDK_COULDNT_CLOSE_CONNECTION'          	: 194,
           'ABM_ERROR_SDK_NOTSET_DEFFILE'              			: 195,
           'ABM_ERROR_SDK_WRONG_DESTPATH'                		: 196,
           'ABM_ERROR_SDK_TOO_LARGE_MISSED_BLOCK'        		: 197}

INITSESS = {}

############################################################################
### Custom Exceptions for communicating with ABM device
class NoDevice(Exception):
	def __init__(self,value):
		self.value = value
	def __str__(self):
		return repr(self.value)

class Wronglen(Exception):
	def __init__(self,value):
		self.value = value
	def _str__(self):
		return repr(self.value)
	
#############################################################################
### Custom structures

# structure for returning device info
class DEVICE_INFO(Structure):
	_fields_=[("chDeviceName",ARRAY256),
			  ("nCommPort",c_int),
			  ("nECGPos",c_int),
			  ("nNumberOfChannel",c_int),
			  ("nESUType",c_int),
			  ("nTymestampType",c_int),
			  ("nDeviceHandle",c_int),
			  ("chDeviceID",ARRAY_MAX_PATH)]

##############################################################################
### Class for communicating the ABM SDK
# This Class defines functions for calling the DLL defined functions
class ABMHandler:
	def __init__(self):
		self.abmDLL = windll.ABM_Athena		# Connect to main ABM DLL, use 'windll' instead of 'cdll'

	## GetDeviceInfo(self):
	# Checks whether ABM device is properly connected to ABM receiver. 
	# Returns information about the connected device.
	# Format:
	# _DEVICE_INFO* GetDeviceInfo();
	# Input Arguments:
	# None
	#Output Arguments:
	#	1. Type: Pointer to _DEVICE_INFO
	#		typedef struct _DEVICE_INFO {
	#			char chDeviceName[256]; //Device Serial/Type
	#			int nCommPort; //COM Port Number
	#			int nECGPos; //Position of EKG Channel(0=1st channel)
	#			int nNumberOfChannel; //Number of Channels
	#			int nESUType; //Type of Receiver (Single-Channel=1/Multi-Channel=0)
	#			int nTymestampType; //Type of Timestamp (System time=1 / ESU time=0)
	#			int nDeviceHandle; //Reserved
	#			char chDeviceID[MAX_PATH]; //Reserved
	#		}
	def GetDeviceInfo(self):
		getDevInfo = self.abmDLL.GetDeviceInfo
		getDevInfo.argtypes = None
		getDevInfo.restype = POINTER(DEVICE_INFO)
 		info = getDevInfo(None)
		if info.contents.nNumberOfChannel == -1:
			raise NoDevice(info.contents.nNumberOfChannel)
		return info.contents

	## SetDestinationFile(self):
	# Informs SDK the path and name of the data file(s).
	# Format:
	# Int SetDestinationFile(char* pDestinationFile)
	# Input Arguments:
	# 	1. Type: char*
	#		pDestinationFile: Full (absolute) path to destination file
	# Output Arguments:
	#	1. Type: int
	#		TRUE //Path was successfully set
	#		FALSE //Failed
	def SetDestinationFile(self,path):
		c_path = c_char_p(path)
		return self.abmDLL.SetDestinationFile(c_path)

	## InitSession(self):
	#	Description:
	#		Initializes SDK to begin a NEW session.
	#	Format:
	#		Int InitSession (int nDeviceType,int nSessionType,int nSelectedDeviceHandle,
	#		BOOL bPlayEBS)
	#	Input Arguments:
	#		1. Type: int
	#			nDeviceType : informs SDK which device configuration to use
	#			Values: ABM_DEVICE_X10Standard [0], ABM_DEVICE_X4APPT [2], ABM_DEVICE_X4BAlert [4], ABM_DEVICE_X24Standard [5]
	#		2. Type: int
	#			nSessionType: informs SDK which session configuration to use
	#			Values: ABM_SESSION_RAW [0] //For RAW & RAW-PSD data
	#			ABM_SESSION_DECON [1] //Additional DECON, DECON-PSD data
	#			ABM_SESSION_BSTATE [2] //Additional Brain State Classification data
	#			ABM_SESSION_WORKLOAD [3] //Additional B-Alert Workload data
	#		3. Type: int
	#			nSelectedDeviceHandle
	#			Value: -1 //Reserved
	#		4. Type: bool
	#			bPlayEBS
	#	Output Arguments:
	#		1. Type: int
	#			INIT_SESSION_OK //Session successfully initiated
	#			INIT_SESSION_NO //Session initiation failed
	#			ID_WRONG_SEQUENCY_OF_COMMAND //command was ignored
	#	PseudoCode:
	#		If (InitSession (ABM_DEVICE_X10Standard, ABM_SESSION_RAW, -1, 0) == INIT_SESSION_OK)
	#			//success
	#		else
	#			//failed
	def InitSession(self,nDeviceType,nSessionType,nSelectedDeviceHandle,PlayEBS):
		bPlayEBS = c_bool(PlayEBS)
		InitSess = self.abmDLL.InitSession
		InitSess.argtypes = [c_int,c_int,c_int,c_bool]
		return InitSess(nDeviceType,nSessionType,nSelectedDeviceHandle,bPlayEBS)

	## StartAcquisition
	#	Description:
	#		Sends START command to ABM device to begin acquisition of data. The SDK will create and start filling the output data files after this function is executed successfully.
	#	Format:
	#		Int StartAcquisition();
	#	Input Arguments:
	#		None
	#	Output Arguments:
	#		1. Type: int
	#			ACQ_STARTED_OK //Acquisition started
	#			ACQ_STARTED_NO //Acquisition failed
	#			ID_WRONG_SEQUENCY_OF_COMMAND // command was ignored
	#	PseudoCode:
	#		If (StartAcquisition() == ACQ_STARTED_OK)
	#			//success
	#		else
	#			//failed
	def StartAcquisition(self):
		return self.abmDLL.StartAcquisition()

	## PauseAcquisition
	#	Description:
	#		Sends PAUSE command to the ABM device and temporarily stops acquisition of data. The client program should call ResumeAcquisition in order to restart data acquisition.
	#	Format:
	#		Int PauseAcquisition();
	#	Input Arguments:
	#		None
	#	Output Arguments:
	#		1. Type: int
	#			ACQ_PAUSED_OK //Acquisition paused
	#			ACQ_PAUSED_NO //Failed
	#			ID_WRONG_SEQUENCY_OF_COMMAND // command was ignored
	#	PseudoCode:
	#		If (PauseAcquisition() == ACQ_PAUSED_OK)
	#			//success
	#		else
	#			//failed
	def PauseAcquisition(self):
		return self.abmDLL.PauseAcquisition()

	## ResumeAcquisition
	#	Description:
	#		Sends RESUME command to ABM device and restarts data acquisition.
	#	Format:
	#		Int ResumeAcquisition();
	#	Input Arguments:
	#		None
	#	Output Arguments:
	#		1. Type: int
	#			ACQ_RESUMED_OK //Acquisition resumed
	#			ACQ_RESUMED_NO //Failed
	#			ID_WRONG_SEQUENCY_OF_COMMAND // command was ignored
	#	PseudoCode:
	#		If (ResumeAcquisition() == ACQ_RESUMED_OK)
	#			//success
	#		else
	#			//failed
	def ResumeAcquisition(self):
		return self.abmDLL.ResumeAcquisition()

	## StopAcquisition
	#	Description:
	#		Sends STOP command to ABM device and stops acquisition of data. This function resets the parameters in the SDK, thus the client program should initiate a new session prior to re-invoking StartAcquisition after this function is called.
	#	Format:
	#		Int StopAcquisition();
	#	Input Arguments:
	#		None
	#	Output Arguments:
	#		1. Type: int
	#			ACQ_STOPPED_OK //Acquisition stopped
	#			ACQ_STOPPED_NO //Failed
	#			ID_WRONG_SEQUENCY_OF_COMMAND // command was ignored
	#	PseudoCode:
	#		If (StopAcquisition() == ACQ_STOPPED_OK)
	#			//success
	#		else
	#			//failed
	def StopAcquisition(self):
		return self.abmDLL.StopAcquisition()

	## GetRawData
	#	Description:
	#		Gets raw data samples from the SDK.
	#	Format:
	#		float* GetRawData ( int& nCount )
	#	Input Arguments:
	#		1. Type: Address to int
	#			nCount: updated with the number of samples returned in the output argument
	#	Output Arguments:
	#		1. Type: float*
	#			Pointer to array of float values containing raw data samples. The size of the return array = (nChannel+6)*nCount, where, nChannel is the number of channels in the ABM device (see GetPacketChannelNmbInfo), nCount is the number of samples acquired. The number of samples will vary based on the delay between successive calls to the function.
	#	PseudoCode:
	#		int nCount;
	#		float *pData;
	#		pData = GetRawData(nCount);	
	def GetRawData(self):
		nCount = c_int()
		getData = self.abmDLL.GetRawData
		getData.restype = POINTER(c_float)
		pData = getData(byref(nCount))
		return (pData,nCount)

	## GetFilteredData
	#	Description:
	#		Gets filtered physiological data samples (EEG & EKG) from the SDK.
	#	Format:
	#		float* GetFilteredData ( int& nCount )
	#	Input Arguments:
	#		1. Type: Address to int
	#			nCount: updated with the number of epochs returned in the output argument
	#	Output Arguments:
	#		1. Type: float*
	#		Pointer to array of float values containing filtered data samples. The size of the return array = (nChannel+6)*nCount, where, nChannel is the number of channels in the ABM device (see GetPacketChannelNmbInfo), nCount is the number of samples. The number of samples will vary based on the delay between successive calls to the function.
	#	PseudoCode:
	#		int nCount;
	#		float *pData;
	#		pData = GetRawData(nCount);
	def GetFilteredData(self):
		nCount = c_int()
		getData = self.abmDLL.GetFilteredData
		getData.restype = POINTER(c_float)
		pData = getData(byref(nCount))
		return (pData,nCount)

	## GetDeconData
	#	Description:
	#		Gets artifacts decontaminated data samples from the SDK.
	#	Format:
	#		float* GetDeconData ( int& nCount )
	#	Input Arguments:
	#		1. Type: Address to int
	#		nCount: updated with the number of epochs returned in the output argument
	#	Output Arguments:
	#		1. Type: float*
	#		Pointer to array of float values containing decontaminated data samples. The size of the return array = (nChannel+6)*nCount, where, nChannel is the number of channels in the ABM device (see GetPacketChannelNmbInfo), nCount is the number of samples. The number of samples may vary based on the delay between t successive calls to the function.
	#	PseudoCode:
	#		int nCount;
	#		float *pData;
	#		pData = GetDeconData(nCount);
	def GetDeconData(self):
		nCount = c_int()
		getData = self.abmDLL.GetDeconData
		getData.restype = POINTER(c_float)
		pData = getData(byref(nCount))
		return (pData,nCount)

	## GetTimeStampsStreamData
	#	Description:
	#		Returns timestamps for raw and processed data samples.
	#	Format:
	#		unsigned char* GetTimeStampsStreamData(int nType);
	#	Input Arguments:
	#		1. Type: Address to int
	#			nType: Timestamps of the following data are supported
	#			TIMESTAMP_RAW (0)
	#			TIMESTAMP_PSD (1)
	#			TIMESTAMP_DECON (2)
	#			TIMESTAMP_CLASS(3)
	#			TIMESTAMP_EKG (4)
	#	Output Arguments:
	#		1. Type: Pointer to unsigned char*
	#			Array of bytes containing 4-byte timestamps each (high byte first). Note that the array may have multiple timestamps, depending on the interval between two successive calls.
	#	PseudoCode:
	#		int nType;
	#		unsigned char *pucTSData;
	#		pucTSData = GetTimeStampsStreamData(nType);
	def GetTimeStampsStreamData(self,nType):
		getTime = self.abmDLL.GetTimeStampsStreamData
		getTime.restype = POINTER(c_ubyte)
		pChar = getTime(nType)
		return pChar

	## GetCurrentSDKMode
	#	Description:
	#		Returns the current operating mode of SDK
	#	Format:
	#		int GetCurrentSDKMode();
	#	Input Arguments:
	#		None.
	#	Output Arguments:
	#		1. Type: int
	#			Integer value representing working modes of the SDK:
	#			SDK_WAITING_MODE (-1)
	#			SDK_NORMAL_MODE (0)
	#			SDK_IMPEDANCE_MODE (1)
	#			SDK_TECHNICALMON_MODE (2)
	#	PseudoCode:
	#		int nMode;
	#		nMode = GetCurrentSDKMode();
	def GetCurrentSDKMode(self):
		return self.abmDLL.GetCurrentSDKMode()

	## GetThirdPartyData
	#	Description:
	#		Returns third party data acquired using ABM Multi-Channel External Sync Unit (MC-ESU).
	#	Format:
	#		unsigned char* GetThirdPartyData(int& nSize);
	#   Input Arguments:
	#	    1. Type: Address to int
	#		nBytes updates with the number of bytes returned
	#	Output Arguments:
	#		1. Type: Pointer to unsigned char*
	#		Array of bytes containing third party packets (packet number = nsize). Each
	#		Packet has the following format:
	#		Flag (0x56,0x5A) 	- 2bytes
	#		Message Counter     - 1 byte (reserved)
	#		ESU timestamp		- 4 bytes
	#		Packet Length 		- 2 bytes
	#		Packet Type 		- 1 byte
	#		Third Party Data 	- bytes = Packet Length
	#		Checksum 			- 1 byte
	#	Pseudocode:
	#		int nSize;
	#		unsigned char *pucTPData;
	#		pucTPData = GetThirdPartyData(nSize);
	def GetThirdPartyData(self):
		nBytes = c_int()
		getTpy = self.abmDLL.GetThirdPartyData
		getTpy.restype = POINTER(c_ubyte)
		pChar = getTpy(byref(nBytes))
		return (pChar,nBytes)

