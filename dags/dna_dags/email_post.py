import argparse
import io
import logging
import os
import sys
import smtplib
from email.message import EmailMessage
from airflow.hooks.base import BaseHook



def generate_email_task(ds, **kwargs):
    dag_run = kwargs['dag_run']
    email_id = dag_run.conf['email_id']
    default = "nyuad.cgsb.cb@nyu.edu"

    # SMTP configuration begins
    subject = f"Processing 10X sequencing run  / Miso ID "
    body = (f"Your recent run  / Miso ID has successfully completed. \n\n"
                 f"Run Path:- /\n"
                 "\n"
                 "For any further inquiries regarding this run, or for further downstream analysis please contact a member of the Core Bioinformatics Team at nyuad.cgsb.cb@nyu.edu \n"
                 "Note that this is an automated message please do not respond to this email as it is not monitored.\n"
                 "\n"
                 "Regards\n"
                 "NYU Abu Dhabi Core Bioinformatics\n")

    # Set the SMTP Connection ID
    smtp_conn_id = 'guru_email'
    smtp_hook = BaseHook.get_connection(smtp_conn_id)

    # SMTP credentials
    smtp_server = smtp_hook.host
    smtp_port = smtp_hook.port
    smtp_username = smtp_hook.login
    smtp_password = smtp_hook.password

    # Compose the template
    msg = EmailMessage()
    msg['From'] = "Sequencing Run Notification"
    to = (f"{email_id},{default}")
    msg['To'] = to
    msg['Subject'] = subject
    msg.set_content(body)

    # Initiate the send
    with smtplib.SMTP_SSL(smtp_server, smtp_port)as server:
        server.login(smtp_username, smtp_password)
        server.sendmail(smtp_username, to.split(','), msg.as_string())



def run_post_email_task(ds, **kwargs):
    generate_email_task(ds, **kwargs)