import binascii
import sys

# with key 18993 the message:
# "Today's PIN:4444" gives us
# 1E5E2E50331639111A78040B7E057E05

def int2bytearray(i):
	answer = []
	answer.append(i >> 8)
	answer.append(i & 0xff)
	return answer

# message: plaintext input
# key: POCSAG capcode (e.g. 'J1' == 18993)
def xorDecrypt(message, key):
	result = ""
	keyarry = int2bytearray(key)
	keyindex = 0
	messageLength = len(message)
	msgindex = 0
	keyLength = len(keyarry)
	while (msgindex < messageLength):
		result += binascii.hexlify(chr(ord(message[msgindex]) ^ 
			keyarry[keyindex])).upper()
		msgindex += 1
		keyindex = (keyindex + 1) % keyLength	
	return result

def usage():
	print "Usage:", sys.argv[0], "<encrypted message (hex)> <decryption key (int)>"
	print "  Example:", sys.argv[0], "1e5e2e50 18993"
	exit(1)

if len(sys.argv) < 3:
	usage()

if len(sys.argv) == 4 and sys.argv[3] == 'r':
	reverse = True
else:
	reverse = False

try:
	key = int(sys.argv[2])
	if reverse:
		message = sys.argv[1]
	else:
		message = binascii.unhexlify(sys.argv[1])
	print "plain: ", binascii.unhexlify(xorDecrypt(message, key))
	print "hex: ", xorDecrypt(message, key)
except:
	e = sys.exc_info()[0]
	print "Invalid input, ensure that input parameters are hex and int"
	print e
	usage()

