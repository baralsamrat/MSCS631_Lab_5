#!/bin/bash
# main.sh: Script to run and demonstrate the HTTP Web Proxy Server lab.

# Check if the proxy server file exists
if [ ! -f ProxyServer.py ]; then
    echo "Error: ProxyServer.py not found in the current directory."
    exit 1
fi

# Start the proxy server on localhost (127.0.0.1) at port 8888 in the background.
echo "Starting Proxy Server on 127.0.0.1:8888..."
python ProxyServer.py 127.0.0.1 &
PROXY_PID=$!

# Allow some time for the server to initialize.
sleep 2

# Demonstrate the lab by requesting a webpage via the proxy.
# The first request should fetch the content from the remote server.
echo "Requesting web page via proxy (first time)..."
curl http://127.0.0.1:8888/www.google.com

echo -e "\n\nRequesting web page via proxy (second time, expecting a cache hit)..."
curl http://127.0.0.1:8888/www.google.com

# Wait a bit to let the user see the output.
sleep 2

# Stop the proxy server.
echo "Stopping Proxy Server..."
kill $PROXY_PID

echo "Lab demonstration complete."
