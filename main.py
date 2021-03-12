import socket
import threading
import os
from dotenv import load_dotenv

load_dotenv(verbose=True)

HOST = os.getenv("HOST")
PORT = int(os.getenv("PORT"))


class ClientThread(threading.Thread):
    def __init__(self, clientAddress, clientsocket):
        threading.Thread.__init__(self)
        self.csocket = clientsocket
        print("New connection added: ", clientAddress)
        print("Connection from : ", clientAddress)

    def run(self):
        # self.csocket.send(bytes("Hi, This is from Server..",'utf-8'))
        msg = ''
        while True:
            data = self.csocket.recv(2048)
            if data:
                msg = data.decode()
                if msg == 'bye':
                    break
                print("from client", msg)
                self.csocket.send(bytes(msg, 'UTF-8'))
        #print("Client at ", clientAddress, " disconnected...")


def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    print("Server started")
    print("Waiting for client request..")
    while True:
        server.listen(1)
        clientsock, clientAddress = server.accept()
        newthread = ClientThread(clientAddress, clientsock)
        newthread.start()


if __name__ == '__main__':
    main()