import sys
import socket
import time
import threading

PACKET_SIZE = 1400
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
rttList = []
timeOutLimit = 0.1

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
    logFile = open(logFilename, 'a')
    logFile.write('File transfer is finished.\n')
    logFile.write('Throughput : {:.2f} pkts/sec\n'.format(throughput))
    logFile.write('Average RTT : {:.1f} ms\n'.format(avgRTT))
    logFile.close()

def fileSender():
    print('sender program starts...') #remove this

    ##########################
    global windowTopIndex
    global packetList
    global timerTime
    global startTime
    global timeOutLimit
    global rttList
    
    #Write your Code here
    f = open(srcFilename, 'rb')
    fileData = f.read()
    f.close()

    logFile = open(logFilename, 'w')
    logFile.write('')
    logFile.close()

    makePacketList(fileData)

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    t = threading.Thread(target=receive, args=(sock, ))
    t.start()
    lenOfPacketList = len(packetList)
    writePkt(logFile, lenOfPacketList, lenOfPacketList, 'packet count')
    for i in range(0, windowSize):
        if i + windowTopIndex >= lenOfPacketList:
            break
        else:
            sequenceNumber = i + windowTopIndex
            sock.sendto(packetList[sequenceNumber], (recvAddr, PORT))
            procTime = time.time() - startTime
            writePkt(logFile, procTime, i, 'sent')
            if i == 0:
                timerTime = time.time()
                # writeAck(logFile, procTime, sequenceNumber, 'timer start-----------------{:2.6f}'.format(procTime))
    
    while windowTopIndex < lenOfPacketList:
        t = timerTime
        if t is not None:
            timeoutSince = time.time() - t
            if timeoutSince > timeOutLimit:
                procTime = time.time() - startTime
                writePkt(logFile, procTime, windowTopIndex, 'timeout since {:1.3f}(timeout value {:1.3f})'.format(timeoutSince, timeOutLimit))
                sock.sendto(packetList[windowTopIndex], (recvAddr, PORT))
                procTime = time.time() - startTime
                writePkt(logFile, procTime, windowTopIndex, 'retransmitted')
                # timerTime = time.time()
                # # writeAck(logFile, procTime, windowTopIndex, 'timer start-----------------{:2.6f}'.format(procTime))
                # for i in range(windowTopIndex + 1, windowTopIndex + windowSize):
                #     if i >= lenOfPacketList:
                #         break
                #     sock.sendto(packetList[i], (recvAddr, PORT))
                #     procTime = time.time() - startTime
                #     writeAck(logFile, procTime, i, 'sent')
    
    sum = 0
    for rtt in rttList:
        sum += rtt
    
    avg = (sum * 1000) / len(rttList)

    totalTime = time.time() - startTime
    throughput = lenOfPacketList / totalTime

    writeEnd(logFile, throughput, avg)

    print('success')

    ##########################

def receive(sock):
    global packetList
    global BUFSIZE
    global SEQUENCE_NUMBER_SIZE
    global timerTime
    global windowTopIndex
    global lastSendedPacketIndex
    global rttList
    global timeOutLimit
    duplicateCount = 0
    lenOfPacketList = len(packetList)

    while windowTopIndex < lenOfPacketList:
        packet, address = sock.recvfrom(BUFSIZE)
        ackNumber = 0
        for i in range(0, SEQUENCE_NUMBER_SIZE):
            ackNumber += packet[i] << (SEQUENCE_NUMBER_SIZE - 1 - i) * 8
        procTime = time.time() - startTime
        writeAck(logFile, procTime, ackNumber, 'received')
        # ack 받음
        if ackNumber >= windowTopIndex:
            if timerTime is not None:
                rtt = time.time() - timerTime
                rttList.append(rtt)
                # writeAck(logFile, procTime, ackNumber, 'append rtt-----------------{:2.6f}'.format(rtt))
                sum = 0
                for i in rttList:
                    sum += i

                avg = sum / len(rttList)
                if avg > 0.1:
                    timeOutLimit = avg
                else:
                    timeOutLimit = 0.1
                timerTime = None
                # rtt 저장, rtt avg
        if ackNumber == windowTopIndex - 1:
            duplicateCount += 1
            if duplicateCount >= 3:
                procTime = time.time() - startTime
                writeAck(logFile, procTime, ackNumber, '3 ack duplicated')
                sock.sendto(packetList[windowTopIndex], (recvAddr, PORT))
                procTime = time.time() - startTime
                writeAck(logFile, procTime, windowTopIndex, 'retransmitted')
                timerTime = time.time()
                # writeAck(logFile, procTime, windowTopIndex, 'timer start-----------------{:2.6f}'.format(procTime))
                duplicateCount = 0
                for i in range(windowTopIndex + 1, windowTopIndex + windowSize):
                    if i >= lenOfPacketList:
                        break
                    sock.sendto(packetList[i], (recvAddr, PORT))
                    procTime = time.time() - startTime
                    writeAck(logFile, procTime, i, 'sent')
        elif ackNumber >= windowTopIndex:
            oldWindowTopIndex = windowTopIndex
            windowTopIndex = ackNumber + 1
            for i in range(0, windowTopIndex - oldWindowTopIndex):
                sequenceNumber = i + oldWindowTopIndex + windowSize
                if sequenceNumber >= lenOfPacketList:
                    break
                else:
                    sock.sendto(packetList[sequenceNumber], (recvAddr, PORT))
                    procTime = time.time() - startTime
                    writePkt(logFile, procTime, sequenceNumber, 'sent')
            duplicateCount = 0
            # 윈도우 슬라이드

def makePacketList(fileData):
    lenOfFileData = len(fileData)
    sequenceNumber = 0
    data = dstFilename.encode()
    packet = makePacket(sequenceNumber, data)
    packetList.append(packet)
    sequenceNumber += 1
    while (sequenceNumber - 1 ) * BODY_DATA_SIZE < lenOfFileData:
        initialIndex = (sequenceNumber - 1) * BODY_DATA_SIZE
        data = fileData[initialIndex:initialIndex + BODY_DATA_SIZE]

        packet = makePacket(sequenceNumber, data)
        packetList.append(packet)
        sequenceNumber += 1

def makePacket(sequenceNumber, data):
    sequenceNumberData = []
    
    for i in range(0, SEQUENCE_NUMBER_SIZE):
        a = (sequenceNumber >> 8 * (SEQUENCE_NUMBER_SIZE - 1 - i)) & 0xFF
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
