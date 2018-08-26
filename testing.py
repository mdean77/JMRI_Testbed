class testing:
	numer = 9
	def testScope(self):
		self.thing = "Mike"
		
		def innerScope(self):
			print(self.thing)
			print(self.numer)
			print(self.thing)
			print(self.numer)
			print(self.thing)
			print(self.numer)
			print(self.thing)
			print(self.numer)
			
		innerScope(self)
	print(numer)
	print(42)
	print(54)
	
	def anotherScope(self):
		print(self.thing)
		print(str.lower(self.thing))
	

a = testing()
a.testScope()
a.anotherScope()


