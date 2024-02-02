import re
import socket
import subprocess
import threading
import time
class Client():
    def __init__(self,host,port=5000):
        # self.host = socket.gethostname()
        # print(socket.gethostbyname(self.host))
        self.cancelationToken = False
        self.host = host
        self.port = port
        self.client_socket = socket.socket()
        self.data = None

        self.socketDataTypes = ["%command%", "%data%"]
        self.socketCommands = ["modelLoaded", "ping", "pong", "stop"]

        self.client_program()

    def client_program(self):
        self.client_socket.connect((self.host, self.port))  # connect to the server
        self.write_data("ping")
        self.tc = threading.Thread(target=self.listenThread)
        self.tc.start()

    def listenThread(self):
        while not self.cancelationToken:
            self.data = self.client_socket.recv(1024).decode()  # receive response
            self.data_readed()

    def data_readed(self):
        print("Serverden mesaj alındı: " + str(self.data))

    def write_data(self,data):
        self.client_socket.send(self.encoder(data).encode())  # send data to the client

    def closeConnection(self):
        if self.client_socket != None:
            self.client_socket.close()

    def stop(self):
        self.cancelationToken = True
        self.closeConnection()
        print("Client dinlemeyi durdurdu ...")


    def encoder(self,string):
        if string in self.socketCommands:
            return str(self.socketDataTypes[0] + string)
        else:
            return str(self.socketDataTypes[1] + string)

    def decoder(self,string):
        if self.socketDataTypes[0] in string:
            return string.replace(self.socketDataTypes[0], "")
        elif self.socketDataTypes[1] in string:
            return string.replace(self.socketDataTypes[1], "")
