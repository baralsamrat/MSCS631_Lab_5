from socket import *
import sys

if len(sys.argv) <= 1:
    print('Usage: "python ProxyServer.py server_ip"\n[server_ip : It is the IP Address Of Proxy Server]')
    sys.exit(2)

# Create a server socket, bind it to the specified IP and port, then start listening
tcpSerSock = socket(AF_INET, SOCK_STREAM)
tcpSerSock.bind((sys.argv[1], 8888))  # Use port 8888 (adjust as needed)
tcpSerSock.listen(5)

while True:
    # Start receiving data from the client
    print('Ready to serve...')
    tcpCliSock, addr = tcpSerSock.accept()
    print('Received a connection from:', addr)
    
    # Receive the request message from the client
    message = tcpCliSock.recv(1024)
    print(message)
    
    # Extract the filename from the given message
    print(message.split()[1])
    filename = message.split()[1].partition("/")[2]
    print("Filename:", filename)
    
    fileExist = "false"
    filetouse = "/" + filename
    print("File to use:", filetouse)
    
    try:
        # Check whether the file exists in the cache (local file system)
        f = open(filetouse[1:], "r")
        outputdata = f.readlines()
        f.close()
        fileExist = "true"
        
        # Cache hit: send the cached content with HTTP 200 OK header
        tcpCliSock.send("HTTP/1.0 200 OK\r\n".encode())
        tcpCliSock.send("Content-Type:text/html\r\n\r\n".encode())
        for line in outputdata:
            tcpCliSock.send(line.encode())
        print('Read from cache')
        
    except IOError:
        if fileExist == "false":
            # Create a new socket to fetch the content from the remote web server
            c = socket(AF_INET, SOCK_STREAM)
            hostn = filename.replace("www.", "", 1)
            print("Remote host:", hostn)
            try:
                # Connect to the remote server on port 80
                c.connect((hostn, 80))
                
                # Create a file-like object and send an HTTP GET request for the file
                fileobj = c.makefile('r', 0)
                getRequest = "GET " + "http://" + filename + " HTTP/1.0\r\n\r\n"
                fileobj.write(getRequest)
                
                # Read the response into a buffer
                buffer = c.recv(4096)
                
                # Create a new file in the cache for the requested file.
                # Also, send the response in the buffer to the client socket.
                tmpFile = open("./" + filename, "wb")
                while len(buffer) > 0:
                    tmpFile.write(buffer)
                    tcpCliSock.send(buffer)
                    buffer = c.recv(4096)
                tmpFile.close()
                c.close()
            except Exception as e:
                print("Illegal request:", e)
                # HTTP response message for file not found
                tcpCliSock.send("HTTP/1.0 404 Not Found\r\n".encode())
                tcpCliSock.send("Content-Type:text/html\r\n\r\n".encode())
        else:
            # This branch is not expected to be reached if fileExist remains false.
            tcpCliSock.send("HTTP/1.0 404 Not Found\r\n".encode())
            tcpCliSock.send("Content-Type:text/html\r\n\r\n".encode())
    
    # Close the client socket
    tcpCliSock.close()
