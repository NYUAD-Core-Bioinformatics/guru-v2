from datetime import datetime
from airflow import DAG
from airflow.providers.ssh.operators.ssh import SSHOperator
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.providers.ssh.hooks.ssh import SSHHook

from dna_dags.downstream_qc_workflow import downstream_qc_workflow_to_slurm
from dna_dags.email_pre import generate_pre_email_task
from dna_dags.email_post import generate_post_email_task

# Loading smtp module
import smtplib
from email.message import EmailMessage
from airflow.hooks.base import BaseHook


"""Defining dag profiles, schedule_interval is set to None, since it is based on trigger based dagrun"""

dag = DAG('dnaseq_dag', description='DNAseq DAG',
          schedule_interval=None,
          start_date=datetime(2024, 4, 1), catchup=False)

ssh_hook = SSHHook(ssh_conn_id='guru_ssh')
ssh_hook.no_host_key_check = True



bash_task = BashOperator(
    task_id="Display_sample_selection",
    bash_command='echo "Selected files: {{ dag_run.conf["selected_items"] }} and Workflow as: {{ dag_run.conf["selected_workflow"] }}"',
    dag=dag,
)


"""Defining QC workflow using Python operator"""
downstream_analysis_task = PythonOperator(
    dag=dag,
    task_id='Downstream_analysis',
    python_callable=downstream_qc_workflow_to_slurm,
)

email_pre_sent_task = PythonOperator(
     task_id='email_pre_sent',
     python_callable=generate_pre_email_task,
     dag=dag
)

email_post_sent_task = PythonOperator(
     task_id='email_post_sent',
     python_callable=generate_post_email_task,
     dag=dag
)

bash_task >> email_pre_sent_task  >> downstream_analysis_task >> email_post_sent_task
