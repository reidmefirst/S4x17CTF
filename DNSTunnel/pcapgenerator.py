import zlib
import struct # cheap to swap endianness of timestamps
port = 53

#Custom Foo Protocol Packet
message =  ('01 01 00 08'   #Foo Base Header
            '01 02 00 00'   #Foo Message (31 Bytes)
            '00 00 12 30'   
            '00 00 12 31'
            '00 00 12 32' 
            '00 00 12 33' 
            '00 00 12 34' 
            'D7 CD EF'      #Foo flags
            '00 00 12 35')     
# DNS request format:
# Transaction ID (2 bytes)
# Query Flags (bitfields, 2 bytes, value 0x0100 means standard query)
# Question count (2 bytes)
# Answer count (2 bytes)
# Authority RR count (2 bytes)
# Additional RR count (2 bytes)

# Queries themselves, which are strings of variable length...
def buildQuery(data, packetNumber):
  print "Debug: ",
  message = ('II II' # transaction id
             '01 00' # flags
             '00 01' # question count
             '00 00' # answer count
             '00 00' #authority count
             '00 00' # additional count
            )
  message = message.replace('II II', "%04x" % packetNumber)
  for chunk in data.split("."):
    message += ' %02x' % len(chunk)
    print "chunking message:", 
    for c in chunk:
      print " %02x" % ord(c),
      message += ' %02x' % ord(c)
  message += ' 00'
  message += (' 00 01 00 01') # standard Type A, Class IN query
  return message

# build response packet
def buildResponse(query, packetNumber):
  message = ('II II' '81 80' # TID, Flags
             '00 00' # question count
             '00 01' # answer count
             '00 00' # authority count
             '00 00' # additional count
            )
  message = message.replace('II II', "%04x" % packetNumber)
  for chunk in query.split("."):
    message += ' %02x' % len(chunk)
    for c in chunk:
      message += ' %02x' % ord(c)
  message += ' 00'
  message += '00 01' # type A query
  message += '00 01' # Class IN
  #message += 'c0 0c 00 01 00 01' # answer header: type a, class IN
  message += "00 00 00 01"
  #message += '00 01' # ttl: 1 second?
  message += '00 04' # response length
  hostchunk = query.split('.')[0]
  respIP = binascii.crc32(hostchunk) & 0xffffffff
  message += "%08x" % respIP
  return message

"""----------------------------------------------------------------"""
""" Do not edit below this line unless you know what you are doing """
"""----------------------------------------------------------------"""

import sys
import binascii

#Global header for pcap 2.4
pcap_global_header =   ('D4 C3 B2 A1'   
                        '02 00'         #File format major revision (i.e. pcap <2>.4)  
                        '04 00'         #File format minor revision (i.e. pcap 2.<4>)   
                        '00 00 00 00'     
                        '00 00 00 00'     
                        'FF FF 00 00'     
                        '01 00 00 00')

#pcap packet header that must preface every packet
pcap_packet_header =   ('TT TT TT TT'   # Timestamp (seconds)
                        'MM MM MM MM'   # Timestamp (microseconds)
                        'XX XX XX XX'   #Frame Size (little endian) 
                        'YY YY YY YY')  #Frame Size (little endian)

ROBOT1MAC = '52 4F 42 4F 54 31'
ROBOT2MAC = '52 4F 42 4F 54 32'
ROBOT1IP = 'C0 A8 10 99'
ROBOT2IP = 'C0 A8 01 01'

eth_header =   ('R1MAC'     #Source Mac    
                'R2MAC'     #Dest Mac  
                '08 00')                #Protocol (0x0800 = IP)

HOST_HACKED = 'C0 A8 10 99'
HOST_DNS = 'C0 A8 01 01'
ip_header =    ('45'                    #IP version and header length (multiples of 4 bytes)   
                '00'                      
                'XX XX'                 #Length - will be calculated and replaced later
                '00 00'                   
                '40 00 40'                
                '11'                    #Protocol (0x11 = UDP)          
                'YY YY'                 #Checksum - will be calculated and replaced later      
                'R1 IP R1 IP'           #Source IP (Default: 127.0.0.1)         
                'R2 IP R2 IP')          #Dest IP (Default: 127.0.0.1) 

udp_header =   ('SS SS'                 #source port
                'XX XX'                 #Port - will be replaced later                   
                'YY YY'                 #Length - will be calculated and replaced later        
                '00 00')
                
def getByteLength(str1):
    return len(''.join(str1.split())) / 2


def openFile(filename):
    print "Debug: Opening file %s" % filename
    filehandle = open(filename, 'wb')
    initializePCAPFile(filehandle)
    return filehandle

def writeByteStringToFileHandle(bytestring, filehandle):
    bytelist = bytestring.split()
    print "Debug: converting data to hex",
    print bytelist
    bytes = binascii.a2b_hex(''.join(bytelist))
    filehandle.write(bytes)

def writeByteStringToFile(bytestring, filename):
    print "Debug: writing ",
    bytelist = bytestring.split()  
    print bytelist
    bytes = binascii.a2b_hex(''.join(bytelist))
    bitout = open(filename, 'wb')
    bitout.write(bytes)

# writes the header to pcapfile
def initializePCAPFile(filehandle):
    writeByteStringToFileHandle(pcap_global_header, filehandle)

def generatePacket(message, srcmac, dstmac, srcip, dstip, seconds, microseconds, srcport, dstport, openfilehandle):
    udp = udp_header.replace('XX XX', "%04x" % dstport)
    udp = udp.replace('SS SS', '%04x' % srcport)
    udp_len = getByteLength(message) + getByteLength(udp_header)
    udp = udp.replace('YY YY', "%04x" % udp_len)
    ip_len = udp_len + getByteLength(ip_header)

    ip = ip_header.replace('XX XX',"%04x"%ip_len)
    ip = ip.replace('R1 IP R1 IP', srcip)
    ip = ip.replace('R2 IP R2 IP', dstip)

    checksum = ip_checksum(ip.replace('YY YY', '00 00'))
    ip = ip.replace('YY YY', "%04x" % checksum)
    eth = eth_header.replace('R1MAC', srcmac)
    eth = eth.replace('R2MAC', dstmac)

    pcap_len = ip_len + getByteLength(eth)
    hex_str = "%08x" % pcap_len
    print "generatePacket(): pcap_len is %d" % pcap_len
    reverse_hex_str = hex_str[6:] + hex_str[4:6] + hex_str[2:4] + hex_str[:2]
    # we will have to update the pcap header (length field, etc)
    pcaph = pcap_packet_header.replace('XX XX XX XX', reverse_hex_str)
    pcaph = pcaph.replace('YY YY YY YY', reverse_hex_str)
    print "generatePacket(): pcaph is %s" % pcaph
    secondbytes = struct.unpack("<I", struct.pack(">I", seconds))[0]
    microsecondbytes = struct.unpack("<I", struct.pack(">I", microseconds))[0]
    pcaph = pcaph.replace('TT TT TT TT', "%08x" % secondbytes)
    pcaph = pcaph.replace('MM MM MM MM', "%08x" % microsecondbytes)
    print "generatePacket(): pcaph is %s" % pcaph
    print "generatePacket(): eth is %s" % eth
    bytestring = pcaph + eth + ip + udp + message
    writeByteStringToFileHandle(bytestring, openfilehandle)



def generatePCAP(message,port,pcapfile): 

    udp = udp_header.replace('XX XX',"%04x"%port)
    udp_len = getByteLength(message) + getByteLength(udp_header)
    udp = udp.replace('YY YY',"%04x"%udp_len)

    ip_len = udp_len + getByteLength(ip_header)
    ip = ip_header.replace('XX XX',"%04x"%ip_len)
    checksum = ip_checksum(ip.replace('YY YY','00 00'))
    ip = ip.replace('YY YY',"%04x"%checksum)
    
    pcap_len = ip_len + getByteLength(eth_header)
    hex_str = "%08x"%pcap_len
    reverse_hex_str = hex_str[6:] + hex_str[4:6] + hex_str[2:4] + hex_str[:2]
    pcaph = pcap_packet_header.replace('XX XX XX XX',reverse_hex_str)
    pcaph = pcaph.replace('YY YY YY YY',reverse_hex_str)

    bytestring = pcap_global_header + pcaph + eth_header + ip + udp + message
    writeByteStringToFile(bytestring, pcapfile)

#Splits the string into a list of tokens every n characters
def splitN(str1,n):
    return [str1[start:start+n] for start in range(0, len(str1), n)]

#Calculates and returns the IP checksum based on the given IP Header
def ip_checksum(iph):

    #split into bytes    
    words = splitN(''.join(iph.split()),4)

    csum = 0;
    for word in words:
        csum += int(word, base=16)

    csum += (csum >> 16)
    csum = csum & 0xFFFF ^ 0xFFFF

    return csum


"""------------------------------------------"""
""" End of functions, execution starts here: """
"""------------------------------------------"""
if __name__ == "__main__":
  if len(sys.argv) < 2:
        print 'usage: pcapgen.py output_file'
        exit(0)

  generatePCAP(buildQuery('FOO.bar.com', 1),port,sys.argv[1])  
  #generatePCAP(buildQuery('6a986yfFhWCDQEz8sgKAp2zktGpZsnnPVf4FTrzij4QKnYbrbTH7Ao1VvxwgNM8o5WbMWz5ztxjb5KJXysFTnhjutDDEt8K9vYqjRabEBmHSxDgNRnaYGLKgWbChy8agbYbGXyYg73pFJEuPTe1HazAdozGXVMycq8keLwjoweFVnvf3vF3MVMrMmDfKEjh1H7b9Q6RQtHU6o7iujSHT8B7doSUZiSphVAe3C.b58.killerrobotsinc.com'), port, sys.argv[1])
