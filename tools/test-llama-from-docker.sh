#!/bin/bash

#docker run --rm curlimages/curl ip route show
#exit
echo "Try connecting from docker curl with host.docker.internal w/o host-gateway ..."

docker run --rm curlimages/curl curl -X POST "http://host.docker.internal:8081/v1/chat/completions" -H "Content-Type: application/json" -d '{"messages": [{"content": "Say this is a test.", "role": "user"}], "model": "gpt-4o-mini"}'

echo ""
echo "Try connecting from docker curl with host.docker.internal w/ host-gateway ..."

docker run --add-host=host.docker.internal:host-gateway --rm curlimages/curl curl -X POST "http://host.docker.internal:8081/v1/chat/completions" -H "Content-Type: application/json" -d '{"messages": [{"content": "Say this is a test.", "role": "user"}], "model": "gpt-4o-mini"}'

echo ""
echo "Try connecting from docker with IP 172.17.0.1 ..."

docker run --add-host=host.docker.internal:host-gateway --rm curlimages/curl curl -X POST "http://172.17.0.1:8081/v1/chat/completions" -H "Content-Type: application/json" -d '{"messages": [{"content": "Say this is a test.", "role": "user"}], "model": "gpt-4o-mini"}'
# 172.17.0.1
# 192.168.0.124
