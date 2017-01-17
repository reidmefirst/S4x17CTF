import zlib
import sys
import base64
import base58
import pcapgenerator
import random

inFile = open(sys.argv[1], 'rb')

domain = 'b58.killerrobotsinc.com'

#chunksize = 252 - len(domain)
chunksize = 20 # let's try this
inData = inFile.read()

outData = base58.b58encode(inData) # zlib.compress(inData))

size = len(outData)

print "Debug: Built output data"
print "Debug: output size: %d bytes" % size

chunks = size / chunksize # full chunks
if (size % chunksize):
  chunks += 1
print "starting chunking"
pcapfilehandle = pcapgenerator.openFile("output.pcap")
time_start = 0x5874a7aa # corresponds to Tuesday, January 10th
# note: we'll have to do some fancy endian conversion on time_start
time = time_start
for i in range(0, chunks):
  time = time + 2 # round-trip time for ACK message
  ms = random.randrange(0, 2**10)  
  query=outData[(i*chunksize):((i+1)*chunksize)] + '.' + domain
  print "Query: %s" % query
  pcapgenerator.generatePacket(pcapgenerator.buildQuery(query, i), pcapgenerator.ROBOT1MAC, pcapgenerator.ROBOT2MAC, pcapgenerator.ROBOT1IP, pcapgenerator.ROBOT2IP, time, ms, 32769, 53, pcapfilehandle)
  ms = random.randrange(0, 2**10)
  if i == 1000:
    print "Duplicating packet 1000"
    # don't send an ack
    # instead simulate a timeout!
    time = time + 2
    ms = random.randrange(0, 2**10)
    pcapgenerator.generatePacket(pcapgenerator.buildQuery(query, i), pcapgenerator.ROBOT1MAC, pcapgenerator.ROBOT2MAC, pcapgenerator.ROBOT1IP, pcapgenerator.ROBOT2IP, time, ms, 32769, 53, pcapfilehandle)
  pcapgenerator.generatePacket(pcapgenerator.buildResponse(query, i), pcapgenerator.ROBOT2MAC, pcapgenerator.ROBOT1MAC, pcapgenerator.ROBOT2IP, pcapgenerator.ROBOT1IP, time + 1, ms, 53, 32769, pcapfilehandle)

