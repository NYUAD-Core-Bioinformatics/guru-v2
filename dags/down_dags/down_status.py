import re
import logging
from jinja2 import Environment, BaseLoader
from airflow.providers.ssh.hooks.ssh import SSHHook

logger = logging.getLogger('down_status')
logger.setLevel(logging.INFO)

submit_script = """
module load gencore gencore_biosails
hpcrunner.pl stats --data_dir {{ status_dir }}
"""

def downstream_status(**kwargs):
    """Run hpcrunner remotely and fail DAG if no submission info is found."""

    conf = kwargs.get('dag_run').conf or {}
    status_dir = conf.get("status_dir")
    if not status_dir:
        raise ValueError("status_dir not provided in dag_run.conf")

    # render the command
    rendered_command = Environment(loader=BaseLoader).from_string(submit_script).render(
        status_dir=status_dir
    )
    logger.info(f"Executing hpcrunner on {status_dir}")

    ssh = SSHHook(ssh_conn_id='guru_ssh').get_conn()

    try:
        stdin, stdout, stderr = ssh.exec_command(rendered_command)
        output = stdout.read().decode("utf-8")
        err_output = stderr.read().decode("utf-8")
        exit_code = stdout.channel.recv_exit_status()

        if err_output.strip():
            logger.warning(f"Remote stderr: {err_output}")

        #CASE 1: hpcrunner says no submission info → fail
        if "does not contain any submission info" in output:
            logger.error(f"No submission info found in {status_dir}")
            raise RuntimeError(f"hpcrunner: no submission info in {status_dir}")

        #CASE 2: exit code non-zero → fail
        if exit_code != 0:
            raise RuntimeError(f"hpcrunner failed with exit code {exit_code}")

        # parse only table lines
        lines = [l for l in output.splitlines() if l.strip().startswith("|")]
        if not lines:
            raise RuntimeError(f"No hpcrunner output table found in {status_dir}")

        # extract header and rows
        header = [h.strip() for h in lines[0].strip("| ").split("|")]
        rows = [r for r in lines[1:] if "JobName" not in r]
        if not rows:
            raise RuntimeError(f"No hpcrunner job rows found in {status_dir}")

        # build summary table
        wanted = ["JobName", "Complete", "Running"]
        idx = [header.index(c) for c in wanted if c in header]

        summary_lines = [
            f"| {' | '.join(wanted)} |",
            "+--------------+----------+---------+",
        ]
        for line in rows:
            parts = [p.strip() for p in line.strip("| ").split("|")]
            vals = [parts[i] for i in idx]
            summary_lines.append("| {:<12} | {:<8} | {:<7} |".format(*vals))

        summary = "\n".join(summary_lines)
        logger.info("---- Downstream Summary ----\n" + summary)

    except Exception as e:
        # raise to fail the DAG task
        logger.error(f"Downstream status failed: {e}")
        raise
    finally:
        ssh.close()

    return {"summary_text": summary}

