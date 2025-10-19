import json
import os
from dna_dags.slurm_helpers import poll_slurm_job_qc
import tempfile
from pprint import pprint

"""
[2023/03/29 23:53:47] Updating task dependencies. This may take some time...
[2023/03/29 23:54:08] Job Summary
[2023/03/29 23:54:08]
.---------------------------------------------------------------------.
| Job Name                | Scheduler ID | Task Indices | Total Tasks |
+-------------------------+--------------+--------------+-------------+
| raw_fastqc              |      1327214 | 1-200        |         200 |
| raw_fastqc              |      1327313 | 201-374      |         174 |
| trimmomatic             |      1327588 | 375-561      |         187 |
| fastp                   |      1327658 | 562-748      |         187 |
| fastp_fastqc            |      1327659 | 749-948      |         200 |
| fastp_fastqc            |      1327660 | 949-1122     |         174 |
| multiqc                 |      1327661 | 1123-1123    |           1 |
| remove_trimmomatic_PE   |      1327662 | 1124-1310    |         187 |
| remove_trimmomatic_logs |      1327663 | 1311-1497
    |         187 |
'-------------------------+--------------+--------------+-------------'

[2023/03/29 23:54:08] Your jobs have been submitted.
[2023/03/29 23:54:08] Experimental! For status updates please run:
[2023/03/29 23:54:08] hpcrunner.pl stats
[2023/03/29 23:54:08] To get status updates for only this submission please run:
[2023/03/29 23:54:08] hpcrunner.pl stats --data_dir /scratch/gencore/novaseq/230327_A00534_0123_AH3NKTDSX5/Unaligned/hpc-runner/2023-03-29T23-53-05/NCS-417-qc/logs/000_hpcrunner_logs/stats
"""


def check_for_hpcrunner_stats(line, context):
    output_path = context['dag_run'].conf['output_path']
    if output_path not in line:
        return False
    else:
        if 'stats' in line and '000_hpcrunner_logs' in line:
            return True
        else:
            return False


def get_hpcrunner_data_dir(output, context):
    output = ''.join(output)
    output = output.split("\n")
    # Filter to get rid of the line
    data_dir_line = list(filter(lambda x: check_for_hpcrunner_stats(str(x), context), output))
    # Split on whitespace, new line, etc
    stats_lines = data_dir_line[0].split()
    # Get the stats line by itself
    data_dir_line = list(filter(lambda x: check_for_hpcrunner_stats(str(x), context), stats_lines))
    stats_line = data_dir_line[0]
    return stats_line


def get_submission_ids(sftp, output, context):
    """
    Read in the submission.json and get a list of job_ids
    :param output:
    :return:
    """
    stats_dir = get_hpcrunner_data_dir(output, context)
    print('Stats dir is {}'.format(stats_dir))
    tfile_local_submission = tempfile.NamedTemporaryFile(delete=False)
    submission_data = os.path.join(str(stats_dir), 'submission.json')
    sftp.get(submission_data, tfile_local_submission.name)
    f = open(tfile_local_submission.name)
    data = json.loads(f.read())
    pprint(data)
    submission_data = []
    for job in data['jobs']:
        job_name = job['job']
        submission_ids = list(map(lambda x: x['scheduler_id'], job['schedule']))
        for submission_id in submission_ids:
            job_data = {}
            job_data['job_name'] = job_name
            job_data['submission_id'] = submission_id
            submission_data.append(job_data)

    return submission_data


def poll_biosails_submissions(ssh, sftp, output, context):
    """
    Poll the biosails job submissions
    :param ssh:
    :param output:
    :param context: Airflow Context
    :return:
    """
    # TODO Set this up in a queue, so it can run in the background every hour or so
    # And update the JIRA ticket
    submission_data = get_submission_ids(sftp, output, context)
    from pprint import pprint
    pprint(submission_data)
    for data in submission_data:
        submission_id = data['submission_id']
        job_status = poll_slurm_job_qc(ssh, submission_id)
        data['job_status'] = job_status

    pprint(submission_data)
    return submission_data