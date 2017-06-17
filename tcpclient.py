import os, sys, time, datetime, socket, select, threading
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

Listen = ('127.0.0.1',8989)
Proxy = ('216.176.190.138',81)
Payload = ('CONNECT [HP] [P0][CL]Host: example.com[CL]X-Online-Host: example.com[CL2]')

def handle_client(client_socket):
    request = client_socket.recv(1024)
    soc = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    try:
        soc.connect(Proxy)
    except socket.error, (value,message):
        print(W + '  ' + C + str(time.strftime('%X %p')) + W + ' => ' + R + str(message) + ' !')
        soc.close()
        client_socket.close()
        return 0
    else:
        netdata = request.split('\n')[0]
        hp = netdata.split(' ')[1]
        req = Payload.replace('[netData]', (str(netdata)))
        req = req.replace('[HP]', (str(hp)))
        req = req.replace('[P0]','HTTP/1.0')
        req = req.replace('[P1]','HTTP/1.1')
        req = req.replace('[C]','\r')
        req = req.replace('[L]','\n')
        req = req.replace('[CL]','\r\n')
        req = req.replace('[CL2]','\r\n\r\n')
        soc.send(req)
        socs = (client_socket,soc)
        count = 0
        while True:
            count += 1
            recv, _, error = select.select(socs, [], socs, 3)
            if error: break
            if recv:
                for bite in recv:
                    try:
                        data = bite.recv(1024)
                        if not data: break
                    except socket.error, (value,message):
                        print(W + '  ' + C + str(time.strftime('%X %p')) + W + ' => ' + B + str(message) + ' !')
                        break
                    if data:
                        if bite is soc:
                            try:
                                client_socket.send(data)
                                count = 0
                            except:
                                break
                        elif bite is client_socket:
                            try:
                                soc.send(data)
                                count = 0
                            except:
                                break
                        else:
                            break
                    if data.startswith('HTTP/'):
                        print(W + '  => ' + C + str(data.split('\n')[0]))
                        os.system('setprop net.dns1 8.8.8.8')
                        os.system('setprop net.dns2 8.8.4.4')
                        os.system('setprop net.rmnet0.dns1 8.8.8.8')
                        os.system('setprop net.rmnet0.dns2 8.8.4.4')
                    if data.find('200 ') != -1:
                        print(W + '  => '+ G +'Connected !')
            if count == 60:
                break
    finally:
        soc.close()
        client_socket.close()
        return 0
    return 1

def tcp_server():
    server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    try:
        server.bind(Listen)
    except socket.error, (value,message):
        slowprint(W + '+ ' + O + str(message) + ' !')
        server.close()
        sys.exit()
    else:
        server.listen(0)
    while True:
        client, addr = server.accept()
        print(W + '+ ' + C + str(time.strftime('%X %p')) + ' ' + G + addr[0] + ':' + str(addr[1]) + W + ' ' + C + str(os.popen('getprop net.rmnet0.gw').read().split('\n')[0]) + ' ' + G + str(os.popen('getprop gsm.network.type').read().split('\n')[0]))
        client_handler = threading.Thread(target=handle_client, args=(client,))
        client_handler.start()

if __name__ == '__main__':
    os.system('clear')
    slowprint(W + '#'*47)
    slowprint(W + '    -== '+G+'Python Injector Internet Free'+W+' ==-')
    slowprint(W + '#'*47)
    slowprint(W + '# ' + str(time.strftime('%a, %d %B %Y')))
    slowprint(W + '# Provider gsm Operator ' + C + str(os.popen('getprop gsm.operator.alpha').read().split('\n')[0]))
    slowprint(W + '# Listened on ' + C + Listen[0] + ':' + str(Listen[1]))
    slowprint(W + '# Use proxy ' + C + Proxy[0] + ':' + str(Proxy[1]))
    slowprint(W + '# Python ' + C + str(pv) + W + ', ' + C + str(os.popen('getprop ro.product.device').read().split('\n')[0]) + ' ' + str(os.popen('getprop ro.build.version.release').read().split('\n')[0]) + ' Build SDK ' + str(os.popen('getprop ro.build.version.sdk').read().split('\n')[0]))
    slowprint(W + '#'*47)
    time.sleep(1)
    tcp_server()
    