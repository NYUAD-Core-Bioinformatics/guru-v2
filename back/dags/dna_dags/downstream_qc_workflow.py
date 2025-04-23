import os
import time
import logging
from jinja2 import Environment, BaseLoader
from airflow.providers.ssh.hooks.ssh import SSHHook

# ✅ Custom helpers
from dna_dags.ssh_helpers import execute_ssh_command_return_stdout_stderr, initialize_ssh
from dna_dags.biosails_helper import poll_biosails_submissions

# ✅ Logging setup
logger = logging.getLogger('submit_qc_workflow')
logger.setLevel(logging.DEBUG)

# ✅ Bash template to render and run on the remote server
submit_script = """
module load gencore gencore_biosails
cd {{ base_path }}
biox run --samples {{ selected_items }} -w {{ selected_workflow }} -o {{ out }}.sh
hpcrunner.pl submit_jobs -i {{ out }}.sh --project {{ out }}
"""

def downstream_qc_workflow_to_slurm(ds, **kwargs):
    """Render a QC workflow with biox, submit via hpcrunner, then poll for job completion."""

    # ✅ Parse DAG config
    conf = kwargs.get('dag_run').conf
    selected_workflow = conf.get("selected_workflow")
    selected_items = conf.get("selected_items")
    base_path = conf.get("base_path")

    if not all([selected_workflow, selected_items, base_path]):
        raise ValueError("Missing workflow parameters!")

    # ✅ Generate output suffix from timestamp
    out = f"{os.path.splitext(os.path.basename(selected_workflow))[0]}_{time.strftime('%Y%m%d_%H%M')}"

    # ✅ Set up SSH
    ssh_hook = SSHHook(ssh_conn_id='guru_ssh')
    ssh = ssh_hook.get_conn()
    sftp = ssh.open_sftp()

    # ✅ Render the remote bash script
    template = Environment(loader=BaseLoader).from_string(submit_script)
    rendered_command = template.render(
        base_path=base_path,
        selected_workflow=selected_workflow,
        selected_items=selected_items,
        out=out
    )

    logger.info("Rendered SLURM submission command:")
    logger.info(rendered_command)

    # ✅ Execute and capture remote logs
    agg_output = False
    try:
        agg_output = execute_ssh_command_return_stdout_stderr(ssh, rendered_command, logger)
    except Exception as e:
        logger.error(f"Error during SSH command execution: {e}")
        raise

    if agg_output:
        from pprint import pprint
        pprint(agg_output)
        poll_biosails_submissions(ssh, sftp, agg_output, kwargs)
    else:
        raise Exception("No output from biosails submission found!")

    ssh.close()
