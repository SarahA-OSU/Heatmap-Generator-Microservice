import socket
import os
import time

# HOST = '3.131.47.90'
HOST = 'localhost'
UPLOAD_PORT = 5555
REQUEST_PORT = 5556
SEPERATOR = "<SEPARATOR>"
BUFFER_SIZE = 4096

def initSocket(port):
    s = socket.socket()
    print(f"Connecting to {HOST}:{port}")
    s.connect((HOST, port))
    print(f"Connected")
    return s

def uploadFile(socket, requestFileName):
    fileSize = os.path.getsize(requestFileName)
    socket.send(f"{requestFileName}{SEPERATOR}{fileSize}".encode())
    time.sleep(0.05)

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
    socket.send(f"{requestFileName}{SEPERATOR}{colorString}".encode())

    # Receive some confirmation back from service that it will generate heat map with these inputs
    return socket.recv(1024).decode()

def receiveFile(socket, newFilename):

    received = socket.recv(1024).decode()
    if received[:2] != '00':
        print(received[3:])
        return

    received = socket.recv(BUFFER_SIZE).decode()
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
    print(requestHeatmap(requestSocket, dataFile, colorString)[3:])
    receiveFile(requestSocket,imageFileName)
    requestSocket.close()

if __name__ == "__main__":
    #getHeatmap("ExampleData01.csv", "ReturnedImage.png", "#BB00BB #BB88BB #FFFFFF")
    getHeatmap("ExampleData02.csv", "ReturnedImage.png")