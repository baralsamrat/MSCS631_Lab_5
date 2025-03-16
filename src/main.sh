#!/bin/bash
# main.sh
# This script runs the main.py implementation of the HTTP Web Proxy Server,
# then uses curl to fetch web pages via the proxy. For each target host, it performs two requests:
#   1. The first request fetches the page from the remote server (and caches it).
#   2. The second request demonstrates a cache hit.
# The output for each target is saved to a separate text file.

# Check if main.py exists.
if [ ! -f main.py ]; then
    echo "Error: main.py not found in the current directory."
    exit 1
fi

# Start the proxy server on localhost at port 8888.
echo "Starting Proxy Server on 127.0.0.1:8888..."
python main.py 127.0.0.1 &
PROXY_PID=$!

# Allow some time for the server to initialize.
sleep 2

# Define target hosts.
declare -A targets
targets=( 
    ["google"]="www.google.com"
    ["bbc"]="www.bbc.co.uk"
    ["baidu"]="www.baidu.com"
    ["uol"]="www.uol.com.br"
)

# For each target host, perform two curl requests (first for remote fetch, second for cache hit).
for key in "${!targets[@]}"; do
    url=${targets[$key]}
    output_file="output_${key}.txt"
    
    echo "Fetching $url via proxy (first request: remote fetch)..."
    curl -s -x 127.0.0.1:8888 "http://$url" > "$output_file"
    
    echo "Fetching $url via proxy (second request: cache hit)..."
    curl -s -x 127.0.0.1:8888 "http://$url" >> "$output_file"
    
    echo "Output for $url saved in $output_file"
done

# Stop the proxy server. Suppress error output if the process has already terminated.
echo "Stopping Proxy Server..."
kill $PROXY_PID 2>/dev/null

echo "Lab demonstration complete."
