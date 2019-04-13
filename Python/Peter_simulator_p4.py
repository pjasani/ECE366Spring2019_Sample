# Supported instructions along with some assumptions:
#   ori: I-type, assuming zero extension
#   addi: I-type, assuming sign extension, can deal with negative numbers in 2's cmp
#   sub: R-type, assuming registers containing numbers in 2's cmp
#   beq: I-type, with the following functionality:
#       if rs == rt, pc = pc+4+(imm<<2)
#       if rs != rt, pc = pc+4

# run with Python3
# There's some poor coding habits in this. 

from math import log, ceil
import random 

MEM_SPACE = 1024	#4-byte word accessible memory space 
Memory = [0 for i in range(MEM_SPACE)] 

# This memory space will correspond to the address spaces 0x2000 - 0x3000 when used by lw (and sw if it were implemented)
# 0x1000 == 0d4096, and 4096 / 4 == 1024, thus 1024 words

class Block:
	def __init__(self, _wordsPerBlock, _whichSet):
		self.data = [ 0 for i in range( _wordsPerBlock ) ]
		self.size = _wordsPerBlock
		self.setIndex = format( whichSet, 'b' ) # Since this is a direct-mapped cache, I can get away with combining the block and set class
							# Blocks and set are not the same thing though. 
		self.valid = False 
		self.tag = "undefined"
	def LoadBlock(self, memIndex, tag ):
		self.tag = tag
		self.valid = True
		for i in range( self.size ): 
			self.data[i] = Memory[i +  memIndex ] 
		

class Cache:
	def __init__(self, _wordsPerBlock):
		self.Cache = [] 		
		for i in range( 8 ): 		
			tempBlock = Block( _wordsPerBlock, i )
			self.Cache.append( tempBlock )
		self.wordsPerBlock = _wordsPerBlock
		self.blockCount = 8 

	#Have this function return 1 if valid && tag match, -1 if not valid && tag doesn't match
	def CheckBlockTag( self, tag ):
		pass

	def AccessCache( self, addr, outFile):		
		inBlkOffset = addr[-( 2 + ceil( log( self.wordsPerBlock, 2) ) ): -2]
		setIndex = addr[-( 2 + 3 + ceil( log( self.wordsPerBlock, 2) ) )]:-( 2 + ceil( log( self.wordsPerBlock, 2) ) )]
		tag = addr[:-( 2 + 3 + ceil( log( self.wordsPerBlock, 2) ) )]
		zeroString = ""
		for i in range( ceil( log( self.wordsPerBlock, 2 ) ):	#There might be a bug here with this loop if wordsPerBlock is 1 or 0
			zeroString = zeroString + "0"  
		memIndex = int( tag + setIndex + zeroString, 2 ) - 2048

def simulate( instructions, instructionsHex, debugMode, program):

	outFile = open("output_" + program , "w")
	registers = [0, 0, 0, 0, 0, 0, 0, 0]
	programDone = False
	PC = 0		#program counter 
	DIC = 0 	#dynamic instruction count
	#counters
	Cycle = 0
	threeCycles = 0     
	fourCycles = 0      
	fiveCycles = 0		#no five cycle instructions supported 
	pipelineCycles = 4

	print( "Starting simulation..." )
	while ( not( programDone ) ):
		fetch = instructions[PC]
		if ( fetch[0:32] == "00010000000000001111111111111111" ):
			programDone = True
			DIC += 1
		elif ( fetch[0:6] == "001000" ):	#addi
			imm = int( fetch[16:32],2 ) if fetch[16] == '0' else -( 65536 - int( fetch[16:32],2 ) ) #range of number for 16 bit unsigned is 0 to 65535
			if ( debugMode ):
				print("Cycle " + str(Cycle) + " for multi-cycle:")
				print("PC =" + str(PC*4) + " Instruction: 0x" +  instructionsHex[PC] + " :" + "addi $" + str(int(fetch[11:16],2)) + ",$" + str(int(fetch[6:11],2)) + ", " + str(imm) )
				print("Taking 4 cycles for multi-cycle\n")
			outFile.write("Cycle " + str(Cycle) + " for multi-cycle:\n")
			outFile.write("PC =" + str(PC*4) + " Instruction: 0x" +  instructionsHex[PC] + " :" + "addi $" + str(int(fetch[11:16],2)) + ",$" + str(int(fetch[6:11],2)) + ", " + str(imm) + "\n" )
			outFile.write("Takes 4 cycles for multi-cycle\n\n")
			PC += 1
			Cycle += 4
			fourCycles += 1
			pipelineCycles += 1
			DIC += 1
			registers[int(fetch[11:16], 2)] = registers[int(fetch[6:11], 2)] + imm
		elif ( fetch[0:6] == "001101" ):	#ori
			imm = int( fetch[16:32],2 ) if fetch[16] == '0' else -( 65536 - int( fetch[16:32],2 ) ) #range of number for 16 bit unsigned is 0 to 65535
			if ( debugMode ):
				print("Cycle " + str(Cycle) + " for multi-cycle:")
				print( "PC = " + str(PC*4) + " Instruction: 0x" +  instructionsHex[PC] + " :" + "ori $" + str(int(fetch[6:11],2)) + ",$" + str(int(fetch[11:16],2)) + "," + str(imm) )
				print("Takes 4 cycles for multi-cycle\n")
			outFile.write( "Cycle " + str(Cycle) + " for multi-cycle:" )
			outFile.write( "PC = " + str(PC*4) + " Instruction: 0x" +  instructionsHex[PC] + " :" + "ori $" + str(int(fetch[6:11],2)) + ",$" + str(int(fetch[11:16],2)) + "," + str(imm) )
			outFile.write( "Takes 4 cycles for multi-cycle\n" )
			imm = int( fetch[16:32],2 )	#I'm basically ignoring the fact that this could be a negative number since it we're zero-extending it.
			PC += 1
			Cycle += 4
			fourCycles += 1
			pipelineCycles += 1
			DIC += 1
			registers[int(fetch[11:16], 2)] = registers[int(fetch[6:11], 2)] | imm
		elif ( fetch[0:6] == "000000" ):	#sub
			#rs = int( fetch[6:11],2 )
			#rt = int( fetch[11:16],2 )
			#rd = int(fetch[16:21],2)
			if ( debugMode ):
				print("Cycle " + str(Cycle) + " for multi-cycle:")
				print("PC =" + str(PC*4) + " Instruction: 0x" +  instructionsHex[PC] + " :" + "sub $" + str(int(fetch[16:21],2)) + ",$" + str(int(fetch[6:11],2)) + ",$" + str(int(fetch[11:16],2)) )
				print("Takes 4 cycles for multi-cycle\n")
			outFile.write("Cycle " + str(Cycle) + " for multi-cycle:\n")
			outFile.write("PC =" + str(PC*4) + " Instruction: 0x" +  instructionsHex[PC] + " :" + "sub $" + str(int(fetch[16:21],2)) + ",$" + str(int(fetch[6:11],2)) + ",$" + str(int(fetch[11:16],2)) + "\n" )
			outFile.write("Takes 4 cycles for multi-cycle\n\n")
			PC += 1
			Cycle += 4
			fourCycles += 1
			pipelineCycles += 1
			DIC += 1
			registers[int(fetch[16:21], 2)] = registers[int(fetch[6:11], 2)] - registers[int(fetch[11:16], 2)]
		elif ( fetch[0:6] == "000100" ):	#beq
			imm = int( fetch[16:32],2 ) if fetch[16] == '0' else -( 65536 - int( fetch[16:32],2 ) )
			if ( debugMode ):
				print("Cycle " + str(Cycle) + " for multi-cycle:")
				print("PC =" + str(PC*4) + " Instruction: 0x" +  instructionsHex[PC] + " :" + "beq $" + str(int(fetch[6:11],2)) + ",$" +str(int(fetch[11:16],2)) + "," + str(imm) )
				print("Takes 3 cycles for multi-cycle\n")
			outFile.write("Cycle " + str(Cycle) + " for multi-cycle:\n")
			outFile.write("PC =" + str(PC*4) + " Instruction: 0x" +  instructionsHex[PC] + " :" + "beq $" + str(int(fetch[6:11],2)) + ",$" +str(int(fetch[11:16],2)) + "," + str(imm) + "\n" )
			outFile.write("Takes 3 cycles for multi-cycle\n\n")
			Cycle += 3
			threeCycles += 1
			pipelineCycles += 1
			PC += 1
			DIC += 1
			if ( registers[int(fetch[6:11], 2)] == registers[int(fetch[11:16], 2)] ):
				PC = PC + imm
		else:
			print( "Unsupported instruction, ending simulator..." )
			programDone = True
	print( "Simulation complete. Now printing register information:" )
	counter = 0
	for register in registers:
		print( "Register " + str( counter ) + ": " + str( register ) )
		counter += 1
	print( "***********************************************************************\n" )
	print( "Dynamic instructions count: " +str(DIC) + "\n\n" )
	print( "PC: " + str( PC ) )
	print("Dynamic instructions count: " +str(DIC) + "\n\n")
	print("Total # of cycles for multi-cycle: " + str(Cycle) + "\n")
	print("                    " + str(threeCycles) + " instructions take 3 cycles\n" )
	print("                    " + str(fourCycles) + " instructions take 4 cycles\n" )
	print("                    " + str(fiveCycles) + " instructions take 5 cycles\n\n" )
	print( "Total cycles for pipelined CPU: "+ str( pipelineCycles ) + "\n\n" )

	outFile.write("***********************************************************************\n")
	outFile.write("Dynamic instructions count: " +str(DIC) + "\n\n")
	outFile.write("Total # of cycles for multi-cycle: " + str(Cycle) + "\n")
	outFile.write("                    " + str(threeCycles) + " instructions take 3 cycles\n" )
	outFile.write("                    " + str(fourCycles) + " instructions take 4 cycles\n" )
	outFile.write("                    " + str(fiveCycles) + " instructions take 5 cycles\n\n" )
	outFile.write( "Total cycles for pipelined CPU: "+ str( pipelineCycles ) + "\n\n" )
	outFile.close()

def main():
	print( "Note: This program assumes that the instructions are in hex." )
	fileName = input( "Please enter MIPS instruction file name: " )
	inputFile = open( fileName, "r" )
	instructions = []	# Declares instructions to be an array
	instructionsHex = []
	for line in inputFile:
		if ( line == "\n" or line[0] =='#' ):              # empty lines and comments ignored
			continue

		line = line.replace( '\n', '' )	# Removes new line characters
		line = line.replace( ' ', '' ) 
		instructionsHex.append( line )
		line = format( int( line, 16 ), "032b" )	# The int function converts the hex instruction into some numerical value, then format converts it into a binary string 
		instructions.append( line )
	inputFile.close()
	debugMode = True if  int( input( "1 = debug mode         2 = normal execution\n" ) ) == 1 else False
	programName = fileName.replace( ".txt", "" )
	simulate( instructions, instructionsHex, debugMode, programName )


if __name__ == "__main__":
    main()
