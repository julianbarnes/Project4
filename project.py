from socket import *
import sys
import io
import argparse
import os
import string
import thread
import easygui   
import StringIO
import gzip


# Create a server socket, bind it to a port and start listening
def main():
	#Request params from user
	args = get_params()
	#Initialize socket of proxy
	client_proxy = initialize_socket(args)
	client_proxy.listen(10)
	
	global state
	state = ["zip"]
	while True:
		print('-----------------------------------------------------------------------')
		counter[0] = counter[0] + 1
		print(str(counter[0]) + "\n")
		thread.start_new_thread(request_proxy, (client_proxy,))

	client_proxy.close()
	sys.exit()
	
			
#Obtain the port number for the proxy from the user
def get_params():
	#Initialize parser
	parser = argparse.ArgumentParser(description='Configure IP Address and Port number for server.')
	parser.add_argument('port', type=int, help='Port number')
	parser.add_argument('features', nargs='*', help='Enter the features you want the proxy to implement')
	
	#Set variable args to results of parser
	args = parser.parse_args()
	return args

#Send request to the server
def request_server(host, port, request, proxy_client):
	try:
		send_socket = socket(AF_INET, SOCK_STREAM)                                  
		#Connect the socket to port 80 (Internet) and send request
		send_socket.connect((host, port))
		send_socket.send(request)
		request_message(request, "[CLI --- PRX ==> SRV]")
		switch_state(request)
		
		response = send_socket.recv(1024)
		response_message(response, "[CLI --- PRX <== SRV]")
		do_feature(response)
		
		if("zip" not in state):
			proxy_client.send(response)
			response_message(response, "[CLI <== PRX --- SRV]")
			while True:
				#Receive response from server to proxy
				response = send_socket.recv(1024)
				#Send response from proxy to client
				if(len(response) > 0): 
					proxy_client.send(response)
					response_message(response, "[CLI <== PRX --- SRV]")

		#Close server socket and client socket
		send_socket.close()
		print("[SRV disconnected]")
		proxy_client.close()
		print("[CLI disconnected]")
		

	except Exception as e:
		print(e)
		#Close server socket and client socket 
		send_socket.close()
		#print("[SRV disconnected]\n")
		proxy_client.close()
		#print("[CLI disconnected]\n")

#Initialize socket that receives requests from the client 
def initialize_socket(args):
	global counter
	counter = [0]
	try:
		#Initialize socket 
		client_proxy = socket(AF_INET, SOCK_STREAM)
		client_proxy.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
		#Bind socket to port 
		client_proxy.bind(('',args.port))
		#Set socket to listen for connection requests
		
		return client_proxy
		print('Starting proxy server on port ' + str(args.port))
		
	except Exception, e:
		print("Connection Error\n")
		print(e)
		
#Receives requests from the client to the proxy	
def request_proxy(client_proxy):
	#Start receiving data from the client
		proxy_client, addr = client_proxy.accept()
		print("[CLI connected to " + str(addr[0]) + ":" + str(addr[1]) + "]\n")
		#Receive the request from the client to proxy
		request = proxy_client.recv(1024)
		
		#Remove hop to hop headers from request
		request = remove_hopper(request)
		request_message(request, "[CLI ==> PRX -- SRV]")
		#Extract host and port number from request
		host, port = get_host(request)
		request_server(host, port, request, proxy_client)
			
		
	
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
def request_message(message, sign):
	print(sign)
	first_header = message.split("\n")[0]
	print(" > " + first_header)
	#print(message) #REMOVE WHEN DONE
	
#Prints the status code, content-type, and content-length of response
def response_message(message, sign):
	lines = message.split("\n")
	status_code = ""
	#Searches for line with status code
	status_code = lines[0][9:]
	
	content_type = ""
	#Searches for line with content type
	for line in lines:
		if(line.split(":")[0] == "Content-Type"):
			content_type = line.split(" ")[1]
			break
			
	if(lines[0].find("HTTP") != -1):
		print(sign)
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

def switch_state(message):
	#-mt -comp -popup
	lines = message.split("\n")
	#print(lines[0])
	if("?start_popup" in lines[0]):
		state.append("popup")
	if("?start_popup" in lines[0]):
		state.remove("popup")	
	

def do_feature(response):
	if("popup" in state):
		start_popup()
		
	if("zip" in state):
		print("ZIPPED\n")
		headers = response.split("\r\n\r\n")[0]
		body = response.split("\r\n\r\n")[1]
		zipped_response = StringIO.StringIO()
		with gzip.GzipFile(fileobj=zipped_response, mode="w") as zipper:
			zipper.write(body)
			while True:
				#Receive response from server to proxy
				response = send_socket.recv(1024)
				#Send response from proxy to client
				if(len(response) > 0): 
					zipper.write(response)

		response_message(response, "[CLI <== PRX --- SRV]")			
		proxy_client.send(headers + "\r\n\r\n")
		proxy_client.send(zipped_response)

def start_popup():
	easygui.msgbox("You have been hacked!", title="Hacked!")
	
def file_zip(response):
	contents = response.split("\r\n\n")
	headers = contents[0]
	body = contents 
	
	
main()


