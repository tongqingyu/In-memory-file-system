import pickle, logging
import hashlib
import sys

from memoryfs_client import BLOCK_SIZE, TOTAL_NUM_BLOCKS
# from memoryfs_client import RSM_LOCKED

## checksum parameter
## 128 bits checksum
CHECKSUM_SIZE = 16
CHECKSUM_PER_BLOCK = BLOCK_SIZE//CHECKSUM_SIZE
TOTAL_CHECKSUM = TOTAL_NUM_BLOCKS*2
TOTAL_CHECKSUM_BLOCK = TOTAL_CHECKSUM //CHECKSUM_PER_BLOCK

from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.server import SimpleXMLRPCRequestHandler

# Restrict to a particular path.
class RequestHandler(SimpleXMLRPCRequestHandler):
  rpc_paths = ('/RPC2',)
  
# This class stores the raw block array
class DiskBlocks():
  def __init__(self):
    self.block = []                                            
    # Initialize raw blocks 
    for i in range (0, TOTAL_NUM_BLOCKS):
      putdata = bytearray(BLOCK_SIZE)
      self.block.insert(i,putdata)

# This class stores the checksum 
class ExtraBlocks():
  def __init__(self):
    self.block=[]
    # Initailize checksum blocks
    for i in range(0,TOTAL_CHECKSUM_BLOCK):
      self.block.append([])
      for j in range(0, CHECKSUM_PER_BLOCK):
        putdata = bytearray(CHECKSUM_SIZE)
        self.block[i].insert(j,putdata)

if __name__ == "__main__":

  RawBlocks = DiskBlocks()
  checksumBlocks = ExtraBlocks()
  
  # Create server
  port = sys.argv[1]
  port = int(port)
  server = SimpleXMLRPCServer(("localhost", port), requestHandler=RequestHandler) 
  
  # Error emulation
  if len(sys.argv) == 3:
      errorblock = sys.argv[2]
      errorblock = int(errorblock)
      string ="istilltry"
      errordata = bytearray(string,'utf-8')
      # RawBlocks.block[errorblock] = errordata
      RawBlocks.block[errorblock] = bytearray(errordata.ljust(BLOCK_SIZE,b'\x00')) 

  # checksumCalculation:calcute checksum
  def chechsumCalculation(physical_block_number):
      data = RawBlocks.block[physical_block_number]
      data_str = str(data)
      data_bytes = bytes(data_str,'utf-8')
      # digest() return encoded in byte format
      result = hashlib.md5(data_bytes).digest()
      
      return result

  # find the location of checksum  
  def checksumLocation(physical_block_number):

    index_of_block = physical_block_number//CHECKSUM_PER_BLOCK
    index_within_block = physical_block_number%CHECKSUM_PER_BLOCK
    
    return index_of_block, index_within_block


  # Get: acquire data from the server and return to the client
  def Get(physical_block_number):

    ## verify checksum
    index_of_block,index_within_block = checksumLocation(physical_block_number)
    stored_checksum = checksumBlocks.block[index_of_block][index_within_block]
    computed_checksum = chechsumCalculation(physical_block_number)
    
    if computed_checksum != stored_checksum:
        errordata = bytearray('error','utf-8')
        errormessage = bytearray(errordata.ljust(BLOCK_SIZE,b'\x00'))
        return errormessage

    result = RawBlocks.block[physical_block_number]
    
    return result

  server.register_function(Get)

  # Put: put data into server
  def Put(physical_block_number,putdata):

      # Put rawdata
      # corruption emulation
      if len(sys.argv) != 3:
          RawBlocks.block[physical_block_number] = putdata
      elif physical_block_number != sys.argv[2]:
          RawBlocks.block[physical_block_number] = putdata
      
      # Put checksum
      checksum = chechsumCalculation(physical_block_number)
      index_of_block,index_within_block = checksumLocation(physical_block_number)
      checksumBlocks.block[index_of_block][index_within_block] = checksum

      return 0

  server.register_function(Put)

#  def RSM(block_number):
#    result = RawBlocks.block[block_number]
#    RawBlocks.block[block_number] = RSM_LOCKED
#    # RawBlocks.block[block_number] = bytearray(RSM_LOCKED.ljust(BLOCK_SIZE,b'\x01'))
#    return result

#  server.register_function(RSM)

  # Run the server's main loop
  server.serve_forever()

