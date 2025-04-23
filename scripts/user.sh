#!/bin/bash

#############################################################################
# Arguments for Guru initialization - User
############################################################################

#Delete default airflow user
airflow users delete -u airflow

#Create gencore user
airflow users create --username guru --password admin --firstname Admin-user --lastname Admin-user --role Admin --email test@example.com
