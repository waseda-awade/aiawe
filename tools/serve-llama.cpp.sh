#!/bin/bash

/home/oem/llama.cpp/build/bin/llama-server -m '/home/oem/llama.cpp/models/Llama-3.3-70B-Instruct-Q5_K_M.gguf' --host 0.0.0.0 --port 8081 --gpu-layers 35
