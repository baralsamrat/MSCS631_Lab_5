from socket import *
import sys

if len(sys.argv) <= 1:
    print('Usage : "python ProxyServer.py server_ip"\n[server_ip : It is the IP Address Of Proxy Server]')
    sys.exit(2)

# Create a server socket, allow address reuse, bind it to a port and start listening.
tcpSerSock = socket(AF_INET, SOCK_STREAM)
tcpSerSock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
tcpSerSock.bind((sys.argv[1], 8888))
tcpSerSock.listen(5)

while True:
    # Start receiving data from the client.
    print('Ready to serve...')
    tcpCliSock, addr = tcpSerSock.accept()
    print('Received a connection from:', addr)
    
    # Receive the request message and decode bytes to string.
    message = tcpCliSock.recv(1024).decode()
    print("Received message:", message)
    
    # Extract the filename from the GET request.
    try:
        request_line = message.split()[1]
    except IndexError:
        tcpCliSock.close()
        continue
    print("Request line:", request_line)
    
    filename = request_line.partition("/")[2]
    print("Filename:", filename)
    
    fileExist = "false"
    filetouse = "/" + filename
    print("File to use:", filetouse)
    
    try:
        # Check whether the file exists in the cache.
        with open(filetouse[1:], "r") as f:
            outputdata = f.readlines()
        fileExist = "true"
        
        # Cache hit: send HTTP 200 OK header and the cached content.
        tcpCliSock.send("HTTP/1.0 200 OK\r\n".encode())
        tcpCliSock.send("Content-Type:text/html\r\n\r\n".encode())
        for line in outputdata:
            tcpCliSock.send(line.encode())
        print('Read from cache')
        
    except IOError:
        if fileExist == "false":
            # Create a socket on the proxy server.
            c = socket(AF_INET, SOCK_STREAM)
            # Remove the "www." prefix if present, for host resolution.
            hostn = filename.replace("www.", "", 1)
            print("Remote host:", hostn)
            try:
                # Connect to the remote server on port 80.
                c.connect((hostn, 80))
                
                # Create a file-like object and send an HTTP GET request.
                fileobj = c.makefile('r', 0)
                getRequest = "GET " + "http://" + filename + " HTTP/1.0\r\n\r\n"
                fileobj.write(getRequest)
                
                # Read the response into a buffer.
                buffer = c.recv(4096)
                
                # Create a new file in the cache and simultaneously send the response to the client.
                tmpFile = open("./" + filename, "wb")
                while len(buffer) > 0:
                    tmpFile.write(buffer)
                    tcpCliSock.send(buffer)
                    buffer = c.recv(4096)
                tmpFile.close()
                c.close()
            except Exception as e:
                print("Illegal request:", e)
                tcpCliSock.send("HTTP/1.0 404 Not Found\r\n".encode())
                tcpCliSock.send("Content-Type:text/html\r\n\r\n".encode())
        else:
            tcpCliSock.send("HTTP/1.0 404 Not Found\r\n".encode())
            tcpCliSock.send("Content-Type:text/html\r\n\r\n".encode())
    
    # Close the connection to the client.
    tcpCliSock.close()
