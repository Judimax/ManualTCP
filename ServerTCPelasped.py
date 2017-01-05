from socket import*
import time

serverPort = 9999 
serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.bind(('',serverPort))
serverSocket.listen(1)
print('The server is ready to receive')
while True:
    
    connectionSocket,addr= serverSocket.accept()
    output = connectionSocket.recv(1024)
    capitalizedSentence = output.upper()
    time.sleep(10)
    connectionSocket.send(capitalizedSentence.encode())
    connectionSocket.close()
