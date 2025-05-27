#!/bin/bash
#############################################################################
# To build image, followed by starting containers.
############################################################################
docker compose up --build -d 
sleep 60
echo "Wait for few seconds"
docker compose restart
echo "Guru setup is completed now"
echo "Check for access instruction in github page"
