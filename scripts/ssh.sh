#!/bin/bash

#############################################################################
# Arguments for Guru initialization - SSH
############################################################################

## Defining SSH connection 
airflow connections add  guru_ssh   --conn-type ssh --conn-host <Specify-server-name> --conn-login <Specify-username> --conn-port 22 --conn-extra '{"key_file": "/home/airflow/.ssh/id_rsa", "missing_host_key_policy": "AutoAddPolicy"}'
