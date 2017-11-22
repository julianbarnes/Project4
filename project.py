from socket import *
import sys
import io
import argparse
import os
import string
import _thread
import easygui  #REMEMBER TO ADD DEPENDENCY TO START FILE  

			
# Create a server socket, bind it to a port and start listening
def main():
	#Request params from user
	args = get_params()
	#Initialize socket of proxy
	initialize_socket(args)
	while True:
		print('-----------------------------------------------------------------------')
		counter[0] = counter[0] + 1
		print(str(counter[0]) + "\n")
		request_proxy()

	client_proxy.close()
	sys.exit()
	
			
#Obtain the port number for the proxy from the user
def get_params():
	#Initialize parser
	parser = argparse.ArgumentParser(description='Configure IP Address and Port number for server.')
	parser.add_argument('port', type=int, help='Port number')
	
	#Set variable args to results of parser
	args = parser.parse_args()
	return args

#Initialize socket that receives requests from the client 
def initialize_socket(args):
	global counter
	counter = [0]
	try:
		#Initialize socket 
		global client_proxy
		client_proxy = socket(AF_INET, SOCK_STREAM)
		client_proxy.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
		#Bind socket to port 
		client_proxy.bind(('',args.port))
		#Set socket to listen for connection requests
		client_proxy.listen(10)
		print('Starting proxy server on port ' + str(args.port))
		
	except Exception as e:
		print("Connection Error\n")
		print(e)
		
#Receives requests from the client to the proxy	
def request_proxy():
	#Start receiving data from the client
	global proxy_client
	proxy_client, addr = client_proxy.accept()
	print("[CLI connected to " + str(addr[0]) + ":" + str(addr[1]) + "]\n")
	#Receive the request from the client to proxy
	request = proxy_client.recv(1024)
	print("[CLI ==> PRX -- SRV]")
	#Remove hop to hop headers from request
	request = remove_hopper(request)
	request_message(request)
	#Extract host and port number from request
	host, port = get_host(request)
	_thread.start(request_server,(host, port, request))

#Send request to the server
def request_server(host, port, request):
	try:
		send_socket = socket(AF_INET, SOCK_STREAM)                                  
		#Connect the socket to port 80 (Internet) and send request
		send_socket.connect((host, port))
		
		
		send_socket.send(request)
		print("[CLI --- PRX ==> SRV]")
		request_message(request)
		
		while True:
			#Receive response from server to proxy
			response = send_socket.recv(1024)
			print("[CLI --- PRX <== SRV]")
			response_message(response)
			#Send response from proxy to client
			if(len(response) > 0):
				parsed_response = remove_hopper(response) 
				proxy_client.send(response)
				print("[CLI <== PRX --- SRV]")
				response_message(response)
			else:
				break
		#Close server socket and client socket
		send_socket.close()
		print("[SRV disconnected]")
		proxy_client.close()
		print("[CLI disconnected]")
		counter = [0]

	except Exception as e:
		#Close server socket and client socket 
		print(e)
		send_socket.close()
		#print("[SRV disconnected]\n")
		proxy_client.close()
		#print("[CLI disconnected]\n")
		counter = [0]
		

	
#Removes hop to hop headers
def remove_hopper(message):
        lines = message.split("\n")
        hoptohop = ["Connection", "Transfer-Encoding", "Keep-Alive", "Proxy-Authorization", "Proxy-Authentication", "Trailer", "Upgrade"]
        output = ""
        #Copies header lines that are not in hoptohop array
        for line in lines:
                if(line.split(":")[0] not in hoptohop):
                        output = output + line + "\n"
        return output

#Prints the request method for request
def request_message(message):
	first_header = message.split("\n")[0]
	print(" > " + first_header)
	
#Prints the status code, content-type, and content-length of response
def response_message(message):
	print(message)
	lines = message.split("\n")
	status_code = ""
	#Searches for line with status code
	for line in lines:
		if(line.split("/")[0] == "HTTP"):
			status_code = line[9:]
	
	content_type = ""
	#Searches for line with content type
	for line in lines:
		if(line.split(":")[0] == "Content-Type"):
			content_type = line.split(" ")[1]
			break
	#if(status_code != ""):
	print(" > " + status_code)
	print(" > " + content_type)
	print(" " + str(len(message)) + "bytes")

#Extracts host and port number from HTTP request
def get_host(message):
	lines = message.split("\n")
	k = 0
	#Searches for Host line in request
	while lines[k].split(":")[0] != "Host":
		k = k + 1
	host = lines[k][6:-1]
	hostandport = lines[k].split(":")
	if(len(hostandport) > 2):
		port = int(hostandport[2])
	else:
		port = 80
		
	return (host, port)

def start_popup():
	easygui.msgbox("You have been hacked!", title="Hacked!")
		
	
main()


