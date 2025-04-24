#!/bin/bash
#############################################################################
# To build image, followed by starting containers.
############################################################################
docker compose up --build -d 
sleep 60
docker compose restart
