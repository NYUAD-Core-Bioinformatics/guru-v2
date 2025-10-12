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
    """Run hpcrunner remotely and log only filtered columns."""

    conf = kwargs.get('dag_run').conf
    status_dir = conf.get("status_dir")
    if not status_dir:
        raise ValueError("status_dir not provided in dag_run.conf")

    template = Environment(loader=BaseLoader).from_string(submit_script)
    rendered_command = template.render(status_dir=status_dir)

    logger.info(f"Executing hpcrunner on {status_dir}")

    ssh_hook = SSHHook(ssh_conn_id='guru_ssh')
    ssh = ssh_hook.get_conn()

    try:
        stdin, stdout, stderr = ssh.exec_command(rendered_command)
        output = stdout.read().decode("utf-8")
        err_output = stderr.read().decode("utf-8")
        exit_code = stdout.channel.recv_exit_status()

        if err_output.strip():
            logger.warning(f"Remote stderr: {err_output}")
        if exit_code != 0:
            raise Exception(f"Remote command failed with exit code {exit_code}")

        #Parse only relevant columns
        rows, header = [], []
        for line in output.splitlines():
            if re.match(r'^\|', line):
                parts = [p.strip() for p in line.strip('| \n').split('|')]
                if "JobName" in parts:
                    header = parts
                elif len(parts) >= 6:
                    rows.append(parts)

        # Extract just JobName, Complete, Running
        wanted = ["JobName", "Complete", "Running"]
        idx = [header.index(c) for c in wanted if c in header]

        formatted = ["| " + "    | ".join(wanted) + " |",
                     "+--------------+----------+---------+"]
        for r in rows:
            vals = [r[i] for i in idx]
            formatted.append("| {:<12} | {:<8} | {:<7} |".format(*vals))

        summary = "\n".join(formatted)
        logger.info("\n")
        logger.info("---- Downstream Summary ----\n" + summary)
        logger.info("\n")

    except Exception as e:
        logger.error(f"Error during SSH execution: {e}")
        raise
    finally:
        ssh.close()

    return {"summary_text": summary}
