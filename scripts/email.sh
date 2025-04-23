#!/bin/bash

#############################################################################
# Arguments for Guru initialization - Email
############################################################################

## Add email 
airflow connections add guru_email --conn-type email --conn-host smtp.gmail.com --conn-login <Specify-email-account> --conn-password <Specify-email-password> --conn-port 465
