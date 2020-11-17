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
startTime = time.time()
windowTopIndex = 0
packetList = []
timerTime = None
BUFSIZE = 1024
logFilename = 'sender_log.txt'
logFile = None

"Use this method to write Packet log"
def writePkt(logFile, procTime, pktNum, event):
    logFile = open(logFilename, 'a')
    logFile.write('{:1.3f} pkt: {} | {}\n'.format(procTime, pktNum, event))
    logFile.close()

"Use this method to write ACK log"
def writeAck(logFile, procTime, ackNum, event):
    logFile = open(logFilename, 'a')
    logFile.write('{:1.3f} ACK: {} | {}\n'.format(procTime, ackNum, event))
    logFile.close()

"Use this method to write final throughput log"
def writeEnd(logFile, throughput, avgRTT):
    logFile.write('File transfer is finished.\n')
    logFile.write('Throughput : {:.2f} pkts/sec\n'.format(throughput))
    logFile.write('Average RTT : {:.1f} ms\n'.format(avgRTT))

def fileSender():
    print('sender program starts...') #remove this

    ##########################
    
    #Write your Code here
    f = open(srcFilename, 'r')
    fileData = f.read()
    f.close()

    logFile = open(logFilename, 'w')
    logFile.write('')
    logFile.close()

    makePacketList(fileData)

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    send(sock)

    sock.close()
    ##########################

def send(sock):
    global timerTime
    global windowTopIndex
    global windowSize
    global startTime
    global recvAddr
    global packetList

    lenOfPacketList = len(packetList)

    for i in range(windowTopIndex, windowTopIndex + windowSize):
        if (i >= lenOfPacketList):
            break
        
        timerTime = time.time()
        sock.sendto(packetList[i], (recvAddr, 10080))
        # 패킷 보냄
        procTime = time.time() - startTime
        writePkt(logFile, procTime, i, 'sent')

def receive(sock):
    global windowTopIndex
    global packetList
    global BUFSIZE
    global SEQUENCE_NUMBER_SIZE

    duplicateCount = 0

    lenOfPacketList = len(packetList)
    while windowTopIndex < lenOfPacketList:
        packet, address = sock.recvfrom(BUFSIZE)

        ack = 0
        for i in range(0, SEQUENCE_NUMBER_SIZE):
            ack += packet[i] << (SEQUENCE_NUMBER_SIZE - 1 - i) * 32
        
        # ack 받음
        procTime = time.time() - startTime
        writeAck(logFile, procTime, ack, 'received')

        if ack == windowTopIndex:
            duplicateCount += 1
        else:
            windowTopIndex = ack

        if duplicateCount >= 3:
            procTime = time.time() - startTime()
            procTime = time.time() - startTime
            writeAck(logFile, procTime, ack, '3 ack duplicated')
        else:
            send(sock)

def makePacketList(fileData):
    fileDataBytes = fileData.encode()
    lenOfFileDataBytes = len(fileDataBytes)

    sequenceNumber = 0
    data = dstFilename.encode()
    packet = makePacket(sequenceNumber, data)
    packetList.append(packet)
    sequenceNumber += 1

    while (sequenceNumber - 1 ) * BODY_DATA_SIZE < lenOfFileDataBytes:
        initialIndex = (sequenceNumber - 1) * BODY_DATA_SIZE
        data = fileDataBytes[initialIndex:initialIndex + BODY_DATA_SIZE]

        packet = makePacket(sequenceNumber, data)
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
