from datetime import datetime
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.ssh.hooks.ssh import SSHHook

#Loading custom dag scripts
from dna_dags.downstream_qc_workflow import downstream_qc_workflow_to_slurm
from dna_dags.email_post import generate_post_email_task

# Loading smtp module
import smtplib
from email.message import EmailMessage
from airflow.hooks.base import BaseHook


"""Defining dag profiles, schedule_interval is set to None, since it is based on trigger based dagrun"""

dag = DAG('dnaseq_dag', description='DNAseq DAG',
          schedule_interval=None,
          start_date=datetime(2025, 10, 1), catchup=False)

ssh_hook = SSHHook(ssh_conn_id='guru_ssh')
ssh_hook.no_host_key_check = True


"""Defining QC workflow using Python operator"""
downstream_analysis_task = PythonOperator(
    dag=dag,
    task_id='Downstream_analysis',
    python_callable=downstream_qc_workflow_to_slurm,
)

email_post_sent_task = PythonOperator(
     task_id='email_post_sent',
     python_callable=generate_post_email_task,
     dag=dag
)

downstream_analysis_task >> email_post_sent_task
