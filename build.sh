#!/bin/bash
#############################################################################
# To build image, followed by starting containers.
############################################################################
echo "==========================="
echo "Guru setup is completed now"
echo "==========================="
docker compose up --build -d 
sleep 10
echo "Wait for few seconds"
docker compose restart
sleep 10
echo "==========================="
echo "Guru setup is completed now, Copy localhost:8080 in browser."
echo "==========================="
