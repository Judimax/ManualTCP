from socket import*
import time
serverName = '127.0.0.1'
serverPort = 9999
clientSocket = socket(AF_INET,SOCK_STREAM)
clientSocket.connect((serverName,serverPort))
sentence = raw_input('Please type in a sentence in lowercase')
Sent = time.time()
clientSocket.send(sentence.encode())
modifiedSentence = clientSocket.recv(1024)
Received = time.time()
Elasped = Received-Sent
print('From Server:', modifiedSentence.encode(,Elasped)
clientSocket.close()
