#The Script will automatically build a speed table for a decoder using OPS mode programming and create a text
#file on the desktop for future use.It is designed for N Scale decoder-equipped locomotives and the Digitrax DCC
#system
#
# This version of the script is deigned for speed matching layouts with 8 detection blocks
#
#Original authors:
#Phil Klein, Version 2.14, Copyright 2010
#Thomas Stephens, Version SpeedTLSv5_B, Copyright January 2013
#Eric Bradford, Version UltimateSpeedMatch_vx1.0, Copyright February 2013
#Thomas Stephens, Version USpeedMatch_v1.1, GPL 1.1, Copyright March 24, 2013
#The above gentlemen laid the foundation upon which this script is built, incorporating their scripts into this single
#speed matching script.
#
#Current authors are:
#James Kalenowski, Version USpeedMatch_v1.7, Copyright January 2014
#John Wallis, Version NRMRCSpeedMatch_v1.7, Copyright July 24, 2014
#
##$Revision: 1.3 $ revision of AutomatonExample distributed with JMRI, from which this script has been developed.
#__________________________________________________________________________________________________
#
# Summary of how it works:
#	User enters info about locomotive and decoder such as:
#		Locomotive Number
#		DCC Address
#		Brand of decoder (default = Digitrax)
#		CV3 and CV4 desired, 
#		Direction to be tested
#		Type of locomotive (steam or diesel)
#		Top speed desired on the input panel.
#	A throttle is created in JMRI to run the locomotive
#	The locomotive is warmed up for a few laps (in both directions if diesel is selected) 
#	The top speed of the locomotive is measured (in both directions for diesels)
#	Using the block detectors to measure time, it adjusts the throttle until the appropriate speed is found
#		for the speed step
#	7 Speed steps are measured; the rest are interpolated. Measured ones are 4, 8, 12, 16, 20, 24, 28
#	These are written to the decoder, a text file is created on the Windows PC desktop, the locomotive is 
#		released from the throttle, and the throttle is discarded.
#
#	If something goes wrong and you need to start over, do the following:
#		"Steal" it in another throttle and stop the locomotive.
#		Close the input panel.
#		Under the "Panels" tab, select "Thread Monitor" and "Kill" the script.
#		Or just close JMRI and reopen JMRI software.
#
#Notes:
#	BEMF	Any adjustments should be made before running the script
#
#	TCS	May need to turn off BEMF since it is not adjustable. A speed jump may be present and may
#		be very noticeable after the speed table is created
#
#	Digitax 	CV57 default value 6 may prevent the locomotive from going below about 5 mph. Setting
#		CV57 to 33 improves this. Or turn it off by setting it to zero.  This Speed Matching script will
#		set it to zero for you.
#
#	NCE	Some older N scale decoders will revert to 28 step mode instead of 128 step mode
#
#	The locomotives speed should be approximately equivalent to what is displayed on a throttle if the
#	maximum speed was set to 100 (running by itself without a train).
# 
#Hardware tested with this script
#	Command Station - Digitrax DCS100, Digitrax Zephyr, Digitrax Zephyr Extra 
#	Train Detection - BDL168 (Board Address 1)
#	Computer Interface - MS100, Locobuffer II, LocoBuffer-USB, Digitrax PR3
#	JMRI Software 3.0 OR GREATER IS REQUIRED for this script to work.
#	By opening up the JMRI Sysem Console screen ("Help Tab" then "System console"), one can see
#	what is being done on the track.  Useful for problem solving.

#	Track - 24 pieces of Kato N scale 19" Radius Unitrack (Cat. No. 20-160)
#	One sensor for used every 2 pieces (12 blocks) or 3 pieces (8 blocks) of Unitrack, share sensors 1 - 12
#
#Updates to script from all authors:
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
#	08/25/08	Added waits after writing CV's 62, 25 and 29  possible issue with Zypher not sending
#			write CV29 command
#	08/26/08	Changed speedtable setting for testing 128 support from 120 to 84
#	09/09/08	Seperated testing for 128 support for N scale and HO scale.
#	09/09/08	Changed speedtable setting for testing 128 support for HO from 84 to 80
#	09/11/08	Add displaying of throttle setting chosen for given speed step
#	09/22/08	Added "Done != True" to fine measurement. Was changing throttle setting even though
#			we were done 
#	09/22/08	Increased wait times after writing CV's before warm up  QSI decoders weren't getting
#			all of them; was 250ms, now 500ms.
#	01/09/09	TCS decoders would not run after initial ops mode programming
#	01/09/09	TCS decoders stall when using values above 249 
#	06/15/09	Changed Soundtraxx to Soundtraxx DCD in preparation for adding Soundtraxx Tsunami 
#	06/26/09	Added Soundtraxx Tsunami
#	08/28/09	Increased wait time when writing table from 100ms to 150ms.  DZ121 was getting zero
#			written for every other entry 
#	09/11/09	Added cycling track power before starting.
#	09/15/09	Created new list for newer TCS decoders
#	09/15/09	Created test to determine which TCS list to use
#	09/15/09	Increased wait time when measuring max speed.  Tsunami was missing direction change
#	09/15/09	Added wait time when turning on speed table.  Tsunami was missing change to CV29
#	09/17/09	Removed "Unknown" from selection list.  Getting too hard to support 
#	09/17/09	fixed throttlesetting from being set above 127 
#	09/17/09	moved comparison of hithrottle & lowthrottle into coarse measurement
#	09/18/09	added a second forward statment when measuring fwd max speed. Sometimes doesn't
#			execute
#	05/21/10	changed getOpsModeProgrammer to getAddressedeProgrammer
#	05/21/10	warmup for steam now only goes forward
#	03/17/12   Added prompts for acel/decel values (CV3/4), Sets value when done
#	03/17/12   added prompt for target direction. Replaces calculation based on max speed
#	03/17/12   increased numbers of values in countsensor to compensate for odd values on specific
#			track sections
#	02/18/13	Changed number of measurements from 1 to 4 for 100 mph by adding a "high speed array"..
#	02/18/13	Corrected decoder lists for speed measurements.  Wrong list being used due to python
#			coding issues.
#	02/18/13	Text File now being created on windows PC desktop for future use.
#	02/18/13	Added comments by commands throughout the script to help others understand what is
#			taking place.
#	03/20/13	Reverted change to let different brands run together.
#	03/24/13	Changed CV3&4 defaults to 4
#	03/24/13	Changed initial dialog position. Was showing mostly off screen.
#
#
#--------------------------------------------------------------- 
import java
import javax.swing
import jmri

class AutoSpeedTable(jmri.jmrit.automat.AbstractAutomaton) :

	# individual block section length (scale feet)
	blockN = float(198)		# layout with 8 blocks

	long = False
# 3/17/12 more test numbers. was 5. Compensate for odd values on specific track sections
	countsensor = 7	# Use 1 for testing and 6 for running
# --- TLS

	# init() is called exactly once at the beginning to do
	# any necessary configuration.
	def init(self):

		self.sensor1 = sensors.provideSensor("LS1")
		self.sensor2 = sensors.provideSensor("LS2")
		self.sensor3 = sensors.provideSensor("LS3")
		self.sensor4 = sensors.provideSensor("LS4")
		self.sensor5 = sensors.provideSensor("LS5")
		self.sensor6 = sensors.provideSensor("LS6")
		self.sensor7 = sensors.provideSensor("LS7")
		self.sensor8 = sensors.provideSensor("LS8")
		self.sensor9 = sensors.provideSensor("LS9")
		self.sensor10 = sensors.provideSensor("LS10")
		self.sensor11 = sensors.provideSensor("LS11")
		self.sensor12 = sensors.provideSensor("LS12")
		self.sensor13 = sensors.provideSensor("LS13")
		self.sensor14 = sensors.provideSensor("LS14")
		self.sensor15 = sensors.provideSensor("LS15")
		self.sensor16 = sensors.provideSensor("LS16")

		self.memory1 = memories.provideMemory("1")
		self.memory10 = memories.provideMemory("10")
		self.memory11 = memories.provideMemory("11")
		self.memory12 = memories.provideMemory("12")
		self.memory13 = memories.provideMemory("13")
		self.memory14 = memories.provideMemory("14")
		self.memory15 = memories.provideMemory("15")
		self.memory16 = memories.provideMemory("16")
		self.memory2 = memories.provideMemory("2")
		self.memory20 = memories.provideMemory("20")
		self.memory21 = memories.provideMemory("21")
		self.memory22 = memories.provideMemory("22")
		self.memory23 = memories.provideMemory("23")
		self.memory24 = memories.provideMemory("24")
		self.memory25 = memories.provideMemory("25")
		self.memory3 = memories.provideMemory("3")
		self.memory4 = memories.provideMemory("4")
		self.memory5 = memories.provideMemory("5")
		self.memory6 = memories.provideMemory("6")
		self.memory7 = memories.provideMemory("7")
		self.memory8 = memories.provideMemory("8")
		self.memory9 = memories.provideMemory("9")


#EWB--Used for 100 MPH (setting for Digitrax DT400 throttle)
#EWB--Wanted to take 3-4 measurements at higher speeds instead of just 1 measurement per lap.
		self.HighSpeedArray = (
				self.sensor1,
				self.sensor5,
				self.sensor9,
				self.sensor13)

#Used for speeds between 50 and 99 MPH
#Uses 2 blocks for each measurement
		self.MediumSpeedArray = (
				self.sensor1,
				self.sensor3,
				self.sensor5,
				self.sensor7,
				self.sensor9,
				self.sensor11,
				self.sensor13,
				self.sensor15)

# used below 50 MPH 
#Uses single blocks for measurements
		self.LowSpeedArray = (
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
				self.sensor12,
				self.sensor13,
				self.sensor14,
				self.sensor15,
				self.sensor16)



#		These speed steps are measured.  All others are calculated
#				CV	70	74	78	82	86	90	94
#		Speedsteps		4	8	12	16	20	24	28

#		These lists are percentages of full speed
		self.DigitraxStepList = [
					14,	29,	43,	57,	71,	86,	100]

		self.Lenz5GenStepList = [
					17,	30,	44,	57,	71,	84,	98]

		self.LenzXFStepList = [
					11,	26,	40.5,	55,	70,	84,	98.5]

		self.NCEStepList = [
					10.5,	25,	39.5,	54,	68,	83,	98]

		self.MRCStepList = [
					14,	29,	43,	57,	71,	86,	100]

		self.OldTCSStepList = [
					14.5,	28.5,	42.5,	57,	71.5,	86,	99]

		self.NewTCSStepList = [
					13,	25.5,	38,	50.5,	63,	75.5,	88]

		self.QSIStepList = [
					11,	26,	41,	55,	70,	85,	99]

		self.SoundtraxxDSDStepList = [
					14,	28,	42,	56,	70,	84,	99]

		self.TsunamiStepList = [
					14.5,	28.5,	42.5,	57,	71,	85,	99]

		self.ESUStepList = [
					12,	27,	41,	56,	70,	85,	99]
		self.XXXStepList = [
					14,	29,	43,	57,	71,	86,	100]


# Getting throttle
		
		self.status.text = "Getting Throttle"

		dccnumber = int(self.dccaddress.text)   #Used for file naming confusion and text file information
		loconumber = int(self.locoaddress.text)  #created to help with file naming confusion or duplicates
		if (dccnumber > 127) :
			 self.long = True
		else :
			 self.long = False
		self.throttle = self.getThrottle(dccnumber, self.long)
		if (self.throttle == None) :
			 print "Couldn't assign throttle!"
		else :
			print
			print
			print
			print "Locomotive number",loconumber, "with DCC Address",dccnumber

# Getting Programmer
#05/21/10
		self.programmer = addressedProgrammers.getAddressedProgrammer(self.long, dccnumber)

		return
#----------------------------------------------------------------
	def measuretime(self,sensorlist,blocklength,starttime,stoptime) :

		"""Measures the time between virtual blocks"""
		if starttime == 0 :
			self.waitChange(sensorlist)
			self.waitSensorActive(sensorlist)
			stoptime = java.lang.System.currentTimeMillis()	

		starttime = stoptime

		self.waitChange(sensorlist)
		self.waitChange(sensorlist)
		self.waitSensorActive(sensorlist)

		stoptime = java.lang.System.currentTimeMillis()
		runtime = stoptime - starttime
		return runtime, starttime, stoptime
#---------------------------------------------------------------
	def getspeed(self,targetspeed,block) :
		"""converts time to speed, ft/sec - scale speed"""
		starttime = stoptime = 0	# Needed when using every block
		self.memory24.value = str(targetspeed)

		speedlist = []	# Clear Speedlist (speed list contains measured speeds for each run)

		self.waitSensorInactive(self.LowSpeedArray)	# Making sure locomotive is at the correct starting position

		for z in range(1,self.countsensor + 1) : # make <countsensor> speed measurements
			if int(targetspeed) >= 125 : #Used for determining max forward and reverse speeds
				if block == 132 :
					blocklength = block * 12	# N scale loop has 12 blocks
				
				else :
					blocklength = block * 8	# N scale loop has 8 blocks

				duration, starttime, stoptime = self.measuretime([self.sensor1],blocklength,starttime,stoptime)
			
			elif int(targetspeed) >= 100 :	# Used for final speed step and for finding max forward and reverse speeds.
				blocklength = block * 4
				duration, starttime, stoptime = self.measuretime(self.HighSpeedArray,blocklength,starttime,stoptime)
								# makes 4-block measurements

			elif int(targetspeed) >= 50 :		# Used for speed steps between 50 and 99 mph.
				blocklength = block * 2
				duration, starttime, stoptime = self.measuretime(self.MediumSpeedArray,blocklength,starttime,stoptime)
								# makes 2-block measurements
			else :
				blocklength = block * 1	# Used for speed steps 10 and 49 mph.
				duration, starttime, stoptime = self.measuretime(self.LowSpeedArray,blocklength,starttime,stoptime)
								# makes 1-block measurements
			
			if duration == 0 :
				print "Measurement #",z," duration = ",duration
				z = z - 1
				print "got a zero for duration" # this has occured when using a MS100
				print "        Measurement #",z
			else :

				speed = (blocklength / (duration / 1000.0)) * (3600.0 / 5280)	
				speedlist.append(speed)

				print "Measured Speed MPH =",round(speed,1) , " Measurement #",z
				self.status.text = "Measured Speed = " + str(round(speed,1)) + " MPH"

				if self.sensor1.knownState==ACTIVE:
					self.memory1.value = str(round(speed))
					self.memory7.value = " "
					self.memory6.value = " "
					print "[Block 1]"
				elif self.sensor2.knownState==ACTIVE:
					self.memory2.value = str(round(speed))
					self.memory8.value = " "
					self.memory7.value = " "
					print "[Block 2]"
				elif self.sensor3.knownState==ACTIVE:
					self.memory3.value = str(round(speed)) 
					self.memory9.value = " "
					self.memory8.value = " "
					print "[Block 3]"
				elif self.sensor4.knownState==ACTIVE:
					self.memory4.value = str(round(speed)) 
					self.memory10.value = " "
					self.memory9.value = " "
					print "[Block 4]"
				elif self.sensor5.knownState==ACTIVE:
					self.memory5.value = str(round(speed)) 
					self.memory11.value = " "
					self.memory10.value = " "
					print "[Block 5]"
				elif self.sensor6.knownState==ACTIVE:
					self.memory6.value = str(round(speed)) 
					self.memory12.value = " "
					self.memory11.value = " "
					print "[Block 6]"
				elif self.sensor7.knownState==ACTIVE:
					self.memory7.value = str(round(speed)) 
					self.memory1.value = " "
					self.memory12.value = " "
					print "[Block 7]"
				elif self.sensor8.knownState==ACTIVE:
					self.memory8.value = str(round(speed)) 
					self.memory2.value = " "
					self.memory1.value = " "
					print "[Block 8]"
				elif self.sensor9.knownState==ACTIVE:
					self.memory9.value = str(round(speed)) 
					self.memory3.value = " "
					self.memory2.value = " "
					print "[Block 9]"
				elif self.sensor10.knownState==ACTIVE:
					self.memory10.value = str(round(speed)) 
					self.memory4.value = " "
					self.memory3.value = " "
					print "[Block 10]"
				elif self.sensor11.knownState==ACTIVE:
					self.memory11.value = str(round(speed)) 
					self.memory5.value = " "
					self.memory4.value = " "
					print "[Block 11]"
				elif self.sensor12.knownState==ACTIVE:
					self.memory12.value = str(round(speed)) 
					self.memory6.value = " "
					self.memory5.value = " "
					print "[Block 12]"
				elif self.sensor13.knownState==ACTIVE:
					self.memory13.value = str(round(speed)) 
					self.memory7.value = " "
					self.memory6.value = " "
					print "[Block 13]"
				elif self.sensor14.knownState==ACTIVE:
					self.memory14.value = str(round(speed)) 
					self.memory8.value = " "
					self.memory7.value = " "
					print "[Block 14]"
				elif self.sensor15.knownState==ACTIVE:
					self.memory15.value = str(round(speed)) 
					self.memory9.value = " "
					self.memory8.value = " "
					print "[Block 15]"
				elif self.sensor16.knownState==ACTIVE:
					self.memory16.value = str(round(speed)) 
					self.memory10.value = " "
					self.memory9.value = " "
					print "[Block 16]"


		# select the median from the list and use it as the measured speed
		speedlist.sort() #EWB-- sorts the <countsensor> measurements from smallest to largest
		speed = speedlist.pop(3) #EWB-- Chooses (numbered entry) in sorted "speedlist" set above NOT including first entry
		# Previous number was not choosing correct median value for set of measurements.

		return speed
#---------------------------------------------------------------

# handle() will only execute once here, to run a single test
# Any "print" command starting from here will show up in the JMRI Sysem Console screen ("Help Tab" then "System console")
	def handle(self):
	
		print "NRMRC Speed Match 8 Version 1.10 --- 5/10/2015"

		screendisplay = float(self.MaxSpeed.text)	# used for display purposes
		topspeed = float(self.MaxSpeed.text)/100	# Used for calculation purposes
		print "Top Speed is ",screendisplay, "MPH"
		self.status.text = "Locomotive Setup"
		self.memory25.value = "Preparing Locomotive for speed measurments"

#09/11/09
		jmri.InstanceManager.powerManagerInstance().setPower(jmri.PowerManager.OFF)
		self.waitMsec(1000)
		jmri.InstanceManager.powerManagerInstance().setPower(jmri.PowerManager.ON)
		self.waitMsec(1000)
		self.throttle.speedSetting = 0.
		self.waitMsec(500)
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



		if self.Scale.getSelectedItem() == "N Scale" :
			block = self.blockN
		if self.Scale.getSelectedItem() == "HO Scale" :
			block = self.blockHO

		else :
			# if user forgets to click a scale button, then it's N scale
			block = self.blockN

		print self.Scale.getSelectedItem()
		print "Decoder Brand is", self.DecoderBrand.getSelectedItem()
		self.memory23.value = self.DecoderBrand.getSelectedItem()
		decodertype = self.DecoderBrand.getSelectedItem()
		print "CV3 will be set to",self.cv3.text
		print "CV4 will be set to",self.cv4.text
		print "Speed Matching Direction is set to", self.SetDirection.getSelectedItem()
		print "-----"
		print "-----\n"
 
		# This will change FX Rate and Keep Alive on Digitrax Decoders
		# This will change Random Sound Max on ESU LokSound Decoders
# 08/25/08
# 09/22/08
		if decodertype == "QSI-BLI" :
			self.programmer.writeCV(62, 0, None) # Turn off verbal reporting on QSI decoders
			self.waitMsec(1000)

		if decodertype == "Digitrax" :
			self.programmer.writeCV(57, 0, None) # Turn OFF Back EMF as per note above.
			self.waitMsec(1000)
			
		self.programmer.writeCV(25, 0, None) # Turn off manufacture defined speed tables
		self.waitMsec(750)

		if self.long == True :			#turn off speed tables
			self.programmer.writeCV(29, 34, None)
		else:
			self.programmer.writeCV(29, 2, None)

		self.waitMsec(500)
		#self.programmer.writeCV(2, 0, None)	#Start Voltage off (EWB--CV not changed due to high max forward/reverse speeds measured.  speeds > 225mph!)
		#self.waitMsec(500)
		self.programmer.writeCV(3, 0, None)	#Acceleration off
		self.waitMsec(500)
		self.programmer.writeCV(4, 0, None)	#Deceleration off
		self.waitMsec(500)
		self.programmer.writeCV(19, 0, None)	#Clear consist
		self.waitMsec(500)
		#self.programmer.writeCV(5, 0, None)	#Maximum Voltage off  (EWB--CV not changed due to high max forward/reverse speeds measured.  speeds > 225mph!)
		#self.waitMsec(500)
		#self.programmer.writeCV(6, 0, None)	#Mid Point Voltage off  (EWB--CV not changed due to high max forward/reverse speeds measured.  speeds > 225mph!)
		#self.waitMsec(500)
		self.programmer.writeCV(66, 0, None) #Turn off Forward Trim
		self.waitMsec(500)
		self.programmer.writeCV(95, 0, None) #Turn off reverse Trim
		self.waitMsec(500)

		# Run Locomotive for 10 laps each direction to warm it up

		self.memory25.value = "Warming up Locomotive"
		self.status.text = "Warming up Locomotive"
		print
		print "Warming up Locomotive"
		print
		self.throttle.setIsForward(True)
		self.memory20.value = "Forward"

		self.throttle.setF0(True)
		self.throttle.setF8(True)

		# Warm up locomotive for 10 laps forward

#01/09/09	TCS decoder would not move when setting throttle to 1.0
 
		self.throttle.speedSetting = .98

		self.waitMsec(500)
		self.throttle.speedSetting = .98

		for x in range (1, 10) :
			self.waitChange([self.sensor1])
			self.waitSensorActive(self.sensor1)

		self.throttle.speedSetting = 0.0
		self.waitMsec(2000)
		
		# Warm up 10 laps reverse

#05/21/10	Removed reverse warmup and max speed measurement for Steam

		if self.Locomotive.getSelectedItem() == "Diesel" :
			self.throttle.setIsForward(False)
			self.memory20.value = "reverse"
			self.throttle.speedSetting = .98

			for x in range (1, 10) :
				self.waitChange([self.sensor1])
				self.waitSensorActive(self.sensor1)

		# Find maximum speed reverse

			self.memory25.value = "Finding Maximum Speeds"
			self.throttle.speedSetting = 1.0
			self.waitMsec(500)
			revmaxspeed = self.getspeed(125,block)
			print
			print "Reverse Max Speed = ",round(revmaxspeed), "MPH"
			print
			self.throttle.speedSetting = 0.0
			self.status.text = "Max Reverse Speed = " + str(int(revmaxspeed))
			
#09/15/09
			self.waitMsec(3000)

#05/21/10
		else :
			revmaxspeed = 0
		
		self.memory21.value = str(int(revmaxspeed))



		# Find maximum speed forward
#09/18/09
		self.throttle.setIsForward(True)
		self.waitMsec(500)
		self.throttle.setIsForward(True)
		self.waitMsec(500)
		self.memory20.value = "Forward"
		self.throttle.speedSetting = .98
		self.waitMsec(1000)
		fwdmaxspeed = self.getspeed(125,block)
		print
		print "Forward Max Speed = ",round(fwdmaxspeed), "MPH"
		print
		self.throttle.speedSetting = 0.0
		self.status.text = "Max Forward Speed " + str(int(fwdmaxspeed))
		self.memory22.value = str(int(fwdmaxspeed))
		self.waitMsec(1000)
		
		self.memory23.value = decodertype
		print "Decoder Brand Installed is ",decodertype

# 3/24/2013 Removed decoder specific steplist. Was prefenting different decoder types from running together
# 			Not needed anyway as speed determined from actual measurement of physical speed.

		steplist = self.XXXStepList
		self.throttle.speedSetting = 0.0
		self.waitMsec(2000)


		#we are now ready to build a speedtable
		if decodertype <> "Unknown" :

			self.memory25.value = "Measuring Speeds"

			#Turn off speed table for measurements
			if self.long == True :
				self.programmer.writeCV(29, 34, None)
			else:
				self.programmer.writeCV(29, 2, None)

#set direction based on user selection
# ++ TLS
			if self.SetDirection.getSelectedItem() == "Forward" :
				self.throttle.setIsForward(True)
				self.memory20.value = "Forward"
			else:
				self.throttle.setIsForward(False)
				self.memory20.value = "Reverse"
# -- TLS

			#Find throttle setting that gives desired speed

			stepvaluelist = [0]
			throttlesetting = 40	#EWB -- starting throttle setting increased by 5 units (determined by lots of testing)
			lowthrottle = 0	

			for speedvalue in steplist :

				targetspeed = round(speedvalue * topspeed)		

				print
				print
				print "TARGET SPEED BEING MEASURED IS: ",targetspeed, " MPH"
				print
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
					print "Locomotive can not reach ",targetspeed, " MPH"
					print
					Done = True
					throttlesetting = 127

				while Done == False:

					# Measure speed
					self.throttle.speedSetting = (.0079365 * throttlesetting)
					self.waitMsec(100)
					print
					print "Throttle Setting ",throttlesetting
					speed = self.getspeed(targetspeed,block)
 
					# compare it to desired speed and decide whether or not to test a different throttle setting
					difference = targetspeed - speed
					print "Difference = ",round(speed - targetspeed,1), "MPH at throttle setting ",throttlesetting
					print

					#Coarse Measurement
					if difference < -10 and targetspeed < 20 and throttlesetting > 15 : #started at 40 want to drop fast to reduce time
						hithrottle = throttlesetting
						throttlesetting = throttlesetting - 5
						if throttlesetting < lowthrottle :
							print "throttlesetting ",throttlesetting,"is too slow"
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
							print "throttlesetting ",throttlesetting,"is too slow"

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
							print "throttlesetting ",throttlesetting,"is too slow"
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
							print "throttlesetting ",throttlesetting,"is too fast"
							throttlesetting = hithrottle - 1
					elif difference > 8 and throttlesetting < 123 : # keep throtte setting < 128
						lowthrottle = throttlesetting
						throttlesetting = throttlesetting + 4
						if throttlesetting > hithrottle :
							print "throttlesetting ",throttlesetting,"is too fast"
							throttlesetting = hithrottle - 1
					elif difference > 5 and targetspeed < 20 and throttlesetting > 10 : #for motors that need a lot at the beginning
						lowthrottle = throttlesetting
						throttlesetting = throttlesetting + 5
						if throttlesetting > hithrottle :
							print "throttlesetting ",throttlesetting,"is too fast"
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
							print "Closest throttle setting is ", throttlesetting, "   On to next speed step"
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
						print "Cannot create speedtable"
						print "Locomotive has mechanical or decoder problem"
						print
						Done = True
						badlocomotive = True
						throttlesetting = 1
	
					if throttlesetting > 127 :
						print
						print "Locomotive can not reach ",targetspeed, " MPH"
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
				throttlesetting = throttlesetting + 7 	# EWB -- Changed value from 10 to 7 to decrease time it takes to find each target speed.
														# no need test a value already in the table
														# time to do the next speed step

				#09/17/09	had instance where prior statment set speed to 128
				if throttlesetting > 127 :
					throttlsetting = 127

			# Stop locomotive

			self.throttle.speedSetting = 0.0
			self.waitMsec(3000)

			#Calculate speed step values inbetween measured ones

			if badlocomotive == False :
				print
				print "Measured Values"
				print stepvaluelist
				print

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

				if decodertype == "TCS" :
					print
					print "Values before TCS correction"
					print stepvaluelist
					print
					counter = 0
					for  z in range (21, 29, 1) :
						#print "z= ",z," ",stepvaluelist[z],"counter = ",counter
						if stepvaluelist[z] > 242 + counter:
							stepvaluelist[z] = 242 + counter
						counter = counter + 1
				print"Turn on acceleration and deceleration"	# Turn on acceleration and deceleration	
				print "Writing value to CV3: ",self.cv3.text
				self.programmer.writeCV(3, int(self.cv3.text), None)	#Acceleration changed to user setting from input panel.
				self.waitMsec(250)
				print "Writing value to CV4: ",self.cv4.text
				self.programmer.writeCV(4, int(self.cv4.text), None)	#Deceleration changed to user setting from input panel.
				self.waitMsec(250)

				print
				print "All Speed Table CV Values"
				print stepvaluelist		#Displays whole range of speed table values on JMRI system console.
				print
				print "Writing Speed Table CV Values to Locomotive"

				# Write Speed Table to locomotive
				for z in range (67, 95) :
					print "CV",z," = ", int(stepvaluelist[z - 66])
					self.programmer.writeCV(z, int(stepvaluelist[z - 66]), None)
					#08/28/09
					self.waitMsec(1000)
				print
				print "Turn on speed table"
				print
#06/28/09
				if decodertype == "SoundtraxxDSD" or decodertype == "Tsunami" :			
					self.programmer.writeCV(25, 16, None)
					#09/15/09
					self.waitMsec(100)
					
				if decodertype == "QSI-BLI" :
					self.programmer.writeCV(25, 1, None)
				
				if self.long == True :
					self.programmer.writeCV(29, 50, None)	#note: CV29 set to use speed table, 28/128 speed steps, forward direction, analog off.
				else:
					self.programmer.writeCV(29, 18, None)


				self.outfilename = "/home/jimk/desktop/locos" + "Loco " + self.locoaddress.text + "_""DCC# " + self.dccaddress.text + "_" +decodertype + ".txt"
				#Creates a file on Windows PC Desktop in the following manner:  "Loco 1234_DCC# 4321_Digitrax.txt"
				print
				print "Transferring Data to a Text File on PC Desktop for future use: ",self.outfilename
				print
				self.ofl = open(self.outfilename, "a")
				self.ofl.write (self.Scale.getSelectedItem() + "\n")	#Records scale used in text file.
				self.ofl.write ("-----\n")								# New line created.
				self.ofl.write ("-----\n")
				self.ofl.write ("CV3 is set to " + self.cv3.text + "\n")	#Records what CV3 was set to as per input panel.
				self.ofl.write ("CV4 is set to " + self.cv4.text + "\n")	#Records what CV4 was set to as per input panel.
				self.ofl.write ("\n")
				self.ofl.write ("Speed Matching Direction is set to " + self.SetDirection.getSelectedItem()  + "\n")	#Records loco direction used for speed matching.
				self.ofl.write ("\n")
				self.ofl.write ("Max Forward Speed is " + str(int(fwdmaxspeed))+ " MPH" + "\n")	#Records max forward speed obtained.
				self.ofl.write ("Max Reverse Speed is " + str(int(revmaxspeed)) + " MPH" + "\n")		#Records max reverse speed obtained.
				self.ofl.write ("-----\n")
				self.ofl.write ("-----\n")
				self.ofl.write ("Speed Table Values" + "\n")		
				# Write Speed Table to file
				for z in range (67, 95) :
					x = int(stepvaluelist[z - 66])
					self.ofl.write ("CV " + str(z) + " --- " + str(x))		#Records Speed Table CV values from CV 67 to CV94.
					self.ofl.write ("\n")
				self.ofl.write ("\n")
				self.ofl.flush()
				self.ofl.close()
								
				self.status.text = "Done"
			else :
				self.status.text = "Done - Locomotive has decoder or mechanical problem; cannot create speed table"

		else :
			self.status.text = "Done - Unknown Decoder Cannot Proceed"
	
		
		
		self.throttle.setF8(False)
		self.throttle.setF0(False)
		endtesttime = java.lang.System.currentTimeMillis()
		print
		print "Test Time = ",((endtesttime - starttesttime) / 1000) / 60, " min."		#Displays time it took to complete the speedmatching of locomotive.

		# done!

		self.throttle.release()
		#re-enable button
		self.startButton.enabled = True
		# and stop


		# cycle track power because some Digitrax decoders don't stop

		jmri.InstanceManager.powerManagerInstance().setPower(jmri.PowerManager.OFF)
		self.waitMsec(2000)
		jmri.InstanceManager.powerManagerInstance().setPower(jmri.PowerManager.ON)
		self.memory25.value = "Done - Ready for next locomotive"
                print "Ready for next locomotive"



		return 0
#---------------------------------------------------------------
	# define what buttons do when clicked and attach that routine to the button
	def whenMyButtonClicked(self,event) :
		self.start()
		# we leave the button off
		self.startButton.enabled = False

		return
#---------------------------------------------------------------

	# routine to show the user input panel, starting the whole process
	# the panel collects the locomotive address and the decoder type if known
	def setup(self):

		DecoderList = ["Digitrax", "TCS", "NCE", "MRC", "QSI-BLI", "SoundTraxxDSD", "Lenz Gen 5", "ESU", "Atlas/Lenz XF", "Tsunami"] 
	
		# create a frame to hold the button, set up for nice layout
		f = javax.swing.JFrame("Speed Matching Table Input Panel")		# argument is the frames title
		f.setLocation(120,50)  # 120 units from left edge, 50 units down from top. 1200 is off the right edge!
		f.contentPane.setLayout(javax.swing.BoxLayout(f.contentPane, javax.swing.BoxLayout.Y_AXIS))

		# create the DCC text field
		self.dccaddress = javax.swing.JTextField(5)	# sized to hold 5 characters, initially empty

		# put the text field on a line preceded by a label
		temppanel1 = javax.swing.JPanel()
		temppanel1.add(javax.swing.JLabel("          DCC Address"))
		temppanel1.add(self.dccaddress)

		# create the LOCO text field
		self.locoaddress = javax.swing.JTextField(5)	# sized to hold 5 characters, initially empty

		# put the LOCO text field on a line preceded by a label
		temppanel5 = javax.swing.JPanel()
		temppanel5.add(javax.swing.JLabel("         Locomotive number"))
		temppanel5.add(self.locoaddress)
		
# create the momentum value fields
		self.cv3 = javax.swing.JTextField(3)	# sized to hold 3 characters, initially empty
		self.cv4 = javax.swing.JTextField(3)	# sized to hold 3 characters, initially empty

		# put the text field on a line preceded by a label
		temppanel4 = javax.swing.JPanel()
		temppanel4.add(javax.swing.JLabel("  cv3 "))
		temppanel4.add(self.cv3)
		temppanel4.add(javax.swing.JLabel("  cv4 "))
		temppanel4.add(self.cv4)
#TLS changed default to 4
		self.cv3.setText("0")		#Prefer to have at least a little Acceleration momentum as a standard.
		self.cv4.setText("0")		#Prefer to have at least a little Deceleration momentum as a standard.

				
		# create the start button
		self.startButton = javax.swing.JButton("Start")
		self.startButton.actionPerformed = self.whenMyButtonClicked

		self.status = javax.swing.JLabel("Enter Locomotive and DCC Addresses and press Start")
		
		self.Scale = javax.swing.JComboBox()
#		self.Scale.addItem("Choose a Scale")
#changed default to N for the club
		self.Scale.addItem("N Scale")
		self.Scale.addItem("HO Scale")
		

		self.Locomotive = javax.swing.JComboBox()
		self.Locomotive.addItem("Diesel")
		self.Locomotive.addItem("Steam")

		self.SetDirection = javax.swing.JComboBox()
		self.SetDirection.addItem("Forward")
		self.SetDirection.addItem("Reverse")

		self.MaxSpeed = javax.swing.JTextField(3)

		temppanel3 = javax.swing.JPanel()
		temppanel3.add(javax.swing.JLabel("Maximum Speed"))
		temppanel3.add(self.MaxSpeed)

		self.DecoderBrand = javax.swing.JComboBox(DecoderList)

		# Put contents in frame and display
		f.contentPane.add(temppanel5)
		f.contentPane.add(temppanel1)
		temppanel2 = javax.swing.JPanel()
		f.contentPane.add(self.Scale)
		f.contentPane.add(self.Locomotive)
		f.contentPane.add(self.DecoderBrand)
		f.contentPane.add(temppanel4)
		f.contentPane.add(self.SetDirection)
		f.contentPane.add(temppanel3)
		temppanel2.add(self.startButton)
		f.contentPane.add(temppanel2)
		f.contentPane.add(self.status)
		f.pack()
		f.show()

		return
#---------------------------------------------------------------
# create one of these
a = AutoSpeedTable()


# set the name, as a example of configuring it
a.setName("Automated Speed Table")

# and show the initial panel
a.setup()
