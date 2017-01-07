from socket import * #importing the socket module
from struct import* #importing the sturct module
import time  #importing the time module
global debug
debug = False
UPS = []
dest_port_num = 9997
class TCP_Client_Header: #using class object to make TCP datagram header
	
    class packet_field:# linked list implementation, easier to transfer list values into class object
	
	def __init__(self):
		self.packet_field = 'b'
		self.packet_value = 'empty'
		self.next = None
       	
    def  __init__(self): # fill in boxes in the header rfr pg 60 transport layer
	self.headptr = None
	self.tailptr = None
	self.download = False

        """i_port_num =source port #
            e_port_num = dest port # which is 9998
            seq_num= sequence #
            ack_num = acknowlegdement #
            head_len = head length
            urg_data = urgent data (gen .not used)
            ack_vld = is ack # valid?
            push_data = push data now
            R_S_F = Connection estab (setup commands)RST,SYN,FIN
            recv_wdw = receive window
            checksum = internet checksum
            urg_ptr = urgent data pointer
            app_data = application data"""
   	        
 

    def __str__(self): # creates a readable text for the object

	runner = self.headptr
	retval = ""
	if self.headptr == None:
		return "nothing here, somethings up"
	
	while runner != self.tailptr:
		retval += runner.packet_field + "," + runner.packet_value + ","
		runner = runner.next
	retval += runner.packet_field + "," + runner.packet_value
	return retval

    def __len__(self):
	length = 0
	runner = self.headptr
	while runner != self.tailptr.next:
		runner = runner.next
		length += 1
	return length
    
    def insert(self,datagram):
	#self.headptr = None would use this but I am too far in the program
	x = 0
	y = 0
	cello = 'please work' #test value to see if argument is a file or string
	 
	if datagram.find('.txt') != -1 :
		datagram = datagram.strip(".txt")
		f = open(datagram,'r')
		fields = f.read()
		fields = fields.split(',')
	
		while x < len(fields):
			self.insert_packet(fields[x],fields[x+1])
			x+= 2
		self.download == True
		x = 0
	
	else:
		datagram = datagram.split(',')
		while y < len(datagram):
			self.insert_packet(datagram[y],datagram[y+1])
			y += 2
		y = 0

    def insert_packet(self,field,value):
		new_field =self.packet_field()
		new_field.packet_field = field
		new_field.packet_value = value	
		if self.headptr == None:
			self.headptr = new_field
        		self.tailptr = new_field
 		else:
			self.tailptr.next = new_field
			self.tailptr = new_field
    
    def check(self,header_field,header_value): #checks if everything matches up
	check = self.__str__()
	check = check.split(',')
	for i in range(len(check)):
		if check[i]== header_field:
			if check[i+1]== header_value:
				return True
	return False
    def replace(self,header_field,header_value): #Should only replace values in header fields 
	z = 0
	replace  =self. __str__()
	replace = replace.split(',')
	for i in range(len(replace)):
		if replace[i] == header_field:
			replace[i+1] = header_value
			self.headptr = None
			break
	while z < len(replace):
		self.insert_packet(str(replace[z]),str(replace[z+1]))
		z +=2
	z = 0

    def steal_a_part(self,header_field,printer = False,retval = False): #sends the transport in open and teardown also returns values for specific fields
	x = 0
	part = self.__str__()
	part = part.split(",")
	for i in range(len(part)):
		if part[i] == header_field:
			if printer:
				if retval:
					return int(part[i+1])
				return "This is the   " + str(header_field) + "%3s" %  part[i+1] 
			value = part[i+1]
			field = part[i] 
			del part[i+1]
			del part[i]
			break

	self.headptr = None
	while x <len(part):

		self.insert_packet(str(part[x]),str(part[x+1]))	
		x += 2
	x = 0
	return field,value

		
  	
if __name__ == "__main__":	
	Host = TCP_Client_Header() # to set up and open teardown commands
	serverName = "127.0.0.1" #name of server
	
	clientSocket = socket(AF_INET,SOCK_DGRAM) # type of connection set up
	Host.insert('init_packet_fields.txt')#now the packet is set up
	#the listen part where server listens for client

	Host.replace("SYNbit",1)
	Host.replace("seq_num",200)
	impt_field,impt_value = Host.steal_a_part("app_data")
	clientSocket.sendto(str(Host).encode(),(serverName,dest_port_num))
	Host.headptr = None
	print("Asking to make a connection with the server")
	#the answer part where server says its okay to recv

       	message,serveraddr = clientSocket.recvfrom(2048)
	message = message.decode()
	message = str(message)
	Host.headptr = None
	Host.insert(message)
	get_i_answer = Host.check("seq_num","201")
	get_ii_answer = Host.check("ACKbit","1")
	get_iii_answer = Host.check("ack_num","201")
	if get_i_answer & get_ii_answer & get_iii_answer:
		print("The server has answered the client")
		Host.replace("ack_num",202)
		clientSocket.sendto(str(Host).encode(),(serverName,dest_port_num))
	else:
		print("Didnt get it")
	clientSocket.sendto(str(Host).encode(),(serverName,dest_port_num))

	x = 1 # for 1st of 32 sent out below
	y = 0 # keeps track of appropriate seq_num
	z = 1 #keep tracks of sequence of packets sent
	t = 0 #tester variable
	limit = 0 #so it wont add twice off second flag
	send_correct = False
	package_note = False
	Client = Host # to send packets back and forth
	Client.insert_packet(impt_field,impt_value)
	finish_data = 0
	bill = []
	while finish_data != 32: #so client can get extra ack if it did not get it in time

		while True:	
			message, serveraddr = clientSocket.recvfrom(2048)
			if message == "None":
				break
			Client.headptr = None
			Client.insert(message)
			current_data = Client.steal_a_part("seq_num",True,True)
			bill.append(current_data)
			Client.replace("ack_num",x)
			x += 1
			z += 1
			UPS.append(str(Client))

		print("\n")
		print("This is the shipment we got from the server")
		print(bill)
		if debug:
			print("x")
			print(x)
			print("y")
			print(y)
			print("z")
			print(z)
			print("finish_data")
			print(finish_data)
		if bill[0] < finish_data:
			print("We didn't send the acks in time")
			UPS = []
			for e in bill:
				Client.replace("ack_num",e)
				UPS.append(str(Client))
			x -= len(bill)

		finish_data = Client.steal_a_part("seq_num",True,True)
		bill = []
		y += z #for getting the right seq_num from packets
		z = 0
		
		if debug:	
			print("this is y")
			print(y)
			print(" this is x")
			print(x)
		for i in UPS:
			if t == 0 and i == UPS[-2]:# It works server sends packets again
				time.sleep(1)
				t += 1
				pass
			clientSocket.sendto(str(i).encode(),(serverName,dest_port_num))
		clientSocket.sendto(str(None).encode(),(serverName,dest_port_num))
		UPS = []
		bill = []

	if debug:
		print("what now?")
		pass
	Host = Client
	#a,b = Host.steal_a_part("app_data")
	Host.replace("FINbit",1)
	Host.replace("seq_num",203)
	clientSocket.sendto(str(Host).encode(),(serverName,dest_port_num))
	clientSocket.recvfrom
	while Host.download == False:
		
		if Host.check("FINbit","1") & Host.check("seq_num","204"):
			Host.replace("ack_num",33)
			Host.replace("ACKbit",2)

			clientSocket.sendto(str(Host).encode(),(serverName,dest_port_num))
			print("The server is starting to close its socket")
			clientSocket.close()
			Host.download = True

		elif Host.check("ACKbit","2") & Host.check ("ack_num","39"):
			clientSocket.sendto(str(Host).encode(),(serverName,dest_port_num))
			print("Waiting for the server to close")
		# closing the connection

		elif Host.check("seq_num","201") & Host.check("ACKbit","1") & Host.check("ack_num","201"):
			Host.replace("FINbit",1)
			Host.replace("seq_num",203)
			clientSocket.sendto(str(Host).encode(),(serverName,dest_port_num))
			print("The server is starting to close its connection")
		
		if Host.download == False:
			message, serveraddr = clientSocket.recvfrom(2048)
			message = message.decode()
			message = str(message)
			if debug:
				#print("What I got from the server")
				#print(message)
				pass
			Host.headptr = None
			try:
				Host.insert(message)
			except:
				pass