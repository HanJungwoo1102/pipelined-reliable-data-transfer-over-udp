import sys
import socket
import time
import threading

PACKET_SIZE = 1000
SEQUENCE_NUMBER_SIZE = 4
BODY_DATA_SIZE = PACKET_SIZE - SEQUENCE_NUMBER_SIZE
recvAddr = None
windowSize = None
srcFilename = None
dstFilename = None
startTime = time.time()
packetList = []
timerTime = None
BUFSIZE = 1024
logFilename = 'sender_log.txt'
logFile = None
PORT = 10080
windowTopIndex = 0
lastSendedPacketIndex = -1

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
    global windowTopIndex
    global packetList
    
    #Write your Code here
    f = open(srcFilename, 'r')
    fileData = f.read()
    f.close()

    logFile = open(logFilename, 'w')
    logFile.write('')
    logFile.close()

    makePacketList(fileData)


    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    t = threading.Thread(target=receive, args=(sock, ))
    t.start()
    
    send(sock, 0, windowSize, 'sent')

    lenOfPacketList = len(packetList)
    while windowTopIndex < lenOfPacketList:
        rtt = time.time() - timerTime
        if rtt > 1:
            procTime = time.time() - startTime
            writePkt(logFile, procTime, windowTopIndex, 'timeout since {:1.3f}(timeout value 1.0)'.format(rtt))
            send(sock, windowTopIndex, windowTopIndex + 1, 'retransmitted')
    
    ##########################

def send(sock, startIndex, endIndex, event):
    global timerTime
    global windowSize
    global startTime
    global recvAddr
    global packetList
    global lastSendedPacketIndex
    lenOfPacketList = len(packetList)

    maxSendedPacketIndex = -1
    for i in range(startIndex, endIndex):

        if i >= lenOfPacketList:
            break
        else:

            sock.sendto(packetList[i], (recvAddr, PORT))
            # 패킷 보냄
            timerTime = time.time()
            procTime = time.time() - startTime
            writePkt(logFile, procTime, i, event)
            maxSendedPacketIndex = i

    if lastSendedPacketIndex < maxSendedPacketIndex:
        lastSendedPacketIndex = maxSendedPacketIndex

def receive(sock):
    global packetList
    global BUFSIZE
    global SEQUENCE_NUMBER_SIZE
    global timerTime
    global windowTopIndex
    global lastSendedPacketIndex
    duplicateCount = 0

    lenOfPacketList = len(packetList)

    while windowTopIndex < lenOfPacketList:
        packet, address = sock.recvfrom(BUFSIZE)

        ackNumber = 0
        for i in range(0, SEQUENCE_NUMBER_SIZE):
            ackNumber += packet[i] << (SEQUENCE_NUMBER_SIZE - 1 - i) * 32
        
        procTime = time.time() - startTime
        writeAck(logFile, procTime, ackNumber, 'received')
        # ack 받음

        if ackNumber == windowTopIndex - 1:
            duplicateCount += 1

            if duplicateCount >= 3:
                procTime = time.time() - startTime
                writeAck(logFile, procTime, ackNumber, '3 ack duplicated')
                send(sock, windowTopIndex, windowTopIndex + 1, 'retransmitted')
        elif ackNumber >= windowTopIndex:
            windowTopIndex = ackNumber + 1
            duplicateCount = 0
            # 윈도우 슬라이드

            send(sock, lastSendedPacketIndex + 1, windowTopIndex + windowSize, 'additional sent')

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
