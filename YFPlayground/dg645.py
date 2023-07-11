#!/usr/bin/python
import os
import sys
import time
import socket
import serial
from datetime import datetime
import traceback



# File: 
# Description: DG645.py

# Version History
#  7/11/23 v 1.0 Inception


#
VERBOSE = 2  # set to 0 to be silent, set to 1 to get some debug output, 2 to get more

# Enter a value of 1 for TCP or 2 for Serial Port
CONNECTION_TYPE = 1  

# SET the device IP Address below # Only used if CONNECTION_TYPE == 1
TCP_SOCKET_PORT=5024 ## sheesh. This is what the DG645 uses.

#IP_ADDR="192.168.11.58"
IP_ADDR="192.168.11.225"
#
## or set serial port # Only used if CONNECTION_TYPE == 2
#
PORT="com3"


class comObject:
    """
    Supports either TCP or COM port I/O to xxx
    """

    
    
    # init method or constructor
    def __init__(self, comType, ip_addr, port):
        self.comms = None
        self.comType = comType
        self.ip_addr = ip_addr
        self.port = port
        self.verbose = VERBOSE
        self.interCommandDelay = 0.1

    def open_serial(self):
        """
        port is com port, such as "COM3"
        returns a SerialPort
        """
        ser=serial.Serial()
        ser.port = self.port
        ser.baudrate = 19200
        ser.bytesize = serial.EIGHTBITS
        ser.parity = serial.PARITY_NONE
        ser.stopbits = serial.STOPBITS_ONE
        ser.timeout= 1
        ser.xonxoff = False
        ser.rtscts = False
        ser.dsrdtr = False
        ser.writeTimeout = 1
        return ser


    def open_socket(self):
        """
        port is TCP port such as 23
        returns a socket
        """
        comm_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        comm_socket.connect( (self.ip_addr, self.port))
        comm_socket.settimeout( 1.0 ) # seconds
        return comm_socket

    #
    #
    #
    def tryConnect( self ):    
        """
        type 1 = TCPIP, 2 = COMM Port, else undefined
        Returns socket or serial port if connects OK
        """

        if (self.comType == 1):
            try:
                if self.verbose:
                    print("Opening socket:" + str(self.ip_addr) + ":" + str(self.port) )
                self.comms = self.open_socket() 
                return self.comms
                
            except Exception as e:
                print ('error opening TCP Port')
                
            return None

        if (self.comType == 2):
            try:
                if self.verbose:
                    print("Opening Serial:" + str(self.port) )
                self.comms = self.open_serial() # Initialise the serial port
                self.comms.open()         # open the serial port
                return self.comms
                
            except Exception as e:
                print ('error opening serial port')
                
            return None

        return None


    def sendQuery(self, cmd):
        """
        send a query - return a string response
        """
        recv = None
        if self.comms == None:
            return None     # Error. not open

        if self.verbose:
            print(cmd + " : ", end="")

        if self.comType == 1:   
            self.comms.send( (cmd+'\r\n').encode() ) 
            time.sleep(self.interCommandDelay);
            recv = self.comms.recv(1000).decode()
            time.sleep(self.interCommandDelay);

        if self.comType == 2:
            self.comms.write( (cmd+'\r\n').encode())
            time.sleep(self.interCommandDelay);

            response = self.comms.read_until()
            if len(response) > 0:
                recv = response.decode()

        if self.verbose:
            print(recv)        
        return recv        


    def parse(self, strResponse):
        # T? Returns T?>1.23:OK\r
        p1 = strResponse.split('>')   # T?       1.23:OK\r
        if p1 and len(p1) >= 2:
            p2 = p1[1].split(':')     #  1.23   OK\r
            if p2 and len(p2) ==2 :
                try:
                    v = float( p2[0] ) 
                    return v
                except ValueError: 
                    pass
                    
        return None  

class DG645:
    """
    """
    
    # init method or constructor
    def __init__(self, comObject):
        self.pols = [0,0,0,0]
        self.verbose = VERBOSE
        self.comObject = comObject

    # TODO various commands



#
#
#
def ShowHelp():
   
   print ("Usage:")
   print (sys.argv[0]) # No command line params


    
      
   
#
#
#
def main(argv):
    r = None
    if CONNECTION_TYPE == 1:
        c = comObject( 1, IP_ADDR, TCP_SOCKET_PORT )
        r = c.tryConnect()
   
    if CONNECTION_TYPE == 2:
        c = comObject( 1, None, PORT )
        r = c.tryConnect()

    if (r):
        #now = datetime.now() # current date and time
        #date_time = now.strftime("%m/%d/%Y, %H:%M:%S")
        pass # TODO
    else:
        if c.verbose:
            print("Error, Could not connect")


    if r:
        if c.verbose:
            print("Close connection")
        c.comms.close()


    print("DONE!")


   
  
  


#
#
#
if __name__ == "__main__":
   main(sys.argv[1:])

    


#include "dg645.h"
#include <QThread>



const QString EOL = "\r";
//
// Constructor
//
DG645::DG645( JSNetwork *network )
{
    m_network = network;
}

DG645::~DG645()
{
    // stub
}


int DG645::send( const QString cmd)
{
   return  m_network->send(cmd + EOL);
}

QString DG645::query( const QString cmd)
{   
    return m_network->query(cmd + EOL);
}

//  set delay.
//  Delay SRS manual page 56
//  DLAY 2,0,10e-6<CR> Set channel A delay to equal channel T0 plus 10 µs.



void DG645::setDelay(int nChannel_c, int nChannel_d, float fDelay)
{
   Q_ASSERT( m_network );
   QString qs = QString("DLAY %1,%2,%3").arg(nChannel_c).arg(nChannel_d).arg(fDelay, 3,'g');
   send( qs);
}

void DG645::doTrigger()
{
   QString qs = QString("*TRG");
   send( qs);
}

void DG645::setTriggerSource(int i)
{
   QString qs = QString("TSRC %1").arg(i);
   send( qs);
}


void DG645::setBurstMode(bool bEnable)
{
   QString qs = QString("BURM %1").arg(bEnable? 1:0);
   send( qs);
}

void DG645::setBurstOptions( int nCount, float fTriggerDelay, float fBurstPeriod, bool T0_only)
{
    {QString qs = QString("BURC %1").arg( nCount);
    send( qs); QThread::msleep(100);}

    {QString qs = QString("BURD %1").arg( fTriggerDelay,3,'g');
    send( qs); QThread::msleep(100);}

    {QString qs = QString("BURP %1").arg( fBurstPeriod,3,'g');
    send( qs); QThread::msleep(100);}

    {QString qs = QString("BURT %1").arg( T0_only? 1 : 0 );
    send( qs); QThread::msleep(100);}

}




