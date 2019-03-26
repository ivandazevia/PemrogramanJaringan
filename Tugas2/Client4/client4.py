import socket
import select

UDP_IP = "127.0.0.4"
IN_PORT = 9000
timeout = 5


sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, IN_PORT))

while True:
    data, addr = sock.recvfrom(1024)
    print("ini adalah "+data)
    if data:
        print "File name:", data
        file_name = data

    f = open(file_name, 'wb')

    while True:
        ready = select.select([sock], [], [], timeout)
        if ready[0]:
            data, addr = sock.recvfrom(10240)
            f.write(data)
        else:
            print "%s Finish!" % file_name
            f.close()
            break