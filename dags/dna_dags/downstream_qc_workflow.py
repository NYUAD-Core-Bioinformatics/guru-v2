import time
import os
from airflow.providers.ssh.hooks.ssh import SSHHook
import logging

def downstream_qc_workflow_to_slurm(**kwargs):
    logger = logging.getLogger("airflow.task")

    ssh = SSHHook(ssh_conn_id='guru_ssh').get_conn()
    conf = kwargs.get('dag_run').conf

    selected_workflow = conf.get("selected_workflow")
    selected_items = conf.get("selected_items")
    base_path = conf.get("base_path")

    if not all([selected_workflow, selected_items, base_path]):
        raise ValueError("Missing workflow parameters!")

    # Remove *.yml and assign time as suffix.
    out = f"{os.path.splitext(selected_workflow)[0]}_{time.strftime('%Y%m%d_%H%M')}"

    submit_script = f"""
module load gencore gencore_biosails
cd {base_path}
biox run --samples {selected_items} -w {selected_workflow} -o {out}.sh
hpcrunner.pl submit_jobs -i {out}.sh --project {out}
"""

    stdin, stdout, stderr = ssh.exec_command(submit_script)
    output, error = stdout.read().decode().strip(), stderr.read().decode().strip()
    
    ssh.close()

    logger.info("SLURM Error:\n%s", error if error else "No errors.")

    
    if error and "Loading module" not in error:
        raise Exception(f"SLURM Submission Error:\n{error}")