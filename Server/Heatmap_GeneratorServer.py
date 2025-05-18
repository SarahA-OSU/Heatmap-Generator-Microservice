import socket
import os
import Heatmap_Generator
import time

PORT = 5556
SEPERATOR = "<SEPARATOR>"
BUFFER_SIZE = 4096

def send_file(socket, fileToSend):
    fileSize = os.path.getsize(fileToSend)
    socket.send(f"{fileToSend}{SEPERATOR}{fileSize}".encode())
    time.sleep(0.05)

    with open(fileToSend, "rb") as f:
        while True:
            # read the bytes from the file
            bytes_read = f.read(BUFFER_SIZE)
            if not bytes_read:
                # file transmitting is done
                break
            # we use sendall to assure transimission in busy networks
            socket.sendall(bytes_read)

s = socket.socket()
print("I'm the server. Socket created.")

s.bind(('', PORT))
print("Socket bound to %s" %(PORT))

s.listen(5)
print("Socket listening")

while True:
    client_socket, addr = s.accept()
    try:
        received = client_socket.recv(1024).decode()
        requestedInputFilename, requestColorString = received.split(SEPERATOR)

        print(f"Trying to make a heatmap for {requestedInputFilename}")

        if os.path.exists(requestedInputFilename):
            client_socket.send('00 Creating heatmap.'.encode())
            result = Heatmap_Generator.handle_request(requestedInputFilename, "Output.png", requestColorString)
            if result[0]:
                client_socket.send('00 Created heatmap.'.encode())
                send_file(client_socket, "Output.png")
            else:
                reply = '02 Could not create heatmap: Error: ' + result[1]
                client_socket.send(reply.encode())

            # Delete local files
            os.remove(requestedInputFilename)
            os.remove("Output.png")
        else:
            client_socket.send('01 I do not have this file.'.encode())

    finally:
        client_socket.close()

s.close()