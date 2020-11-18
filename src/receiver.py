import sys
import socket
import time

SEQUENCE_NUMBER_SIZE = 4
startTime = time.time()
BUFSIZE = 1024

logFilename = 'receiver_log.txt'

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
def writeEnd(logFile, throughput):
    logFile.write('File transfer is finished.\n')
    logFile.write('Throughput : {:.2f} pkts/sec\n'.format(throughput))


def fileReceiver():
    print('receiver program starts...') 

    #########################
    
    #Write your Code here

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    sock.bind(('', 10080))

    ack = -1

    dstFilename = 'dst.txt'

    logFile = open(logFilename, 'w')
    logFile.write('')
    logFile.close()

    while True:
        packet, address = sock.recvfrom(BUFSIZE)
        sequenceNumber, data = parsePacket(packet)
        # 패킷 받음
        procTime = time.time() - startTime
        writePkt(logFile, procTime, sequenceNumber, 'received')

        isSave = False

        if sequenceNumber == ack + 1:
            ack += 1
            isSave = True
            # 잘 받은 경우

        ackNumberData = []
        for i in range(0, SEQUENCE_NUMBER_SIZE):
            a = (ack >> 8 * (SEQUENCE_NUMBER_SIZE - 1 - i)) & 0xFF
            ackNumberData.append(a)
        ackNumberByteData = bytes(ackNumberData)

        sock.sendto(ackNumberByteData, address)
        procTime = time.time() - startTime
        writeAck(logFile, procTime, ack, 'sent')
        # ACK 보냄

        if isSave:
            # 잘 받은 경우
            if sequenceNumber == 0:
                dstFilename = data
                # 제목인 경우 제목 저장
            else:
                f = open(dstFilename, 'ab')
                f.write(data)
                f.close()
                # 제목 아닌 경우 파일 저장
            isSave = False

    #########################


def parsePacket(packet):
    sequenceNumber = 0
    for i in range(0, SEQUENCE_NUMBER_SIZE):
        sequenceNumber += packet[i] << (SEQUENCE_NUMBER_SIZE - 1 - i) * 8

    data = packet[SEQUENCE_NUMBER_SIZE:]

    return (sequenceNumber, data)


if __name__=='__main__':
    fileReceiver()
