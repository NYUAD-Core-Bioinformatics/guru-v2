from datetime import datetime
from airflow import DAG
from airflow.providers.ssh.operators.ssh import SSHOperator
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.providers.ssh.hooks.ssh import SSHHook

from dna_dags.downstream_qc_workflow import downstream_qc_workflow_to_slurm
# from dna_dags.poll_slurm_job_status import poll_slurm_job_status

#Loading smtp module
# import smtplib
# from email.message import EmailMessage
# from airflow.hooks.base import BaseHook


"""Defining dag profiles, schedule_interval is set to None, since it is based on trigger based dagrun"""

dag = DAG('dnaseq_dag', description='DNAseq DAG',
          schedule_interval=None,
          start_date=datetime(2024, 4, 1), catchup=False)

ssh_hook = SSHHook(ssh_conn_id='guru_ssh')
ssh_hook.no_host_key_check = True

rsync_work_to_scratch_command = """
        mkdir -p /scratch/jr5241/test-airflow
        rsync -av /scratch/jr5241/soft/* /scratch/jr5241/test-airflow
"""

rsync_work_to_scratch_task = SSHOperator(
    task_id='rsync_work_to_scratch',
    ssh_hook=ssh_hook,
    command=rsync_work_to_scratch_command,
    dag=dag
)



bash_task = BashOperator(
    task_id="print_selected_items",
    bash_command='echo "Selected files: {{ dag_run.conf["selected_items"] }} and Workflow as: {{ dag_run.conf["selected_workflow"] }}"',
    dag=dag,
)


"""Defining QC workflow using Python operator"""
downstream_qc_workflow_task = PythonOperator(
    dag=dag,
    task_id='downstream_qc_workflow',
    provide_context=True,
    python_callable=downstream_qc_workflow_to_slurm,
)

# poll_slurm_task = PythonOperator(
#     task_id='poll_slurm_status',
#     python_callable=poll_slurm_job_status,
#     provide_context=True,
#     dag=dag,
# )

# email_pre_sent_task = PythonOperator(
#     task_id='email_pre_sent',
#     retries=1,
#     python_callable=run_pre_email_task,
#     dag=dag
# )

# email_post_sent_task = PythonOperator(
#     task_id='email_post_sent',
#     retries=1,
#     python_callable=run_post_email_task,
#     dag=dag
# )

rsync_work_to_scratch_task >> bash_task >> downstream_qc_workflow_task 



