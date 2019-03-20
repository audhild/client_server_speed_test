
from threading import Thread
import socket
import sys
import os
import ast
from datetime import datetime


if not os.path.exists('DATA'):
    os.mkdir('DATA')


class Server:

    def __init__(self):
        self.data = {}
        self.command = ['finish', '', '']
        self.connections_status = {}
        self.connected_clients = []
        self.count = 0
        self.connections_number = 0
        self.num = 0
        self.exitFlag = False
        self.write_flag = True
        self.start_time = object
        self.start_server_thread()

    def start_server_thread(self):
        """start thread for local server"""
        self.thread = Thread(target=self.start_server)
        self.thread.start()

    def new_client_thread(self):
        self.start_get_command_thread()
        c = self.client_c_addr[self.num][0]
        self.num += 1
        client = ''
        while True:
            try:
                if self.exitFlag:
                    sys.exit(0)

                c.send(bytes(str(self.command), 'utf-8'))

                data = ast.literal_eval(c.recv(1024).decode('utf-8'))

                client = data[0]
                if client not in self.connected_clients:
                    self.connected_clients.append(client)
                    print('Connected clients:', self.connected_clients)

                if not data[1]:
                    continue

                self.data.setdefault(client, {})
                self.data[client] = data[1]

                if len(self.data.keys()) == self.num and self.write_flag:
                    self.write_data(self.data)
                    self.write_flag = False

            except Exception as e:
                print('Error', e)
                print(f'\nClient: {client} disconnected!')
                self.connections_number -= 1
                self.connected_clients.remove(client)
                print('Connected clients:', self.connected_clients, '\n')
                if self.connections_number == 0:
                    #print('Stop running server..')
                    self.exitFlag = True
                    #self.sock.close()
                sys.exit()

    #iVMS-4200(v2.7.0.10).rar

    def start_server(self):
        """create server"""
        try:
            print('Start server...\n')
            SERVER_HOST = str(input('Enter host for server("local" for localhost) : \n'))
            FTP_HOST = str(input('Enter host for FTP server: \n'))
            FILENAME = str(input('Enter filename to download: \n'))
            if SERVER_HOST == 'local':
                SERVER_HOST = ''
            self.command[2] = FILENAME
            self.command[1] = FTP_HOST
            print('Your server host: ', SERVER_HOST)
            print('Your FTP server host: ', FTP_HOST)
            print('File to download: ', FILENAME)
            print('Waiting for connections...\n')
            self.num = 0
            self.client_c_addr = []
            self.sock = socket.socket()
            self.sock.bind((SERVER_HOST, 9090))
            self.sock.listen(15)

            while True:
                if self.exitFlag:
                    sys.exit(0)
                c, addr = self.sock.accept()
                print('New connection:', addr, '\n')
                self.client_c_addr.append((c, addr))
                exec('self.thread_{} = Thread(target=self.new_client_thread)'.
                     format(self.num))
                exec('self.thread_{}.start()'.format(self.num))
                self.connections_number += 1
        except Exception as e:
            print('Wrong host!')
            self.start_server_thread()

    def start_get_command_thread(self):
        """start thread for each exchange"""
        try:
            self.thread_start_clients = Thread(target=self.get_command)
            self.thread_start_clients.start()
        except Exception as e:
            print(e)

    def get_command(self):
        try:
            command = str(input('Enter command "start" for starting all clients: \n'))
            if command == 'start':
                print(f'Starting all clients...\nWaiting until all downloads will be finished...\n')
                self.command[0] = command
                self.start_time = datetime.now().time()
                #self.get_command()
            else:
                print('Wrong command, try again!')
                self.get_command()
        except Exception as e:
            print(e)

    def write_data(self, data):
        print('DATA TO WRITE:\nServer started all clients at:', str(self.start_time), '\n')
        for i,j in data.items():
            print(i, j, '\n')

        date = str(datetime.now())[:-10].replace(':', '_')
        line_num = 1

        with open('DATA\\{}.txt'.format(date), 'w') as f:
            template_h = "{0:25}{1:20}{2:15}{3:20}{4:25}{5:20}"
            template_l = "{0:3}{1:22}{2:20}{3:15}{4:20}{5:25}{6:20}"
            headers = ['   START_ON_SERVER', 'START_ON_CLIENT', 'FILE_SIZE', 'DOWNLOAD_SPEED', 'DURATION', 'IP']
            f.write(template_h.format(*headers) + '\n')
            f.write('_' * 115 + '\n')
            for i,j in data.items():
                line = [f'{line_num}.']
                line_num += 1
                line.append(str(self.start_time))
                for m, n in j.items():
                    n = str(n)
                    if m == 'size':
                        n += ' Kbyte'
                    elif m == 'speed':
                        n += ' Kbyte/s'
                    elif m == 'duration':
                        n += ' s'
                    line.append(n)
                line.append(i)
                f.write(str(template_l.format(*line)) + '\n')



if __name__ == '__main__':
    Server()
