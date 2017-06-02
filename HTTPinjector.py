import os, sys, time, socket, thread, string, select
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

def slowprint(s):
    for c in s + '\n':
        sys.stdout.write(c)
        sys.stdout.flush()
        time.sleep(3.0 / 90)

LISTEN = '127.0.0.1:8989'
PROXY = 'host:port'
PAYLOAD = 'CONNECT [HP] [P0][CL]Host: example.com[CL]X-Online-Host: example.com[CL]Ping-Server: www.google.com[CL]Connection: keep-alive[CL2]'
TAM_BUFFER = 65535
MAX_CLIENT_REQUEST_LENGTH = 8192 * 8

def getReplacedPayload(payload, netData, hostPort, protocol):
    str = payload.replace('[netData]', netData)
    str = str.replace('[HP]', (hostPort[0] + ':' + hostPort[1]))
    str = str.replace('[H]', hostPort[0])
    str = str.replace('[P]', hostPort[1])
    str = str.replace('[PC]', protocol)
    str = str.replace('[P0]','HTTP/1.0')
    str = str.replace('[P1]','HTTP/1.1')
    str = str.replace('[C]','\r')
    str = str.replace('[L]','\n')
    str = str.replace('[CL]','\r\n')
    str = str.replace('[LC]','\n\r')
    str = str.replace('[CL2]','\r\n\r\n')
    return str
    
def getRequestProtocol(request):
    inicio = request.find(' ', request.find(':')) + 1
    str = request[inicio:]
    fim = str.find('\r\n')
    
    return str[:fim]
    
def getRequestHostPort(request):
    inicio = request.find(' ') + 1
    str = request[inicio:]
    fim = str.find(' ')
    
    hostPort = str[:fim]
    
    return hostPort.split(':')
    
def getRequestNetData(request):
    return request[:request.find('\r\n')]
    
def receiveHttpMsg(socket):
    len = 1
    
    data = socket.recv(1)
    while data.find('\r\n\r\n'.encode()) == -1:
        if not data:
            print(W + '  => ' + O + 'Socket close !')
            break
        data = data + socket.recv(1)
        len += 1
        if len > MAX_CLIENT_REQUEST_LENGTH: break
        
    return data
    
def doConnect(clientSocket, serverSocket, tamBuffer):
    sockets = [clientSocket, serverSocket]
    timeout = 0
    print(W +'  => ' + G + 'Connected !')
    while 1:
        timeout += 1
        ins, _, exs = select.select(sockets, [], sockets, 3)
        if exs: break
        if ins:
            for socket in ins:
                try:
                    data = socket.recv(tamBuffer)
                    if not data: break
                    if socket is serverSocket:
                        clientSocket.sendall(data)
                    else:
                        serverSocket.sendall(data)
                        timeout = 0
                except:
                    break
                    
        if timeout == 60:
            break
	
def acceptThread(clientSocket, clientAddr):
    print(W +'+ Client connected : ' + G + clientAddr[0] + ':' + str(clientAddr[1]))
    request = receiveHttpMsg(clientSocket)
    if not request.startswith('CONNECT'):
        print(W + '  => ' + O + 'The payload is incorrect !')
        clientSocket.sendall('HTTP/1.1 405 Only_CONNECT_Method!\r\n\r\n')
        clientSocket.close()
        thread.exit()

    netData = getRequestNetData(request)
    protocol = getRequestProtocol(request)
    hostPort = getRequestHostPort(netData)
    
    finalRequest = getReplacedPayload(PAYLOAD, netData, hostPort, protocol)
    proxySocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    RMT = PROXY.find(':')
    if RMT >= 0:
        PX = (PROXY[:RMT], int(PROXY[RMT + 1:]))
    else:
        PX = (PROXY, 80)
    try:
        proxySocket.connect((PX))
        #proxySocket.sendall(finalRequest)
    except socket.error, (value,message):
        print(W +'  => Client closed' + W + ' : ' + R + clientAddr[0] + ':' + str(clientAddr[1]))
        print(W +'  => ' + R + str(message) + ' !')
        proxySocket.close()
        clientSocket.close()
        thread.exit()
    #else:
    if finalRequest:
        proxySocket.sendall(finalRequest)
    while 1:
            try:
                proxyResponse = receiveHttpMsg(proxySocket)
                clientSocket.sendall(proxyResponse)
                timeout = 0
                if not proxyResponse:
                    print(W + '  => ' + B + 'Disconnected !')
                    break
                if proxyResponse.startswith('HTTP/'):
                    print(W +'  => ' + C + str(getRequestNetData(proxyResponse.split('\n')[0])))
                    os.system('setprop net.dns1 8.8.8.8')
                    os.system('setprop net.dns2 8.8.4.4')
                    os.system('setprop net.rmnet0.dns1 8.8.8.8')
                    os.system('setprop net.rmnet0.dns2 8.8.4.4')
            except socket.error, (value,message):
                print(W + '  => ' + B + str(message) + ' !')
                break
            if proxyResponse.find('200') != -1:
                doConnect(clientSocket, proxySocket, TAM_BUFFER)
    #print(W +'  => ' + O + 'Socket close !')
    proxySocket.close()
    clientSocket.close()
    thread.exit()
    
def start():
    soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    LS = LISTEN.find(':')
    if LS >= 0:
        LST = (LISTEN[:LS], int(LISTEN[LS + 1:]))
    else:
        LST = (LISTEN, 8989)
    try:
        soc.bind((LST))
    except socket.error, (value,message):
        print(W +'+ ' + O + str(message) + ' !')
        soc.close()
    else:
        slowprint(W +'+ Server listening on...')
        soc.listen(0)
        while 1:
            try:
                clientSocket, clientAddr = soc.accept()
                thread.start_new_thread(acceptThread, tuple([clientSocket,clientAddr]))
            except KeyboardInterrupt:
                soc.close()
                os.abort()
                
if __name__ == '__main__':
    os.system('clear')
    slowprint(W +'#'*46)
    slowprint(W +'     -== ' + G + 'Python Injector Internet Free' + W + ' ==-')
    slowprint(W +'#'*46)
    slowprint(W +'+ Listen : ' + LISTEN)
    slowprint(W +'+ Remote : ' + PROXY)
    slowprint(W +'+ Python : ' + pv + ' linux')
    slowprint(W +'#'*46)
    slowprint(W +'#'*46)
    time.sleep(1)
    start()
    