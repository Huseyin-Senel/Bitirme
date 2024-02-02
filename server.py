import socket
import threading
from abc import ABC, abstractmethod


class Server():
    def __init__(self, port=5000):  # host
        # self.host = socket.gethostname()
        # print(socket.gethostbyname(self.host))
        self.__cancellationToken = False
        self.__listenThread = threading.Thread(target=self.__listen_thread)
        self.host = self.__get_ip()
        self.port = port
        self.__server_socket = socket.socket()
        self.__conn = None
        self.address = None
        self.data = None

        self.socketDataTypes = ["%command%", "%data%"]
        self.socketCommands = ["modelLoaded", "ping", "pong", "stop"]

    def start(self):
        """It starts the server and waits to connect on the (default 5000) port.
        """
        self.__server_socket.bind((self.host, self.port))
        self.__server_socket.listen(2)
        print("Server started listening ...")
        self.__conn, self.address = self.__server_socket.accept()
        print("Connected with client on port " + str(self.address) + ":" + str(self.port))
        self.write_data("pong")

        self.__listenThread.start()

    def __listen_thread(self):
        while not self.__cancellationToken:
            self.data = self.__conn.recv(1024).decode()  # receive response
            # if not data:
            #     break
            self.data_read()

    @abstractmethod
    def data_read(self):
        """
        It works when a message is received from the client.
        By **overriding** this method, you can process messages from the client.

        raw data from client: **self.data**

        With the **command = self.decoder(self.data)**

        code, you can receive the command part of the message from the client.
        """
        print("Message received from client: " + str(self.data))

    def write_data(self, message):
        """Sends a message to the client.

        Parameters:
            message (str): Message to be sent to the client.
        """
        self.__conn.send(self.__encoder(message).encode())

    def __close_connection(self):
        if self.__conn is not None:
            self.__conn.close()

    def stop(self):
        """Stop the server.
        """
        self.__cancellationToken = True
        self.__listenThread.join()
        self.__close_connection()
        print("Server stopped and stopped listening ...")

    def __encoder(self, string):
        if string in self.socketCommands:
            return str(self.socketDataTypes[0] + string)
        else:
            return str(self.socketDataTypes[1] + string)

    def decoder(self, raw_message):
        """The given raw data returns only the message part.
        If the socket data type is not found in the raw data, the raw data is returned.

        :param str raw_message:
        :return: message in raw data
        :rtype: str
        """
        for socket_data_type in self.socketDataTypes:
            if socket_data_type in raw_message:
                return raw_message.replace(socket_data_type, "")

        return raw_message

    @staticmethod
    def __get_ip():
        hostname = socket.gethostname()
        ip_address = socket.gethostbyname(hostname)
        return ip_address
