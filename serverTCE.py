from socket import * #importing the socket module
from struct import * #importing the struct module
from fallback import *  #importing clientTCP to make use of the packet object
import time
global debug
debug = False
cong_wdw = 1 #how many packets, slow start to 32
exp = 0 #counter for slow start function
ss_thresh =64 #cong_wdw must get to 63
total_packets_sent = 0 
packets_sent = 0
seq_num = 0
timer = 1 #the timer for server to resend if client did not send acks in time
UPS = [] # to send packets according to cong wdw
def slow_start(num,exp): #function for congestion
	if num < 32:
		value = (2^(exp))*num
	else:
		value = num + 1
	exp +=1
	return value

def checkequal(lst):
	return lst[1:] == lst[:-1]

def try_list(*args):
	for i in range(len(args)):
		try:
			args[i][-2]
			try:
				args[i][-2][0]
				return args[i][-1]
			except:
				return args[i]
		except:
			pass
try:

    source_port_num = 8997 #port number router will be receiving from
    serverSocket = socket(AF_INET, SOCK_DGRAM) #handshake and connection type
    serverSocket.bind(('',source_port_num))
    print("The server is ready to receive")
except:
    print("didn't set up UDP")

Router = TCP_Client_Header() #to take care of setup and close commands
Server = TCP_Client_Header() 
gtep = TCP_Client_Header() #to find when server has sent enough packets
shut_down = 0
speed_up = True
got_fst = True

while True:
    if got_fst:
	output,clientaddr = serverSocket.recvfrom(2048)# should receive a string of the datagram
	Router.headptr = None #so it can make way for new data that is coming in
	output = str(output)# so string can be inserted uniforminly with insert method
	Router.insert(output)
	got_fst = False
	
    else:

   	if speed_up:
		output,clientaddr = serverSocket.recvfrom(2048)
		Router.headptr= None
		output = str(output)
		try:
			Router.insert(output)
		except:
			pass
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
		Router.replace("ack_num",39)
		serverSocket.sendto(str(Router).encode(),clientaddr)
		print("The client is starting to close its socket")
		print("The client can no longer send but receive data")
		speed_up = True
		shut_down += 1
		pass
	else:
		if debug:
			#print("this is the val of shut_down")
			#print(shut_down)
			pass
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
	Sent = 0
	Received =0
	t_times = [0]
	resend = False
	bill = [946]
	all_pkgs = []
	missing_note = False
	Server.replace("ack_num",0)
	if debug:
		print(here)#
	while cong_wdw != 33:	
		print("\n")
		print("all_pkgs ...receiving")
		print(all_pkgs)
		if debug:
			pass
		#print("This is the bill, acks we got from the client")
		#print(bill)
		print(resend)
		print(Server.steal_a_part("ack_num",True,True))
		
		if len(bill)> 1 and checkequal(all_pkgs[-1]) or resend:
			resend = False
			print("The sequennce did not get to the client in time")
			print(all_pkgs)
			print(bill)
			re_ack = Server
			for i in try_list(all_pkgs,[1,2]):
				print(i)
				re_ack.headtr = None
				re_ack.replace("seq_num",i)
				serverSocket.sendto(str(re_ack).encode(),clientaddr)
			serverSocket.sendto(str(None).encode(),clientaddr)
			print("shld get # and shld break out of loop")
			missing_note = True
			bill = []
			"""while True:
				print("they should be sending different acks")
				output, clientaddr = serverSocket.recvfrom(2048)
				if output == "None":
					break
				Server.headptr = None
				Server.insert(output)
				msing_ack = Server.steal_a_part("ack_num",True,True)
				bill.append(msing_ack)
				print(Server.steal_a_part("ack_num",True))
			all_pkgs.append(bill)"""

		else:
			if not missing_note:
				print("sending as normal")	
				resend= False
				bill = []
			
			
				UPS = []
				cong_wdw = slow_start(cong_wdw,exp)
				print("This is cong_wdw")
				print(cong_wdw)
				while packets_sent != cong_wdw:	
					seq_num += 1
					Server.replace('seq_num',seq_num)
					if seq_num <= 32:
						UPS.append(str(Server))
   	        				packets_sent += 1
					else:
						break
				print("amnt of packets sent")
				print(packets_sent)	
			
			else: 
				pass
	
			if packets_sent == cong_wdw or total_packets_sent >=31 or resend or len(UPS) != 0:
				resend = False
				total_packets_sent += packets_sent
				packets_sent = 0
				
				for i in UPS:
					if total_packets_sent == 2:
						time.sleep(3.1) 			      
					Sent = time.time()
					serverSocket.sendto(str(i).encode(),clientaddr)
				serverSocket.sendto(str(None).encode(),clientaddr)
			
				t_times = []

				while True:
					output,clientaddr =serverSocket.recvfrom(2048)
					Received = time.time()
					Elasped = Received - Sent
					if output == "None":
						break
					t_times.append(Elasped)
					Server.headptr =None
					Server.insert(output)
					current_data = Server.steal_a_part('ack_num',True,True)
					bill.append(current_data)
					print(Elasped)
					print(Server.steal_a_part('ack_num',True))
				print("This is what im checking against")
				print(t_times)
				for i in t_times:
					if i > 1:
						print("Client didn't get it")
						resend = True
						break
				print("I hope I didn't break yet")
				print('\n')
				print("This is the acks we got  from the client")
				print(bill)			
				all_pkgs.append(bill)
				missing_note = False
				#print("did it go in the right box?")
				#print(all_pkgs)			
	if debug:
		print("Got out I should be getting something  right?")
		#print(Server)
	speed_up = True