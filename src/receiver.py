import sys
import socket

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

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    sock.bind(('', 10080))

    data, addr = sock.recvfrom(1024)

    print('Server receive the data : ', data.decode())
    print('Client Address', addr)

    sock.close()

    #########################



if __name__=='__main__':
    fileReceiver()
