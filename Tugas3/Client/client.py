import socket
import json
import os
from threading import Thread


class RelativePath:
    def __init__(self):
        self.current_dir = ''

    def get_dir(self):
        return self.current_dir

    def _get_array_dir(self):
        return self.current_dir.split('/')

    def cd(self, dir):
        if dir == '..':
            array_dir = self._get_array_dir()
            self.current_dir = ''

            a_len = len(array_dir)

            for i in range(0, a_len-2):
                print('concat : '+array_dir[i])
                self.current_dir += array_dir[i]
                self.current_dir += '/'

        elif self.current_dir == '':
            self.current_dir = dir + '/'
        else:
            self.current_dir += dir + '/'


class Client(Thread):
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_addr = ('127.0.0.1', 9000)
        self.sock.connect(server_addr)
        print('Sedang terhubung dengan server '+str(server_addr))
        self.r_path = RelativePath()
        Thread.__init__(self)

    def list(self):
        req = {}
        req['cmd'] = 'list'
        req['dir'] = self.r_path.get_dir()

        self.sock.sendall(json.dumps(req))
        respon = self.sock.recv(1024)
        data = json.loads(respon)

        dir_list = data['dir_list']
        print(self.r_path.get_dir()+' > ')
        for dir in dir_list:
            dir_type = ''
            if dir['file']:
                dir_type = 'file'
            else :
                dir_type = 'folder'

            print(dir['name'] + '     [{}]'.format(dir_type))

    def download(self, file_name):
        req = {}
        req['cmd'] = 'download'
        req['path'] = self.r_path.get_dir() + file_name
        self.sock.sendall(json.dumps(req))
        fd = open(file_name, 'wb+', 0)
        respon = self.sock.recv(1024)
        data = json.loads(respon)
        if data['size'] is not None:
            max_size = data['size']
            received = 0
            while received < max_size:
                data = self.sock.recv(1024)
                received += len(data)
                fd.write(data)
        fd.close()
        print('Selamat, file berhasil terdownload')

    def upload(self, file_name):
        path = self.r_path.get_dir()+file_name
        fd = open(file_name, 'rb')
        req = {}
        req['cmd'] = 'upload'
        req['path'] = path
        req['size'] = os.path.getsize(file_name)
        self.sock.sendall(json.dumps(req))
        respon = self.sock.recv(1024)
        if respon == 'SIAP':
            for data in fd:
                self.sock.sendall(data)

        self.sock.send(bytes('SELESAI'))
        print('Selamat, file berhasil terupload')


    def run(self):
        print('----MENU----')
        print('1. List (Ketikkan "list" untuk mengetahui file yang ada)')
        print('2. Move Directory (Ketikkan move ... untuk pindah direktori)')
        print('3. Download (Ketikkan download ... untuk mengunduh file)')
        print('4. Upload (Ketikkan upload ... untuk mengupload file)')
        while True:
            commands = raw_input().split(' ')
            cmd = commands[0]
            if cmd == 'list':
                self.list()
            elif cmd == 'move':
                cd_path = commands[1]
                self.r_path.cd(cd_path)
                print(self.r_path.get_dir())
            elif cmd == 'download':
                self.download(commands[1])
            elif cmd == 'upload':
                self.upload(commands[1])


if __name__=="__main__":
    Client().start()

