# Access host API from docker

Suppose we have a llama.cpp server running in the host machine on port `8081` and we want to access it from the docker container.
These are the steps to do it.

## Allow 8081 port

``` sh
sudo ufw allow 8081
```

## llama.cpp is running in host machine

Note the host IP address and port number.

```sh
/home/oem/llama.cpp/build/bin/llama-server -m '/home/oem/llama.cpp/models/Llama-3.3-70B-Instruct-Q5_K_M.gguf' --host 0.0.0.0 --port 8081 --gpu-layers 35
```

The `--host 0.0.0.0` part is crucial. It allows the docker container to access the host machine.

## The app (django) is running in docker

This is important for Linux host machine.

``` yml
services:
  django:
    extra_hosts:
      - "host.docker.internal:host-gateway"
```

Now we should be able to access the host API from the docker container with `http://host.docker.internal:8081/v1/chat/completions`.

Test it out with this docker command:

```sh
docker run --add-host=host.docker.internal:host-gateway --rm curlimages/curl curl -X POST "http://host.docker.internal:8081/v1/chat/completions" -H "Content-Type: application/json" -d '{"messages": [{"content": "Say this is a test.", "role": "user"}], "model": "gpt-4o-mini"}'
```
