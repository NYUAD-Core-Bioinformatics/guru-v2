import paramiko
import argparse
import io
import logging
import os
import sys
import smtplib
from email.message import EmailMessage
from airflow.hooks.base import BaseHook


def generate_pre_email_task(ds, **kwargs):
    dag_run = kwargs['dag_run']
    email_id = dag_run.conf['email_address']
    base_path = dag_run.conf['base_path']
    samples = dag_run.conf['selected_items']
    default = "jr5241@nyu.edu"

    # SMTP configuration begins
    subject = f"Downstream Analysis Initiated"
    body = (f"Your recent downstream analysis has started processing. \n"
                "\n"
                f"Your selected samples are: {samples}.\n"
                f"Your basepath is: {base_path}.\n"
                 "You will automatically be notified once the run has processed successfully.\n"
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
    msg['From'] = "Downstream Analysis Notification"
    # to = (f"{email_id},{default}")
    to = (f"{email_id}")
    msg['To'] = to
    msg['Subject'] = subject
    msg.set_content(body)

    # Initiate the send
    with smtplib.SMTP_SSL(smtp_server, smtp_port)as server:
        server.login(smtp_username, smtp_password)
        server.sendmail(smtp_username, to.split(','), msg.as_string())



# def run_pre_email_task(ds, **kwargs):
#     generate_email_task(ds, **kwargs)
