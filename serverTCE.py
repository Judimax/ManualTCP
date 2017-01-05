from socket import * #importing the socket module
from struct import * #importing the struct module
from fallback import *  #importing clientTCP to make use of the packet object
import time
global debug
debug = True
cong_wdw = 1 #how many packets, slow start to 32
exp = 0 #counter for slow start function
ss_thresh =64 #cong_wdw must get to 63
total_packets_sent = 0 
packets_sent = 0
seq_num = 0
def slow_start(num,exp): #function for congestion
	if num < 32:
		value = (2^(exp))*num
	else:
		value = num + 1
	exp +=1
	return value

try:
    source_port_num = 9998 #port number router will be receiving from
    serverSocket = socket(AF_INET, SOCK_DGRAM) #handshake and connection type
    serverSocket.bind(('',source_port_num))
    print("The server is ready to receive")
except:
    print("didn't set up UDP")

Router = TCP_Client_Header() #to take care of setup and close commands
Server = TCP_Client_Header() 
shut_down = 0
speed_up = True
got_fst = True

while True:
    if got_fst:
	output,clientaddr = serverSocket.recvfrom(2048)# should receive a string of the datagram
	Router.headptr = None #so it can make way for new data that is coming in
	output = str(output)# so string can be inserted uniforminly with insert method
	Router.insert(output)
	print(str(Router))
	got_fst = False
	
    else:

   	if speed_up:
		output,clientaddr = serverSocket.recvfrom(2048)
		Router.headptr= None
		output = str(output)
		Router.insert(output)
    	else:	
		output,clientaddr = serverSocket.recvfrom(2048)
		Server.headptr = None
		output = str(output)
		Server.insert(output)
    
    if Router.check("ACKbit","2") & Router.check("ack_num","33"):
	serverSocket.close()
	if debug:
		print("The server has closed its socket")
	break
    elif Router.check("FINbit","1") & Router.check("seq_num","203"):
	if shut_down == 1:
		Router.replace("ACKbit",2)
		Router.replace("ack_num",32)
		serverSocket.sendto(str(Router).encode(),clientaddr)
		print("The client is starting to close its socket")
		print("The client can no longer send but receive data")
		speed_up = True
		shut_down += 1
		pass
	else:
		Router.replace("FINbit",1)
		Router.replace("seq_num",204)
		serverSocket.sendto(str(Router).encode(),clientaddr)
		print("Informing the client that the server will start to close its socket")

    elif Router.check("ACKbit","1") & Router.check("ack_num","202") & speed_up:
	if shut_down == 0:
		print("The client has established a connection with the server")
		shut_down +=1
		Server = Router
		Server.insert_packet("app_data","I am the server")
		speed_up = False

    elif Router.check("SYNbit","1") & Router.check("seq_num","200"):
	Router.replace("seq_num",201)
	Router.replace("ACKbit",1)
	Router.replace("ack_num",201)
	print("The server has received the initiation message from the client")
    	serverSocket.sendto(str(Router).encode(),clientaddr)
   
    elif speed_up == False:
	print("here")
	while total_packets_sent != 31:
		if debug:
			pass
			print(total_packets_sent)
		cong_wdw = slow_start(cong_wdw,exp)
		gets = []
		while packets_sent != cong_wdw:
			output,clientaddr = serverSocket.recvfrom(2048)
			if debug:
				#print(type(output))
				pass
			Server.headptr = None
			Server.insert(output)
			if debug:
				print(Server.steal_a_part("ack_num",True))
			Server.replace('seq_num',seq_num)
			serverSocket.sendto(str(Server).encode(),clientaddr)
			
			if total_packets_sent == 30:
				total_packets_sent +=1
				if debug:
					print(total_packets_sent)
				if total_packets_sent == 31:
					if debug:
						print(total_packets_sent)	
					break
			else:
	   	        	packets_sent += 1		
				seq_num += 1
			if packets_sent == cong_wdw:
				
				total_packets_sent += packets_sent
				packets_sent = 0
				print(total_packets_sent)
				if debug:
					print("Sent it")
				break
			
			
	if debug:
		print("Got out I should be getting something  right?")
	speed_up = True