#!/bin/bash
# main.sh
# This script runs the ProxyServer.py implementation of the HTTP Web Proxy Server,
# then uses curl to fetch web pages via the proxy.
# For each target host, it performs two requests:
#   1. The first request fetches the page from the remote server (and caches it).
#   2. The second request demonstrates a cache hit.
# The output for each target is saved to a separate text file.

# Check if the proxy server file exists
if [ ! -f ProxyServer.py ]; then
    echo "Error: ProxyServer.py not found in the current directory."
    exit 1
fi

# Start the proxy server on localhost (127.0.0.1) at port 8888.
# (Adjust the IP/port if needed.)
echo "Starting Proxy Server on 127.0.0.1:8888..."
python ProxyServer.py 127.0.0.1 &
PROXY_PID=$!

# Allow some time for the server to initialize.
sleep 2

# Define an associative array for target hosts.
declare -A targets
targets=( 
    ["google"]="www.google.com"
    ["bbc"]="www.bbc.co.uk"
    ["baidu"]="www.baidu.com"
    ["uol"]="www.uol.com.br"
)

# Loop over each target host, fetching the web page twice to show caching.
for key in "${!targets[@]}"; do
    url=${targets[$key]}
    output_file="output_${key}.txt"
    
    echo "Fetching $url via proxy (first request: remote fetch)..."
    # The -x option tells curl to use the proxy at 127.0.0.1:8888.
    curl -s -x 127.0.0.1:8888 "http://$url" > "$output_file"
    
    echo "Fetching $url via proxy (second request: should hit cache)..."
    curl -s -x 127.0.0.1:8888 "http://$url" >> "$output_file"
    
    echo "Output for $url saved in $output_file"
done

# Stop the proxy server.
echo "Stopping Proxy Server..."
kill $PROXY_PID

echo "Lab demonstration complete."
