import socket
import os
import time

HOST = '3.131.47.90'
# HOST = 'localhost'
UPLOAD_PORT = 5555
REQUEST_PORT = 5556
SEPERATOR = "<SEPARATOR>"
BUFFER_SIZE = 4096
MESSAGE_SIZE = 1024

def pad_string(text, length=MESSAGE_SIZE, char=' '):
    return text.ljust(length, char)

def initSocket(port):
    s = socket.socket()
    print(f"Connecting to {HOST}:{port}")
    s.connect((HOST, port))
    print(f"Connected")
    return s

def uploadFile(socket, requestFileName):
    fileSize = os.path.getsize(requestFileName)
    message = requestFileName + SEPERATOR + str(fileSize)
    message = pad_string(message)
    socket.send(message.encode())

    with open(requestFileName, "rb") as f:
        while True:
            # read the bytes from the file
            bytes_read = f.read(BUFFER_SIZE)
            if not bytes_read:
                # file transmitting is done
                break
            # we use sendall to assure transimission in busy networks
            socket.sendall(bytes_read)

def requestHeatmap(socket, requestFileName, colorString):
    # Request that the server make a heatmap
    message = requestFileName + SEPERATOR + colorString
    message = pad_string(message)
    socket.send(message.encode())

    # Receive some confirmation back from service that it will generate heat map with these inputs
    return socket.recv(MESSAGE_SIZE).decode()

def receiveFile(socket, newFilename):
    received = socket.recv(MESSAGE_SIZE).decode()
    if received[:2] != '00':
        print(received[3:].strip())
        return

    received = socket.recv(MESSAGE_SIZE).decode()
    filename, filesize = received.split(SEPERATOR)

    with open(newFilename, "wb") as f:
        while True:
            # read 1024 bytes from the socket (receive)
            bytes_read = socket.recv(BUFFER_SIZE)
            if not bytes_read:
                # nothing is received
                # file transmitting is done
                break
            # write to the file the bytes we just received
            f.write(bytes_read)
    return

def getHeatmap(dataFile, imageFileName, colorString = ''):
    uploadSocket = initSocket(UPLOAD_PORT)
    uploadFile(uploadSocket, dataFile)
    uploadSocket.close()

    requestSocket = initSocket(REQUEST_PORT)
    print(requestHeatmap(requestSocket, dataFile, colorString)[3:].strip())
    receiveFile(requestSocket,imageFileName)
    requestSocket.close()

if __name__ == "__main__":
    # getHeatmap("ExampleData03.csv", "ReturnedImage.png", "#00FF00 #FFFF00 #0000FF")
    getHeatmap("ExampleData01.csv", "ReturnedImage.png")