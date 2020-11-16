import sys
import socket
import time

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


def fileSender(recvAddr, windowSize, srcFilename, dstFilename):
    print('sender program starts...') #remove this

    ##########################
    
    #Write your Code here

    PACKET_SIZE = 10
    SEQUENCE_NUMBER_SIZE = 4
    BODY_DATA_SIZE = PACKET_SIZE - SEQUENCE_NUMBER_SIZE

    f = open(srcFilename, 'r')
    fileData = f.read()
    f.close()

    entireDataBytes = (srcFilename + '\n' + fileData).encode()
    lenOfEntireDataBytes = len(entireDataBytes)

    packetList = []

    sequenceNumber = 0
    while sequenceNumber * BODY_DATA_SIZE < lenOfEntireDataBytes:
        sequenceNumberData = []
        for i in range(0, 4):
            a = (sequenceNumber >> 32 * (3 - i)) & 0xFF
            sequenceNumberData.append(a)
        sequenceNumberByteData = bytes(sequenceNumberData)
        initialIndex = sequenceNumber * BODY_DATA_SIZE
        bodyData = entireDataBytes[initialIndex:initialIndex + BODY_DATA_SIZE]
        packet = sequenceNumberByteData + bodyData
        packetList.append(packet)
        sequenceNumber += 1

    print(packetList)

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    sock.sendto(packetList[0], (recvAddr, 10080))

    sock.close()
    ##########################


if __name__=='__main__':
    recvAddr = sys.argv[1]  #receiver IP address
    windowSize = int(sys.argv[2])   #window size
    srcFilename = sys.argv[3]   #source file name
    dstFilename = sys.argv[4]   #result file name

    fileSender(recvAddr, windowSize, srcFilename, dstFilename)
