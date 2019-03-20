
import sys
from threading import Thread
from ftplib import FTP
from datetime import datetime
import socket
import time
import ast


class Client:

    HOST = '10.0.0.138'  # The server's hostname or IP address
    PORT = 9090  # The port used by the server

    def __init__(self):
        super().__init__()
        self.exitFlag = False
        self.command = 'finish'
        self.startFlag = True
        self.start_client_thread()

    def start_client_thread(self):
        self.thread = Thread(target=self.send_get_server)
        self.thread.start()

    def send_get_server(self):
        SERVER_HOST = str(input('Enter server host("local" for localhost) : \n'))
        if SERVER_HOST == 'local':
            SERVER_HOST = 'localhost'
        print('Client started!\nWaiting for "start" command...')
        sock = socket.socket()

        #sock.connect((self.HOST, self.PORT))
        sock.connect((SERVER_HOST, self.PORT))

        ip = sock.getsockname()[0]

        while True:
            try:
                if self.exitFlag:
                    sys.exit(0)

                self.command = ast.literal_eval(sock.recv(1024).decode('utf-8'))

                if self.command[0] == 'start' and self.startFlag:
                    print('Start downloading...')
                    data = [ip]
                    host = self.command[1]
                    filename = self.command[2]
                    data.append(self.connect_ftp(host, filename))
                    print('Download complete! ', data)
                    sock.send(bytes(str(data), 'utf-8'))
                    self.startFlag = False
                    #self.exitFlag = True
                else:
                    sock.send(bytes(str([ip, {}]), 'utf-8'))
                #time.sleep(2)
            except Exception as e:
                print(e)

    def connect_ftp(self, host, filename):
        x = GetFileFromFTP(host, filename).get_data()
        return x


class GetFileFromFTP:

    def __init__(self, host, filename):
        self.host = host
        self.data = []
        self.filename = filename
        self.total_size = 0
        self.run()

    def run(self):
        TIME_START = str(datetime.now().time())
        TIME = self.get_file()[1]
        SPEED = self.get_download_speed(TIME, self.total_size)
        SIZE = round(self.total_size / 1024)
        #print(f'timestart: {TIME_START}\nspeed: {SPEED} KiB/s\ndownload duration: {TIME:2.2f} s')

        self.data = {
                                    'timestart': TIME_START,
                                    'size': SIZE,
                                    'speed': SPEED,
                                    'duration': TIME,
        }

    def get_data(self):
        return self.data

    def connect_to_ftp(self):
        try:
            self.ftp = FTP(self.host)
            self.ftp.login('root1', 'Qwerty!23')
            self.ftp.cwd('/home/root1')
            #self.ftp.login('root', 'Qwerty!23')
            #self.ftp.cwd('/test')
            self.total_size = round(self.ftp.size(self.filename))
        except Exception as e:
            print('Error with connect to FTP:', e)

    def timeit(method):
        def timed(self, *args, **kw):
            ts = time.time()
            result = method(self, *args, **kw)
            te = time.time()
            TIME = te - ts
            return result, TIME
        return timed

    @timeit
    def get_file(self):
        self.connect_to_ftp()
        with open(self.filename, 'wb') as file:
            self.ftp.retrbinary('RETR %s' % self.filename, file.write)
            file.close()

    def get_download_speed(self, time, size):
        return round((size / time) / 1024)

if __name__ == '__main__':
    Client()
