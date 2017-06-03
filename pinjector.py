import os, sys, time, socket, select, thread
from platform import python_version
pv = python_version()

W = '\x1b[0m'
R = '\x1b[31m'
G = '\x1b[1;32m'
O = '\x1b[33m'
B = '\x1b[34m'
P = '\x1b[35m'
C = '\x1b[36m'
GR = '\x1b[37m'

# Pinjector Configuration
Listen = '127.0.0.1:8989' # local host and port
Proxy = 'host:port' # remote http proxy host and port default or squid proxy ssh or vpn
Payload = 'CONNECT [HP] [P0][CL]Host: example.com[CL]X-Online-Host: example.com[CL]Ping-Server: www.google.com[CL]Connection: keep-alive[CL2]'

def slowprint(s):
    for c in s + '\n':
        sys.stdout.write(c)
        sys.stdout.flush()
        time.sleep(3.0 / 90)

class Pinjector:
    def __init__(self, request, address):
        soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client = request
        self.Addr = address
        self.NetData = self.client.recv(int(1024))
        chp = self.NetData.split(' ')[1].find(':')
        if chp >= 0:
            hp = (self.NetData.split(' ')[1][:chp], int(self.NetData.split(' ')[1][chp + 1:]))
        print(W +'+ Client connected : ' + G + self.Addr[0] + ':' + str(self.Addr[1]))
        RMT = Proxy.find(':')
        if RMT >= 0:
            PXY = (Proxy[:RMT], int(Proxy[RMT + 1:]))
        else:
            PXY = (Proxy, 80)
        try:
            soc.connect((PXY))
            req = Payload.replace('[NetData]', self.NetData.split('\n')[0])
            req = req.replace('[HP]', self.NetData.split(' ')[1])
            req = req.replace('[H_P]', (hp[0] + ':' + str(hp[1])))
            req = req.replace('[H]', hp[0])
            req = req.replace('[P]', (str(hp[1])))
            req = req.replace('[P0]','HTTP/1.0')
            req = req.replace('[P1]','HTTP/1.1')
            req = req.replace('[C]','\r')
            req = req.replace('[L]','\n')
            req = req.replace('[CL]','\r\n')
            req = req.replace('[LC]','\n\r')
            req = req.replace('[CL2]','\r\n\r\n')
        except socket.error, (value,message):
            print(W +'  => Client closed' + W + ' : ' + R + self.Addr[0] + ':' + str(self.Addr[1]))
            print(W +'  => ' + O + str(message) + ' !')
            soc.close()
            self.client.close()
            thread.exit()
            
        else:
            soc.send(req)
            count = 0
        socs = [self.client,soc]
        while 1:
            count += 1
            recv, _, error = select.select(socs, [], socs, 3)
            if error:
                break
                
            if recv:
                for bite in recv:
                    try:
                        data = bite.recv(int(1024))
                        if not data: break
                    except socket.error, (value,message):
                        print(W +'  => ' + B + str(message) + ' !')
                        break
                    if data:
                        if bite is soc:
                            self.client.send(data)
                        else:
                            soc.send(data)
                            count = 0
                    if data.startswith('HTTP/'):
                        print(W + '  => ' + C + str(data.split('\n')[0]))
                        os.system('setprop net.dns1 8.8.8.8')
                        os.system('setprop net.dns2 8.8.4.4')
                    if data.find('200') != -1:
                        print(W + '  => ' + G + 'Pinjector Connected !')
                        
            if count == 60:
                break
                
        #print(W +'  => ' + O + 'Socket close !')
        soc.close()
        self.client.close()
        thread.exit()
            
def start():
    soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    LS = Listen.find(':')
    if LS >= 0:
        LST = (Listen[:LS], int(Listen[LS + 1:]))
    else:
        LST = (Listen, 8989)
    try:
        soc.bind((LST))
    except socket.error, (value,message):
        print(W +'+ ' + O + str(message) + ' !')
        soc.close()
    else:
        slowprint(W + '+ Server listening on...')
        soc.listen(0)
        while 1:
            try:
                request,address = soc.accept()
                thread.start_new_thread(Pinjector, tuple([request,address]))
            except KeyboardInterrupt:
                soc.close()
                os.abort()

if __name__ == '__main__':
    os.system('clear')
    slowprint(W +'#'*47)
    slowprint(W +'     -== ' + G + 'Python Injector Internet Free' + W + ' ==-')
    slowprint(W +'#'*47)
    slowprint(W +'+ Listen : ' + O + Listen)
    slowprint(W +'+ Remote : ' + O + Proxy)
    slowprint(W +'+ Python : ' + O + pv + ' linux')
    slowprint(W +'#'*47)
    time.sleep(1)
    start()