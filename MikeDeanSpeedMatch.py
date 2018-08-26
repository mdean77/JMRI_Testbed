# This Script will automatically build a speed table for a decoder using OPS mode programming
#
# Summary of how it works:
#	User enters info about decoder such as address, scale, brand of decoder, top speed desired on the input panel
#	A throttle is created in JMRI to run the locomotive
#	The locomotive is warmed up for a few laps (in both directions if diesel is selected) 
#	The top speed of the locomotive is measured (in both directions for diesels)
#	Using the block detectors to measure time, it adjusts the throttle until the appropriate speed is found for the speed step
#	7 Speed steps are measured; the rest are interpolated. The measured ones are 4, 8, 12, 16, 20,24, and 28
#	These are written to the decoder and the locomotive is release from the throttle and the throttle is discarded.
#
#	If something goes wrong and you need to start over; "Steal" it in another throttle and stop the locomotive
#		Under the "Panels" tab, select "Thread Monitor" and "Kill" the script.
#		Close the input panel
#
#	Notes:
#		BEMF	Any adjustments should be made before running the script
#
#			TCS - May need to turn off BEMF since it is not adjustable. A speed jump may be present
#				and maybe very noticeable after the speedtable is created
#
#			Digitax -
#				Maximum throttle setting used should be 85% when Digitrax equipped locomotives are included in a consist.
#				163 series decoders
#					CV57 default value 6 may prevent the locomotive from going below about 5 mph
#					setting this to 33 improves this. Or turn it off by setting it to zero
#
#			NCE - some older n scale decoders will revert to 28 step mode instead of 128 step mode (this may happen in HO as well)
#
#		The locomotives speed should be approximately equivlent to what is displayed on a throttle if the maximum speed was set to 100.
#			(running by itself without a train)

# $Revision: 1.3 $ revision of AutomatonExample distributed with JMRI
#					 from which this script has been developed.
#
# Author: Phil Klein, Version 2.14 copyright 2010
#
#	Hardware tested with this script
#	Command Station - Digitrax DCS100, DCS200, DC50 
#	Train Detection - BDL168 (Board Address ????)
#	Computer Interface - Locobuffer-USB
#	Track - 12 pieces of Kato N scale 19" Radius Unitrak
#	Track - 16 pieces of Kato HO scale 21 5/8" Radius Unitrak
#	Track - 16 seconds of 42" radius flex on Free-mo Return Loop
#	I used one sensor for each piece of HO scale track
#	I used one sensor for every 2 pieces of N scale track
#	The HO & N tracks share sensors 1 - 12
#	HO Track also uses sensors 13 - 16


#	Added step list for ESU decoders
#	Added redo time measurement when start time and stop time are the same when using the MS100
#	Fixed writing values higher than 255 to the decoder
#	Fixed writing values lower than 1
#	Added STEAM to input panel to see if that accomodates tender pickup issues
#		Steam locomotives should be placed on the track so that the wheels that pick up power
#		on the tenders front truck are on the rail that is detected to reduce errors.
#	Added the ability for the user to select the top speed
#	Added "Atlas" to user selectable decoders
#	05/28/08	Added CV25 = 0 If decoder was using a predefined table, can't get accurate measurements
#	08/18/08	Fixed Atlas...should have been Atlas/Lenz XF
#	08/25/08	Added waits after writing CV's 62, 25 and 29  possible issue with Zypher not sending write CV29 command
#	08/26/08	Changed speedtable setting for testing 128 support from 120 to 84
#	09/09/08	Seperated testing for 128 support for N scale and HO scale.
#	09/09/08	Changed speedtable setting for testing 128 support for HO from 84 to 80
#	09/11/08	Add displaying of throttle setting chosen for given speed step
#	09/22/08	Added "Done != True"  to fine measurement.  Was changing throttle setting even though we were done 
#	09/22/08	Increased wait times after writing CV's before warm up  QSI decoders weren't getting all of them  was 250msec, now 500
#	01/09/09	TCS decoders would not run after initial ops mode programming
#	01/09/09	TCS decoders stall when using values above 249 
#	06/15/09	Changed Soundtraxx to Soundtraxx DCD in preparation for adding Soundtraxx Tsunami 
#	06/26/09	Added Soundtraxx Tsunami
#	08/28/09	Increased wait time when writing table from 100ms to 150ms  DZ121 was getting zero written for every other entry 
#	09/11/09	Added cycling track power before starting.
#	09/15/09	Created new list for newer TCS decoders
#	09/15/09	Created test to determine which TCS list to use
#	09/15/09	Increased wait time when measuring max speed.  Tsunami was missing direction change
#	09/15/09	Added wait time when turning on speed table.  Tsunami was missing change to CV29
#	09/17/09	Removed "Unknown" from selection list.  Getting too hard to support 
#	09/17/09	fixed throttlesetting from being set above 127 
#	09/17/09	moved comparison of hithrottle & lowthrottle into coarse measurement
#	09/18/09	added a second forward statment when measuring fwd max speed. Sometimes doesn't execute
#	05/21/10	changed getOpsModeProgrammer to getAddressedeProgrammer something changed between 2.8 and 2.9.6
#	05/21/10	warmup for steam now only goes forward
#	11/05/17	Ported to Erich Whitney's Speed Calibration Testbed (NCE and C/MRI) setup with KATO track both N and HO
#   07/07/18	Changed to cpOD Block Detectors and rewrote speed measurement code
#   08/22/18    JMD changes to version 3.0 which will be N scale only.
# 
# Memory Location Mapping
#====================================================== 
# memory1 : speed measurement 1 - no longer used
# memory2 : speed measurement 2 - no longer used
# memory3 : speed measurement 3 - no longer used
# memory4 : speed measurement 4 - no longer used
# memory5 : speed measurement 5 - no longer used
# memory6 : speed measurement 6 - no longer used
# memory7 : speed measurement 7 - no longer used
# memory8 : speed measurement 8 - no longer used
# memory9 : speed measurement 9 - no longer used
# memory10: speed measurement 10 - no longer used
# memory11: speed measurement 11 - no longer used
# memory12: speed measurement 12 - no longer used
# memory13: speed measurement 13 - no longer used
# memory14: speed measurement 14 - no longer used
# memory15: speed measurement 15 - no longer used
# memory16: speed measurement 16 - no longer used
# memory17: 
# memory18: 
# memory19: 
# memory20: direction
# memory21: reverse max speed
# memory22: forward max speed
# memory23: decoder brand
# memory24: target speed
# memory25: current step in the algorithm (text)

import java
import javax.swing
import jmri

####################################################################################
#
# Create an instance of the AbstractAutomation class 
#
####################################################################################	
class DCCDecoderCalibration(jmri.jmrit.automat.AbstractAutomaton) :
	
####################################################################################
#
# self.init() called exactly once at the startup to do any necessary configuration
#
####################################################################################	
	def init(self) :
	    # individual block section length (scale feet)
		self.scriptversion = 3.0
		self.block = float(132.65)  # 132.65 feet Erich's Speed Matching Track Kato Unitrack 19" Radius - 12 Sections / 24 Pieces
		self.NumSpeedMeasurements = 5
		self.long = False
		self.addr = 0
		self.warmupLaps = 5
		self.programmer = None
		self.throttle = None
		self.writeLock = False
		self.fullSpeed = 100

		# JMD:  I changed the sensor numbering since I will only have 12 blocks.
		self.sensor1 = sensors.provideSensor("Block:1")
		self.sensor2 = sensors.provideSensor("Block:2")
		self.sensor3 = sensors.provideSensor("Block:3")
		self.sensor4 = sensors.provideSensor("Block:4")
		self.sensor5 = sensors.provideSensor("Block:5")
		self.sensor6 = sensors.provideSensor("Block:6")
		self.sensor7 = sensors.provideSensor("Block:7")
		self.sensor8 = sensors.provideSensor("Block:8")
		self.sensor9 = sensors.provideSensor("Block:9")
		self.sensor10 = sensors.provideSensor("Block:10")
		self.sensor11 = sensors.provideSensor("Block:11")
		self.sensor12 = sensors.provideSensor("Block:12")
		self.homesensor = sensors.provideSensor("Block:12")
		
		
		self.memory1 = memories.provideMemory("1")
		self.memory2 = memories.provideMemory("2")
		self.memory3 = memories.provideMemory("3")
		self.memory4 = memories.provideMemory("4")
		self.memory5 = memories.provideMemory("5")
		self.memory6 = memories.provideMemory("6")
		self.memory7 = memories.provideMemory("7")
		self.memory8 = memories.provideMemory("8")
		self.memory9 = memories.provideMemory("9")
		self.memory10 = memories.provideMemory("10")
		self.memory11 = memories.provideMemory("11")
		self.memory12 = memories.provideMemory("12")
		self.memory13 = memories.provideMemory("13")
		self.memory14 = memories.provideMemory("14")
		self.memory15 = memories.provideMemory("15")
		self.memory16 = memories.provideMemory("16")
		self.memory20 = memories.provideMemory("20")
		self.memory21 = memories.provideMemory("21")
		self.memory22 = memories.provideMemory("22")
		self.memory23 = memories.provideMemory("23")
		self.memory24 = memories.provideMemory("24")
		self.memory25 = memories.provideMemory("25")

		# Different block sizes for different speeds or it would take
		# forever to do the low speed if loco had to circle whole track
		# for every measurement.

		self.HighSpeedNBlocks = 12
		self.MediumSpeedNBlocks = 3		
		self.LowSpeedNBlocks = 1

		self.HighSpeedArrayN = [self.homesensor]

		self.MediumSpeedArrayN= (
				self.sensor1,
				self.sensor4,
				self.sensor7,
				self.sensor10)

		self.LowSpeedArrayN = (
				self.sensor1,
				self.sensor2,
				self.sensor3,
				self.sensor4,
				self.sensor5,
				self.sensor6,
				self.sensor7,
				self.sensor8,
				self.sensor9,
				self.sensor10,
				self.sensor11,
				self.sensor12)
				
		self.MediumSpeedThreshold = 45
		self.HighSpeedThreshold = 85
		
		self.DecoderMap = {141:"Tsunami", 129:"Digitrax", 153:"TCS", 11:"NCE", 113: "QSI/BLI", 99:"Lenz Gen 5", 151:"ESU", 127:"Atlas/Lenz XF"}
		self.DecoderType = "Default"

		#	These speed steps are measured.  All others are calculated
		#	CV			70	74	78	82	86	90	94
		#	Speedsteps	 4	 8	12	16	20	24	28

		#	These lists are percentages of full speed
		self.DigitraxStepList = [10, 22, 35, 47, 60, 72, 85]
		self.Lenz5GenStepList = [17, 30, 44, 57, 71, 84, 98]
		self.LenzXFStepList = [11, 26, 40.5, 55, 70, 84, 98.5]
		self.NCEStepList = [10.5, 25, 39.5, 54,	68,	83,	98]
		self.OldTCSStepList = [14.5, 28.5, 42.5, 57, 71.5, 86, 99]
		self.NewTCSStepList = [13, 25.5, 38, 50.5, 63, 75.5, 88]
		self.QSIStepList = [11,	26,	41,	55,	70,	85,	99]
		self.SoundtraxxDSDStepList = [14,	28,	42,	56,	70,	84,	99]
		self.TsunamiStepList = [14.5,	28.5,	42.5,	57,	71,	85,	99]
		self.ESUStepList = [12,	27,	41,	56,	70,	85,	99]
		return

####################################################################################
#
# self.myCVListener() Provides an acknowledgement after a CV write operation
#
####################################################################################	
	def myCVListener(self, value, status) :
		self.writeLock = False
		return
####################################################################################
#
# self.testbedWriteCV() Wraps the ops writes with a post write delay to give time
# for the listener to respond
#
####################################################################################	
	def testbedWriteCV(self, cv, value) :
		self.writeLock = True
		self.programmer.writeCV(cv, value, self.myCVListener)
		while (self.writeLock) :	# will be set to False by myCVListener()
			pass
		return
####################################################################################
#
# self.LoopActive() Returns true if there is a locomotive detected on the loop
# JMD revised this to loop through all the sensors and if any of them is active,
# then there is a locomotive on the track.
#
####################################################################################	
	def LoopActive(self) :
		retval = False
		for blockSensor in self.lowSpeedArrayN:
			if (blockSensor.getKnownState() == CLOSED) :
				retval = True
		return retval			

####################################################################################
#
# self.DCCSourceSelect() configures the testbed DCC input to main or program
#
####################################################################################	
	def DCCSourceSelect(self, Source):
		if (Source == "MAIN") :
			print ("Testbed Track MAIN Selected")
			turnouts.provideTurnout("ProgMain").setState(CLOSED)
			pass
		elif (Source == "PROG") :
			print ("Testbed Track PROG Selected")
			turnouts.provideTurnout("ProgMain").setState(THROWN)
			pass
		else :
			print ("Please select either 'MAIN' or 'PROG'")
			pass
		return
####################################################################################
#
# self.SWLed() controls the testbed software-controlled LEDs on/off
#
####################################################################################	
	def SWLed(self, Led, Value):
		if (Led == "WHT") :
			if (Value == "ON") :
				print ("Testbed White Software LED On")
				turnouts.provideTurnout("SWLEDWHT").setState(CLOSED)
				pass
			elif (Value == "OFF") :
				print ("Testbed White Software LED Off")
				turnouts.provideTurnout("SWLEDWHT").setState(THROWN)
				pass
			else :
				print ("Please select either 'ON' or 'OFF'")
				pass
		elif (Led == "BLU") :
			if (Value == "ON") :
				print ("Testbed Blue Software LED On")
				turnouts.provideTurnout("SWLEDBLU").setState(CLOSED)
				pass
			elif (Value == "OFF") :
				print ("Testbed Blue Software LED Off")
				turnouts.provideTurnout("SWLEDBLU").setState(THROWN)
				pass
			else :
				print ("Please select either 'ON' or 'OFF'")
				pass
		else :
			print ("Please select either 'WHT' or 'BLU' Led")
			pass
		return
####################################################################################
#
# self.TrackNormal() configures the testbed to turn the main DCC power to both loops
#
####################################################################################	
	def TrackNormal(self):
		self.DCCSourceSelect("MAIN")
		self.waitMsec(500)
		return
####################################################################################
#
# self.TrackProgram() configures the testbed to select the DCC program on both loops
#
####################################################################################	
	def TrackProgram(self):
		self.DCCSourceSelect("PROG")
		self.waitMsec(500)
		return
####################################################################################
#
# self.waitNextActive() configures the testbed to turn the main DCC power to both loops
#
####################################################################################	
	def waitNextActiveSensor(self, sensorlist) :
		inactivesensors = []
		
		if (len(sensorlist) == 1) :
			if (sensorlist[0].getKnownState() == sensorlist[0].ACTIVE) :
				self.waitSensorInactive(sensorlist)
			inactivesensors.append(sensorlist[0])
		else :
			for s in sensorlist:
				if s.getKnownState() == s.INACTIVE :
					inactivesensors.append(s)
		self.waitSensorActive(inactivesensors)
		return
####################################################################################
#
# self.measureTime() is used as part of the speed measurement
#
# This has been rewritten to first get the set of only the inactive sensors then
# wait just on a list of those sensors until one of them goes active.
#
# This should eliminate the false triggering of the block sensors that have a long
# timeout delay when they go from active to inactive.
#
####################################################################################
	def measureTime(self, sensorlist, starttime, stoptime) :

		"""Measures the time between virtual blocks"""

        # At the start of a measurement loop, we have to get the start time at the beginning
        # of the block then measure the time for the block.
        #
        # Otherwise, we take the stop time from the previous block, make it the start time
        # for this block and measure this block.

		if (starttime == 0):
			self.waitNextActiveSensor(sensorlist)
			stoptime = java.lang.System.currentTimeMillis()
	
		starttime = stoptime

		self.waitNextActiveSensor(sensorlist)
		stoptime = java.lang.System.currentTimeMillis()

		runtime = stoptime - starttime
		return runtime, starttime, stoptime
####################################################################################
#
# self.getSpeed() is used as part of the speed measurement
#
# This takes several speed measurements and returns an average value. If more than
# 3 values are given, the min and max values are omitted from the average.
# The final speed value returned is an average of the remaining values.
#
####################################################################################
	def getSpeed(self, speedlist) :

		imin = imax = 0
		minval = maxval = 0.0
		
		if (self.NumSpeedMeasurements > 3):
			minval = min(speedlist)
			maxval = max(speedlist)
			for s in range(0, self.NumSpeedMeasurements):
				if (speedlist[s] == minval):
					imin = s
				if (speedlist[s] == maxval):
					imax = s
			if (imin > imax):
				del speedlist[imin]
				del speedlist[imax]
			else:
				del speedlist[imax]
				del speedlist[imin]
		
		speed = sum(speedlist)/len(speedlist)
		return speed
####################################################################################
#
# self.measureSpeed() performs the speed measurement algorithm
#
# Given which track loop and the length of a block, we can measure the speed by
# measuring the time through each block. This version takes several measurements and
# averaging them, throwing out the high and low values.
#
# The targetspeed parameter is used to select the appropriate sensor array
####################################################################################
	def measureSpeed(self, targetspeed) :
		"""converts time to speed, ft/sec - scale speed"""
		starttime = stoptime = 0	# Needed when using every block
		speed = 0.0
		speedlist = []
		num_measurements = self.NumSpeedMeasurements
		num_blocks = 1
		sensor_array = []
		
		self.memory24.value = str(targetspeed)

		if (int(targetspeed) >= self.HighSpeedThreshold) :
			num_blocks = self.HighSpeedNBlocks
			sensor_array = self.HighSpeedArrayN
			print ("Measuring speed using the high speed array,", num_blocks, "block(s)...")
		elif (int(targetspeed) >= self.MediumSpeedThreshold) :
			num_blocks = self.MediumSpeedNBlocks
			sensor_array = self.MediumSpeedArrayN
			print ("Measuring speed using the medium speed array,", num_blocks, "block(s)...")
		else:
			num_blocks = self.LowSpeedNBlocks
			sensor_array = self.LowSpeedArrayN
			print ("Measuring speed using the low speed array,", num_blocks, "block(s)...")

		# Calculate the length of the selected block
		blocklength = self.block * num_blocks

        # Measure the speed a number of times and put those speeds into a list

		for z in range(0,self.NumSpeedMeasurements) : # make 5 speed measurements
			duration, starttime, stoptime = self.measureTime(sensor_array,starttime,stoptime)

			if duration == 0 :
				print ("Error: Got a zero for duration") # this should not happen
				speed = 0.0
			else :
				speed = (blocklength / (duration / 1000.0)) * (3600.0 / 5280)
				print ("    Measurement ", z+1, ", Speed = ", str(round(speed,3)) , "MPH")
				self.status.text = "Speed = " + str(round(speed,3)) + " MPH"
			speedlist.append(speed)

		speed = self.getSpeed(speedlist)
		return speed
####################################################################################
#
# self.handle() will only be execute once here, to run a single test
#
####################################################################################
	def handle(self):

		long = False
		address = 0
		scale = ""
		mfrID = 0
		mfrVersion = 0
				
		# 01/02/2017 ECW: Ported to Erich's setup starting with v2.2
		print ("Speed Table Script Version", self.scriptversion)

		topspeed = float(self.MaxSpeed.text)/100
		print ("Top Target Speed is ", self.MaxSpeed.text, "MPH")
		self.status.text = "Locomotive Setup"
		self.memory25.value = "Preparing Locomotive for speed measurments"

		self.TrackNormal()
	
		if (self.LoopActive()) :
			self.status.text = "Locomotive Detected"
			print ("Locomotive found on track loop")
			pass
		else :
			print ("No locomotive detected on the track, cannot proceed")
			return
			
		self.TrackProgram()	

		print ("Reading Locomotive...")
		self.val29 = self.readServiceModeCV("29")
		print ("CV 29 = ", self.val29)
		self.val1 = self.readServiceModeCV("1")
		print ("CV 1 = ", self.val1)
		self.val17 = self.readServiceModeCV("17")
		print ("CV 17 = ", self.val17)
		self.val18 = self.readServiceModeCV("18")
		print ("CV 18 = ", self.val18)
		self.val7 = self.readServiceModeCV("7")
		print ("CV 7 = ", self.val7)
		self.val8 = self.readServiceModeCV("8")
		print ("CV 8 = ", self.val8)
		self.val105 = self.readServiceModeCV("105")
		print ("CV 105 = ", self.val105)
		self.val106 = self.readServiceModeCV("106")
		print ("CV 106 = ", self.val106)
		
		# Determine if this locomotive uses a long address
		if ((self.val29 & 32) == 32) :
			self.long = True
			self.address = (self.val17 - 192) * 256 + self.val18
		else :
			self.long = False
			self.address = self.val1
		
		# get the manufacturer so we can adjust for decoder-specific settings
		
		self.mfrID = self.val8
		self.mfrVersion = self.val7
		
		if (self.DecoderMap.has_key(self.mfrID)):
			self.DecoderType = self.DecoderMap[self.mfrID]
		else:
			self.DecoderType = "Unknown"
			
		print ("The Locomotive Address is: ", self.address)
		print ("The Manufacturer is: ", self.DecoderType)
		print ("The Manufacturer ID is: ", self.mfrID)
		print ("The Manufacturer Version is: ", self.mfrVersion)
		print ("The Current Private ID is ", self.val105, ", ", self.val106)

		self.TrackNormal()	

        # Getting throttle
		
		self.status.text = "Getting throttle"

		self.throttle = self.getThrottle(self.address, self.long)
		if (self.throttle == None) :
			print ("ERROR: Couldn't assign throttle!")
		else :
			print ("Trottle assigned to locomotive: ", self.address)

            # Getting Programmer

		self.programmer = addressedProgrammers.getAddressedProgrammer(self.long, self.address)

		self.SWLed("BLU", "ON")

		print ("Turn on the headlight")
		self.throttle.setF0(True)
		print ("Mute the sound")
		self.throttle.setF8(True)
	
		starttesttime = java.lang.System.currentTimeMillis()
		badlocomotive = False # will be true if locomotive will not go slow enough
		self.memory1.value = " "
		self.memory2.value = " "
		self.memory3.value = " "
		self.memory4.value = " "
		self.memory5.value = " "
		self.memory6.value = " "
		self.memory7.value = " "
		self.memory8.value = " "
		self.memory9.value = " "
		self.memory10.value = " "
		self.memory11.value = " "
		self.memory12.value = " "
		self.memory13.value = " "
		self.memory14.value = " "
		self.memory15.value = " "
		self.memory16.value = " "

		if (self.val105 != 42) :
			self.testbedWriteCV(105, 42) # Write Private ID #42 in Decoder CV 105
		if (self.val106 < 255) :
			self.val106 = self.val106+1
			self.testbedWriteCV(106, self.val106) # Write count in Decoder CV 106

		print ("Set Private ID to ", self.val105, ", ", self.val106)

		print ("Decoder Brand is", self.DecoderType)
		self.memory23.value = self.DecoderType
 		
		self.memory25.value = "Setting CVs to known state"
		self.testbedWriteCV(62, 0) # Turn off verbal reporting on QSI decoders
		self.testbedWriteCV(25, 0) # Turn off manufacture defined speed tables
		self.testbedWriteCV(19, 0) # Clear Consist Address in locomotive

		if self.long == True :			#turn off speed tables
			self.testbedWriteCV(29, 34)
		else:
			self.testbedWriteCV(29, 2)

		self.testbedWriteCV(2, 0)	#Start Voltage off
		self.testbedWriteCV(3, 0)	#Acceleration off
		self.testbedWriteCV(4, 0)	#Deceleration off
		self.testbedWriteCV(5, 0)	#Maximum Voltage off
		self.testbedWriteCV(6, 0)	#Mid Point Voltage off
		self.testbedWriteCV(66, 0) #Turn off Forward Trim
		self.testbedWriteCV(95, 0) #Turn off reverse Trim

		# Run Locomotive for 5 laps each direction to warm it up

		self.memory25.value = "Warming up Locomotive"
		self.status.text = "Warming up Locomotive"
		print
		print ("Warming up Locomotive")
		self.throttle.setIsForward(True)
		self.memory20.value = "Forward"

		#01/09/09	TCS decoder would not move when setting throttle to 1.0
 
 		print ("Set the throttle to 1.0")

		self.throttle.setSpeedSetting(.99)
		self.waitMsec(250)
		self.throttle.setSpeedSetting(1.0)

		print ("Wait for the locomotive to get to block", self.homesensor_num, "after", self.warmupLaps, "laps...")

		for x in range (0, self.warmupLaps) :
			self.waitNextActiveSensor([self.homesensor])

		print ("Stop the locomotive")
		self.throttle.setSpeedSetting(0.0)
		self.waitMsec(2000)
		
		# Warm up 5 laps reverse

		if self.Locomotive.getSelectedItem() <> "Steam" :
			self.throttle.setIsForward(False)
			self.memory20.value = "Reverse"
			self.throttle.setSpeedSetting(1.0)

			print ("Warming up in the reverse direction for", self.warmupLaps, "laps...")
			for x in range (0, self.warmupLaps) :
				self.waitNextActiveSensor([self.homesensor])

		# Find maximum speed reverse

			print ("Finding the maximum reverse speed...")
			self.memory25.value = "Finding Maximum Reverse Speed"
			self.status.text = "Finding Maximum Reverse Speed"
			self.throttle.setSpeedSetting(1.0)
			self.waitMsec(500)
			revmaxspeed = self.measureSpeed(self.fullSpeed)
			print ("Maximum reverse speed found = ",round(revmaxspeed))
			print
			print ("Returning locomotive to block", self.homesensor_num, "...")
			self.waitNextActiveSensor([self.homesensor])
			self.throttle.setSpeedSetting(0.0)
			self.status.text = "Max Reverse Speed " + str(int(revmaxspeed))
			self.waitMsec(3000)
		else :
			revmaxspeed = 0

		self.memory21.value = str(int(revmaxspeed))

		# Find maximum speed forward
		
		self.memory25.value = "Finding Maximum Forward Speed"
		self.status.text = "Finding Maximum Forward Speed"
		print ("Finding the maximum forward speed over", self.NumSpeedMeasurements, "laps...")
		self.throttle.setIsForward(True)
		self.waitMsec(500)
		self.memory20.value = "Forward"
		self.throttle.setSpeedSetting(1.0)
		self.waitMsec(1000)
		fwdmaxspeed = self.measureSpeed(self.fullSpeed)
		print ("Maximum forward speed found = ",round(fwdmaxspeed))
		print
		print ("Returning locomotive to block", self.homesensor_num, "...")
		self.waitNextActiveSensor([self.homesensor])
		
		self.throttle.setSpeedSetting(0.0)
		self.status.text = "Max Forward Speed " + str(int(fwdmaxspeed))
		self.memory22.value = str(int(fwdmaxspeed))
		self.waitMsec(1000)

		if (fwdmaxspeed > revmaxspeed) :
			print ("Locomotive",self.address,"is faster in the forward direction")
			self.throttle.setIsForward(True)
			self.waitMsec(500)
			self.memory20.value = "Forward"
		elif (revmaxspeed > fwdmaxspeed) :
			print ("Locomotive",self.address,"is faster in the reverse direction")
			self.throttle.setIsForward(False)
			self.waitMsec(500)
			self.memory20.value = "Reverse"
		else :
			print ("Locomotive",self.address,"runs equally well in both directions")
			self.throttle.setIsForward(True)
			self.waitMsec(500)
			self.memory20.value = "Forward"


		print
		self.memory23.value = self.DecoderType
		print ("Decoder Brand is ",self.DecoderType)

		if self.DecoderType == "Digitrax" :
			steplist = self.DigitraxStepList 
		elif self.DecoderType == "TCS" :
			#09/15/09
			self.memory25.value = "Determining Type of TCS Decoder"
			self.status.text = "Determining Type of TCS Decoder"
			print ("Determining Type of TCS Decoder")

			# Set speed table CV's to determine which type of TCS decoder it is
	
			self.testbedWriteCV(90,50)
			self.testbedWriteCV(93,249)

			# Turn on speed table
			if self.long == True :
				self.testbedWriteCV(29, 50)
			else:
				self.testbedWriteCV(29, 18)

			self.throttle.setSpeedSetting(.85)
			self.waitMsec(2000)
			speed = self.measureSpeed(self.fullSpeed)
			self.throttle.setSpeedSetting(0.0)
			if speed > (.9 * fwdmaxspeed) :
				steplist = self.NewTCSStepList
				print ("Using new TCS steplist")
			else :
				steplist = self.OldTCSStepList
				print ("Using old TCS steplist")
			self.waitMsec(3000)

		elif self.DecoderType == "Lenz5Gen" :
			steplist = self.Lenz5GenStepList
		elif self.DecoderType == "Atlas/Lenz XF" :
			steplist = self.LenzXFStepList
		elif self.DecoderType == "NCE" :
			steplist = self.NCEStepList
		elif self.DecoderType == "QSI/BLI" :
			steplist = self.QSIStepList
            #haven't verified that table for a SoundtraxxDSD unit is correct yet, may be same as Tsunami
		elif self.DecoderType == "SoundtraxxDSD" :
			steplist = self.SoundtraxxDSDStepList
		elif self.DecoderType == "Tsunami" :
			steplist = self.TsunamiStepList
		elif self.DecoderType == "ESU" :
			steplist = self.ESUStepList
		else :	#User doesn't know decoder type
				#and we couldn't figure it out 
			print ("Decoder is still unknown")
		self.throttle.setSpeedSetting(0.0)
		self.waitMsec(2000)


		#we are now ready to build a speedtable

		if self.DecoderType <> "Unknown" :

			self.memory25.value = "Measuring Speeds"
			self.status.text = "Measuring Speeds"

			#Turn off speed table for measurements
			if self.long == True :
				self.testbedWriteCV(29, 34)
			else:
				self.testbedWriteCV(29, 2)

			# Going to make speed measurements while locomotive is traveling in slower direction
			# if the locomotive is a diesel.  Steam locomotives with tenders that have offset
			# pickups sometimes gave ambiguous readings

			if self.Locomotive.getSelectedItem() <> "Steam" :
				if revmaxspeed > fwdmaxspeed :
					self.throttle.setIsForward(False)
					self.memory20.value = "Reverse"

			#Find throttle setting that gives desired speed

			stepvaluelist = [0]
			throttlesetting = 35	# starting throttle setting(determined by lots of testing)
			lowthrottle = 0

            #			while badlocomotive == False :

            #			for targetspeed in steplist :

			for speedvalue in steplist :

				targetspeed = round(speedvalue * topspeed)		

				print
				print ("Target Speed ",targetspeed)
				print

				stepvaluelist.extend([0,0,0]) #create spots in list for calculated speed steps

				#initializing all variables for next measured speed step
				Done = False
				speed = 1000
				minimumdifference = 20
				beenupone = False
				beendownone = False
				lowspeed = 0	
				hispeed = 1000
				hithrottle = 127

                #05/21/10
				if ((self.Locomotive.getSelectedItem() == "Diesel") and (targetspeed > revmaxspeed)) or targetspeed > fwdmaxspeed :
					print
					print ("Locomotive can not reach ",targetspeed, " MPH")
					print
					Done = True
					throttlesetting = 127

				while Done == False:

					# Measure speed
					self.throttle.setSpeedSetting(.0079365 * throttlesetting)
					self.waitMsec(100)
					print
					print ("Throttle Setting ",throttlesetting)
					speed = self.measureSpeed(targetspeed)
 
					# compare it to desired speed and decide whether or not to test a different throttle setting
					difference = targetspeed - speed
					print ("Measured Speed = ",round(speed,3), "Difference = ",round(speed - targetspeed,3), " at throttle setting ",throttlesetting)

					#Coarse Measurement
					if difference < -10 and targetspeed < 20 and throttlesetting > 15 : #started at 35 want to drop fast to reduce time
						hithrottle = throttlesetting
						throttlesetting = throttlesetting - 10
						if throttlesetting < lowthrottle :
							print ("throttlesetting ",throttlesetting,"is too slow")
							throttlesetting = lowthrottle + 1
                            #09/17/09
							if hithrottle-lowthrottle < 2 :
								Done = True
								if (hispeed - targetspeed) > (targetspeed - lowspeed) :
									throttlesetting = lowthrottle
								else :
									throttlesetting = hithrottlesetting

					elif difference < -13 and throttlesetting > 15 : # keep throttle setting > 0
						hithrottle = throttlesetting
						throttlesetting = throttlesetting - 6	 # and don't want drastic changes
						if throttlesetting < lowthrottle :
							print ("throttlesetting ",throttlesetting,"is too slow")
                            #08/29/09 This didn't resolve the issue			throttlesetting = lowthrottle
                            #12-05-08 Having problems with some BEMF decoders	throttlesetting = lowthrottle + 1
							throttlesetting = lowthrottle + 1
                            #09/17/09
							if hithrottle-lowthrottle < 2 :
								Done = True
								if (hispeed - targetspeed) > (targetspeed - lowspeed) :
									throttlesetting = lowthrottle
								else :
									throttlesetting = hithrottlesetting

					elif difference < -8 and throttlesetting > 6 : # keep throttle setting > 0
						hithrottle = throttlesetting
						throttlesetting = throttlesetting - 3
						if throttlesetting < lowthrottle :
							print ("throttlesetting ",throttlesetting,"is too slow")
							throttlesetting = lowthrottle + 1
                            #09/17/09
							if hithrottle-lowthrottle < 2 :
								Done = True
								if (hispeed - targetspeed) > (targetspeed - lowspeed) :
									throttlesetting = lowthrottle
								else :
									throttlesetting = hithrottlesetting

					elif difference > 13 and throttlesetting < 121 : # keep throtte setting < 128
						lowthrottle = throttlesetting
						throttlesetting = throttlesetting + 7
						if throttlesetting > hithrottle :
							print ("throttlesetting ",throttlesetting,"is too fast")
							throttlesetting = hithrottle - 1
					elif difference > 8 and throttlesetting < 123 : # keep throtte setting < 128
						lowthrottle = throttlesetting
						throttlesetting = throttlesetting + 4
						if throttlesetting > hithrottle :
							print ("throttlesetting ",throttlesetting,"is too fast")
							throttlesetting = hithrottle - 1
					elif difference > 5 and targetspeed < 20 and throttlesetting > 10 : #for motors that need a lot at the beginning
						lowthrottle = throttlesetting
						throttlesetting = throttlesetting + 5
						if throttlesetting > hithrottle :
							print ("throttlesetting ",throttlesetting,"is too fast")
							throttlesetting = hithrottle - 1

					else :
						#Fine Measurement
						if minimumdifference > abs(difference) :
							minimumdifference = abs(difference)
							savethrottlesetting = throttlesetting
						elif beenupone == True and beendownone == True :
							Done = True
							throttlesetting = savethrottlesetting
							lowthrottle = throttlesetting + 1
                            #09/11/08	added print
							print ("Closest throttle setting is", throttlesetting)
                            #09/22/08

						if difference < 0  and Done != True :
							throttlesetting = throttlesetting - 1
							beendownone = True
						elif difference > 0 and Done != True :
							throttlesetting = throttlesetting + 1
							lowthrottle = throttlesetting
							beenupone = True
						else :
							Done = True
							throttlesetting = savethrottlesetting
							lowthrottle = throttlesetting + 1

					if throttlesetting < 1 :
						print
						print ("Cannot create speedtable")
						print ("Locomotive has mechanical or decoder problem")
						print
						Done = True
						badlocomotive = True
						throttlesetting = 1

	
					if throttlesetting > 127 :
						print
						print ("Locomotive can not reach ",targetspeed, " MPH")
						print
						Done = True
						throttlesetting = 127

				lowthrottle = throttlesetting
				if difference < -5 :
					stepvaluelist.append(int(round((throttlesetting - .5) * 2)))
				elif difference > 5 :
					stepvaluelist.append(int(round((throttlesetting + .5) * 2)))
				else :
					stepvaluelist.append(int(round(throttlesetting * 2)))
				throttlesetting = throttlesetting + 10 	# no need test a value already in the table
											# time to do the next speed step
                                            #09/17/09	had instance where prior statment set speed to 128
				if throttlesetting > 127 :
					throttlsetting = 127

			# Stop locomotive

			self.throttle.setSpeedSetting(0.0)
			self.waitMsec(3000)

			#Calculate speed step values inbetween measured ones

			if badlocomotive == False :
				print
				print ("Measured Values")
				print (stepvaluelist)

				if stepvaluelist[4] < 4 :
					stepvaluelist[4] = 4

				stepvaluelist[0] = stepvaluelist[4] - (stepvaluelist[8] - stepvaluelist[4]) #trying to improve the bottom end performance

				# making sure none of the speedsteps are < 1
				if ((stepvaluelist[4] - stepvaluelist[0]) / 4) + stepvaluelist[0] < 1 :
					stepvaluelist[0] = 0

				for  z in range (4, 29, 4) :
					# To prevent speedsteps from having the same value
					# decided it was better to error faster than slower
					if stepvaluelist[z] - stepvaluelist[z - 4] < 4 :
						stepvaluelist[z] = stepvaluelist[z - 4] + 4

					if stepvaluelist[z] > 255 :	#can't have a value greater than 255
						stepvaluelist[z] = 255
 

					# Create calculated speed steps
					y = stepvaluelist[z] - stepvaluelist[z - 4]
					x = (y/4)
					stepvaluelist[z -3] = stepvaluelist[z] - round(x * 3)
					stepvaluelist[z -2] = stepvaluelist[z] - round(x * 2)
					stepvaluelist[z -1] = stepvaluelist[z] - round(x)

                    #01/09/09	some TCS decoders will stop if a speed step value is 250 or greater

				if self.DecoderType == "TCS" :
					print
					print ("Values before TCS correction")
					print (stepvaluelist)
					counter = 0
					for  z in range (21, 29, 1) :
                        #						print "z= ",z," ",stepvaluelist[z],"counter = ",counter
						if stepvaluelist[z] > 242 + counter:
							stepvaluelist[z] = 242 + counter
						counter = counter + 1

				print
				print ("All Values")
				print (stepvaluelist)

				self.memory25.value = "Writing Speed Table to Locomotive"

				# Write Speed Table to locomotive
				for z in range (67, 95) :
					self.testbedWriteCV(z, int(stepvaluelist[z - 66]))

				# Turn on speed table
				if self.DecoderType == "SoundtraxxDSD" or self.DecoderType == "Tsunami" :			
					self.testbedWriteCV(25, 16)

				if self.DecoderType == "QSI/BLI" :			
					self.testbedWriteCV(25, 1)

				if self.long == True :
					self.testbedWriteCV(29, 50)
				else:
					self.testbedWriteCV(29, 18)

				# Turn on acceleration and deceleration
				self.testbedWriteCV(3, 1)	#Acceleration on
				self.testbedWriteCV(4, 1)	#Deceleration on

				self.status.text = "Done"
			else :
				self.status.text = "Done - Locomotive has decoder or mechanical problem; cannot create speed table"

		else :
			self.status.text = "Done - Unknown Decoder Cannot Proceed"


		self.throttle.setF8(False)
		self.throttle.setF0(False)
		endtesttime = java.lang.System.currentTimeMillis()
		print
		print ("Test Time =",(endtesttime - starttesttime) / 1000, "sec.")

		print ("Return to the home position")
		self.throttle.setSpeedSetting(1.0)
		self.waitChange([self.sensor1])
		self.waitSensorActive(self.sensor1)
		self.throttle.setSpeedSetting(0.0)

		# done!

		self.SWLed("BLU", "OFF")		

		self.throttle.release()
		#re-enable button
		self.startButton.enabled = True
		# and stop


		# cycle track power because some Digitrax decoders don't stop
		self.DCCPower("N",  "OFF")
		self.DCCPower("HO", "OFF")
		self.waitMsec(500)

		self.DCCPower("N",  "ON")
		self.DCCPower("HO", "ON")
		self.waitMsec(500)

		return False
		
####################################################################################
#
# define what buttons do when clicked and attach that routine to the button
#
####################################################################################
	def whenMyButtonClicked(self,event) :
		self.start()
		# we leave the button off
		self.startButton.enabled = False

		return

####################################################################################
#
# This method creates the user input panel, starting the whole process
# the panel collects input parameters from the user
#
####################################################################################

	def setup(self):
		# create a frame to hold the button, set up for nice layout
		f = javax.swing.JFrame("Testbed Input Panel")		# argument is the frames title
		f.setLocation(300,200)
		f.contentPane.setLayout(javax.swing.BoxLayout(f.contentPane, javax.swing.BoxLayout.Y_AXIS))

		# create the start button
		self.startButton = javax.swing.JButton("Start")
		self.startButton.actionPerformed = self.whenMyButtonClicked

		self.status = javax.swing.JLabel("Press start when ready")

		templabel = javax.swing.JLabel("", javax.swing.JLabel.CENTER)
		templabel.setText("Select Locomotive Type")
		
		self.Locomotive = javax.swing.JComboBox()
		self.Locomotive.addItem("Diesel")
		self.Locomotive.addItem("Electric")
		self.Locomotive.addItem("Steam")
		
		self.MaxSpeed = javax.swing.JTextField(3)

		temppanel3 = javax.swing.JPanel()
		temppanel3.add(javax.swing.JLabel("Maximum Speed (MPH)"))
		temppanel3.add(self.MaxSpeed)

		temppanel2 = javax.swing.JPanel()
		f.contentPane.add(templabel)
		f.contentPane.add(self.Locomotive)
		f.contentPane.add(temppanel3)
		temppanel2.add(self.startButton)
		f.contentPane.add(temppanel2)
		f.contentPane.add(self.status)
		f.pack()
		f.show()

		return

####################################################################################
#
# Instantiate the automation class and start it up
#
####################################################################################
a = DCCDecoderCalibration()

# set the name, as a example of configuring it
a.setName("DCC Decoder Calibration")

# This brings up the dialog box that will call self.start()
a.setup()
