import sys
import socket
import time
import threading

PACKET_SIZE = 10
SEQUENCE_NUMBER_SIZE = 4
BODY_DATA_SIZE = PACKET_SIZE - SEQUENCE_NUMBER_SIZE
recvAddr = None
windowSize = None
srcFilename = None
dstFilename = None
startTime = None
windowTopIndex = None
packetList = []

"Use this method to write Packet log"
def writePkt(logFile, procTime, pktNum, event):
    logFile.write('{:1.3f} pkt: {} | {}'.format(procTime, pktNum, event))

"Use this method to write ACK log"
def writeAck(logFile, procTime, ackNum, event):
    procTime = time.time() - startTime
    logFile.write('{:1.3f} ACK: {} | {}'.format(procTime, ackNum, event))

"Use this method to write final throughput log"
def writeEnd(logFile, throughput, avgRTT):
    logFile.write('File transfer is finished.')
    logFile.write('Throughput : {:.2f} pkts/sec'.format(throughput))
    logFile.write('Average RTT : {:.1f} ms'.format(avgRTT))

def fileSender():
    print('sender program starts...') #remove this

    ##########################
    
    #Write your Code here
    f = open(srcFilename, 'r')
    fileData = f.read()
    f.close()

    entireDataBytes = (dstFilename + '\n' + fileData).encode()

    makePacketList(entireDataBytes)

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    send(sock)

    sock.close()
    ##########################

def send(sock):
    lenOfPacketList = len(packetList)

    for i in range(0, windowSize):
        if (i is lenOfPacketList):
            break
        
        sock.sendto(packetList[i], (recvAddr, 10080))


def makePacketList(entireDataBytes):
    lenOfEntireDataBytes = len(entireDataBytes)

    sequenceNumber = 0
    while sequenceNumber * BODY_DATA_SIZE < lenOfEntireDataBytes:
        initialIndex = sequenceNumber * BODY_DATA_SIZE
        bodyData = entireDataBytes[initialIndex:initialIndex + BODY_DATA_SIZE]

        packet = makePacket(sequenceNumber, bodyData)

        packetList.append(packet)
        sequenceNumber += 1

def makePacket(sequenceNumber, data):
    sequenceNumberData = []
    for i in range(0, SEQUENCE_NUMBER_SIZE):
        a = (sequenceNumber >> 32 * (SEQUENCE_NUMBER_SIZE - 1 - i)) & 0xFF
        sequenceNumberData.append(a)
    sequenceNumberByteData = bytes(sequenceNumberData)
    
    packet = sequenceNumberByteData + data

    return packet


if __name__=='__main__':
    recvAddr = sys.argv[1]  #receiver IP address
    windowSize = int(sys.argv[2])   #window size
    srcFilename = sys.argv[3]   #source file name
    dstFilename = sys.argv[4]   #result file name

    fileSender()
