import socket
import sys
import os
import time
from threading import Thread
import glob
import json

class _Client(Thread):
	def __init__(self, connect, addr):
		self.connect = connect
		self.addr = addr
		Thread.__init__(self)

	def list(self, req):
		respon = {}
		dir_list = glob.glob(req['dir']+'*')
		respon['dir_list'] = map(
			lambda file_name : {'name':file_name, 'file' : os.path.isfile(req['dir']+file_name)},
			dir_list
		)
		self.connect.sendall(json.dumps(respon))

	def download(self, req):
		fd = open(req['path'], 'rb')
		respon = {}
		respon['size'] = os.path.getsize(req['path'])
		self.connect.sendall(json.dumps(respon))
		for data in fd:
			self.connect.sendall(data)
		fd.close()

	def upload(self, req):
		max_size = req['size']
		recieved = 0
		fd = open(req['path'], 'wb+', 0)
		self.connect.sendall('SIAP')
		while recieved < max_size:
			data = self.connect.recv(1024)
			recieved += len(data)
			fd.write(data)
		fd.close()
		print('Selamat, file berhasil terupload')

	def run(self):
		while True:
			data = self.connect.recv(1024)
			req = json.loads(data)
			print(req)
			menu = req['cmd']

			if menu == 'list':
				self.list(req)
			elif menu == 'download':
				self.download(req)
			elif menu == 'upload':
				self.upload(req)

class Server(Thread):
	def __init__(self):
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sock.bind(('127.0.0.1', 9000))
		print('Server Siap Digunakan')
		Thread.__init__(self)

	def run(self):
		self.sock.listen(1)
		while True:
			conn, addr = self.sock.accept()
			print('Client yang sedang terhubung '+str(addr))
			_Client(conn, addr).start()

if __name__=="__main__":
	Server().start()

