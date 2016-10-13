import os, sys, time
from socket import *
from threading import Thread
from platform import python_version
sion = python_version()

W = '\x1b[0m'
R = '\x1b[31m'
G = '\x1b[1;32m'
O = '\x1b[33m'
B = '\x1b[34m'
P = '\x1b[35m'
C = '\x1b[36m'
GR = '\x1b[37m'

LHOST = '127.0.0.1'
PHOST = '10.8.3.8'
PPORT = 80
pay1 = '[NET][CLC][CL]GET / [P1] 200 OK[CL]Host: [CL]X-Online-Host: download.cdn.oly-eu.blackberry.com[CL2]'
pay2 = ''

def slowprint(s):
    for c in s + '\n':
        sys.stdout.write(c)
        sys.stdout.flush()
        time.sleep(3.0 / 90)
        
class PipeThread(Thread):
    pipes = []
    def __init__(self,source,sink):
        Thread.__init__(self)
        self.source = source
        self.sink = sink
        PipeThread.pipes.append(self)

    def run(self):
        while 1:
            try:
                rawdata = self.source.recv(1024)
                if not rawdata: break
                netdata = (rawdata).strip()
                if netdata.startswith('CONNECT'):
                    req = '%s%s' % (pay1,pay2)
                    req = req.replace('[NET]','%s' % netdata)
                    req = req.replace('[C]','\r')
                    req = req.replace('[L]','\n')
                    req = req.replace('[CL]','\r\n')
                    req = req.replace('[LC]','\n\r')
                    req = req.replace('[CLC]','\r\n\r')
                    req = req.replace('[LCL]','\n\r\n')
                    req = req.replace('[CL2]','\r\n\r\n')
                    req = req.replace('[CL3]','\r\n\r\n\r\n')
                    req = req.replace('[P0]','HTTP/1.0')
                    req = req.replace('[P1]','HTTP/1.1')
                    req = req.replace('[SP]','%s' % pay2)
                    slowprint(G +'+ %s' % netdata)
                    self.sink.send(req)
                else:
                    self.sink.send(rawdata)
                    dres = rawdata.split('\n')[0]
                    if dres.startswith('HTTP'):
                        slowprint(C +'+ %s' % dres)
            except:
                slowprint(B +'+ Disconnected !')
                break
        PipeThread.pipes.remove(self)
		
class TCPTunel(Thread):
    if (len(sys.argv)<2):
        os.system('clear')
        slowprint(G +'+ Usage: python pin.py <listenport>')
        time.sleep(2)
        os.system('clear')
        slowprint(C +'+ Example: python sdcard/pin.py 8989')
        time.sleep(2)
        os.system('clear')
        exit()

    LHOST = '127.0.0.1'
    LPORT = int(sys.argv[1])
    def __init__( self, LHOST, LPORT, PHOST, PPORT):
        Thread.__init__(self)
        self.sock = socket( AF_INET, SOCK_STREAM )
        try:
            self.sock.bind((LHOST,LPORT))
            self.sock.listen(0)
        except:
            self.sock.close()
            slowprint(R +'+ Listen port address already in use !')

    def run(self):
        while 1:
            newsock, address = self.sock.accept()
            fwd = socket( AF_INET, SOCK_STREAM )
            try:
                fwd.connect((PHOST, PPORT))
                slowprint(G +'+ Connect to %s:%s' % (PHOST,PPORT))
            except:
                fwd.close()
                slowprint(O +'+ Socket close !')
            PipeThread(newsock,fwd).start()
            PipeThread(fwd,newsock).start()

if __name__ == '__main__':
    LPORT = int(sys.argv[1])
    os.system('clear')
    slowprint(W +'#'*46)
    slowprint(G +'    --= Python Injector Internet Free =--')
    slowprint(W +'#'*46)
    slowprint(W +'+ Author : NetHandlers\n+ Remote : %s:%s\n+ Listen : %s:%s\n+ Python : %s Linux' % (PHOST, PPORT, LHOST, LPORT, sion))
    slowprint(W +'#'*46)
    TCPTunel(LHOST,LPORT,PHOST,PPORT).start()
