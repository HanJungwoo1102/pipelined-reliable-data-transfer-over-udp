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
def writeEnd(logFile, throughput):
    logFile.write('File transfer is finished.')
    logFile.write('Throughput : {:.2f} pkts/sec'.format(throughput))


def fileReceiver():
    print('receiver program starts...') 

    #########################
    
    #Write your Code here

    BUFSIZE = 1024

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    sock.bind(('', 10080))

    packet, address = sock.recvfrom(BUFSIZE)

    sequenceNumber, data = parsePacket(packet)

    print('sequence number : ', sequenceNumber)
    print('data: ', data)

    packet, address = sock.recvfrom(BUFSIZE)

    sequenceNumber, data = parsePacket(packet)

    print('sequence number : ', sequenceNumber)
    print('data: ', data)

    packet, address = sock.recvfrom(BUFSIZE)

    sequenceNumber, data = parsePacket(packet)

    print('sequence number : ', sequenceNumber)
    print('data: ', data)

    #########################


def parsePacket(packet):
    SEQUENCE_NUMBER_SIZE = 4

    sequenceNumber = 0
    for i in range(0, SEQUENCE_NUMBER_SIZE):
        sequenceNumber += packet[i] << (SEQUENCE_NUMBER_SIZE - 1 - i) * 32

    data = packet[SEQUENCE_NUMBER_SIZE:].decode()

    return (sequenceNumber, data)


if __name__=='__main__':
    fileReceiver()
