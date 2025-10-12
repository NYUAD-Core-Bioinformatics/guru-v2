from airflow.plugins_manager import AirflowPlugin
from airflow.www.app import csrf
from airflow.models import DagBag, DagRun
from airflow.utils.state import State
from airflow.utils import timezone
from flask_appbuilder import expose, BaseView as AppBuilderBaseView
from flask import Flask, Blueprint, render_template, request, flash, jsonify, send_file
from wtforms import Form, BooleanField
import os
import fnmatch
from datetime import datetime
import pandas as pd
import io
import re

from airflow.providers.ssh.operators.ssh import SSHOperator
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.providers.ssh.hooks.ssh import SSHHook

#Define the biosails yml. Change this path to custom installation.
YAML_FILES_DIR = "/opt/airflow/plugins/templates/yaml_files"

# Blueprints for the plugin
bp = Blueprint(
    "dnaseq_plugin",
    __name__,
    template_folder="templates",
)
samples_bp = Blueprint('samples', __name__)
workflow_bp = Blueprint("workflow_yaml_files", __name__)


@workflow_bp.route('/list_yaml_files', methods=['GET'])
def list_yaml_files():
    """List all YAML files in their respective folders (DNA, RNA, Others)."""
    
    categories = ["DNA", "RNA", "Others"]
    file_groups = {}

    for category in categories:
        category_path = os.path.join(YAML_FILES_DIR, category)

        # If the directory exists, list YAML files, otherwise return an empty list
        file_groups[category] = [
            file for file in os.listdir(category_path)
            if file.endswith(('.yml', '.yaml'))
        ] if os.path.isdir(category_path) else []

    return jsonify(file_groups)


@workflow_bp.route('/download_yaml', methods=['POST'])
@csrf.exempt
def download_yaml():
    """Allow users to download the selected YAML file."""
    try:
        data = request.get_json()
        filename = data.get('filename')

        if not filename:
            return jsonify(error="Filename is required"), 400

        # Locate the file in one of the category directories
        filepath = None
        for category in ["DNA", "RNA", "Others"]:
            path = os.path.join(YAML_FILES_DIR, category, filename)
            if os.path.exists(path):
                filepath = path
                break

        if not filepath:
            return jsonify(error="File not found"), 404
        return send_file(filepath, as_attachment=True)

    except Exception as e:
        return jsonify(error=str(e)), 500
    
@workflow_bp.route('/upload_yaml', methods=['POST'])
@csrf.exempt
def upload_yaml():
    """Upload YAML file to the remote base_path using SSHHook."""
    try:
        base_path = request.form.get('base_path')
        if not base_path:
            return jsonify(error="You need to choose a sample process before uploading."), 400

        if "file" not in request.files:
            return jsonify(error="No file part"), 400
        
        file = request.files["file"]
        if file.filename == "" or not file.filename.endswith(('.yaml', '.yml')):
            return jsonify(error="Invalid file. Only .yaml or .yml files are allowed."), 400

        ssh_hook = SSHHook(ssh_conn_id='guru_ssh')
        ssh_client = ssh_hook.get_conn()
        sftp = ssh_client.open_sftp()

        try:
            sftp.chdir(base_path)
        except IOError:
            return jsonify(error="Base path does not exist on the remote server."), 400

        remote_file_path = f"{base_path}/{file.filename}"
        with sftp.open(remote_file_path, 'wb') as remote_file:
            remote_file.write(file.read())

        sftp.close()
        ssh_client.close()

        return jsonify(message=f"Upload successful to path: {remote_file_path}"), 200
    except Exception as e:
        return jsonify(error=str(e)), 500
    

@workflow_bp.route('/select_yaml', methods=['POST'])
@csrf.exempt
def select_yaml():
    """Copy selected YAML file to the base_path on the remote server."""
    try:
        data = request.get_json()
        base_path, filename = data.get('base_path'), data.get('filename')

        if not base_path or not filename:
            return jsonify(error="Base path and filename are required."), 400

        # Locate the file in its category directory
        source_file_path = None
        for category in ["DNA", "RNA", "Others"]:
            path = os.path.join(YAML_FILES_DIR, category, filename)
            if os.path.exists(path):
                source_file_path = path
                break

        if not source_file_path:
            return jsonify(error="File not found."), 404

        # Establish SSH connection and transfer file
        ssh_hook = SSHHook(ssh_conn_id='guru_ssh')
        ssh_client = ssh_hook.get_conn()
        sftp = ssh_client.open_sftp()

        # Ensure base path exists on the remote server
        try:
            sftp.chdir(base_path)
        except IOError:
            return jsonify(error="Base path does not exist on the remote server."), 400

        # Copy file
        remote_file_path = os.path.join(base_path, filename)
        sftp.put(source_file_path, remote_file_path)

        # Close connections
        sftp.close()
        ssh_client.close()

        return jsonify(message=f"File copied to: {remote_file_path}"), 200

    except Exception as e:
        return jsonify(error=str(e)), 500
    

@samples_bp.route('/listdir', methods=['POST'])
@csrf.exempt
def listdir():
    data = request.get_json()
    user_input_path = data.get('base_path')

    # Normalize base_path to always include "Unaligned"
    user_input_path = os.path.normpath(user_input_path)
    base_path = (
        user_input_path.split("/Unaligned")[0] + "/Unaligned"
        if "/Unaligned" in user_input_path
        else os.path.join(user_input_path, "Unaligned")
    )

    ssh_client = SSHHook(ssh_conn_id='guru_ssh').get_conn()
    command = f"find {base_path} -type d -name 'processed' -exec find {{}} -type d -path '*/fastp' \\; | sed 's|/fastp||' | awk -F'/' '{{print $NF}}'"
    stdin, stdout, stderr = ssh_client.exec_command(command)
    file_list = stdout.read().decode().strip().split('\n')

    if not file_list or file_list == ['']:
        return jsonify(message="No valid folders found.", base_path=base_path), 200

    return jsonify(base_path=base_path, folder_names=file_list)


@samples_bp.route('/validate_base_path', methods=['POST'])
@csrf.exempt
def validate_base_path():
    data = request.get_json()
    base_path = data.get('base_path')

    if not base_path:
        return jsonify({"message": "Base path is required.", "status": "error"}), 400

    ssh_hook = SSHHook(ssh_conn_id='guru_ssh')
    ssh_client = ssh_hook.get_conn()

    stdin, stdout, stderr = ssh_client.exec_command(f"if [ -d '{base_path}' ]; then echo 'exists'; else echo 'not_found'; fi")
    result = stdout.read().decode().strip()
    if result == "exists":
        return jsonify({"message": "Base path is valid!", "status": "success"}), 200
    return jsonify({"message": "The specified path does not exist.", "status": "error"}), 200

@samples_bp.route('/upload_file', methods=['POST'])
@csrf.exempt
def upload_file():
    file = request.files.get('file')
    base_path = request.form.get('base_path', '').strip()

    if not base_path or not file:
        return jsonify({"message": "Base path and file are required.", "status": "error"}), 400

    if not file.filename.endswith(('.txt', '.csv')):
        return jsonify({"message": "Only .txt and .csv files are allowed.", "status": "error"}), 400

    try:
        ssh_client = SSHHook(ssh_conn_id='guru_ssh').get_conn()
        sftp = ssh_client.open_sftp()

        try:
            sftp.chdir(base_path)  
        except IOError:
            return jsonify({"message": "Base path does not exist on the remote server.", "status": "error"}), 400

        remote_file_path = f"{base_path}/{file.filename}"
        with sftp.open(remote_file_path, 'wb') as remote_file:
            remote_file.write(file.read())

        sftp.close()
        ssh_client.close()

        return jsonify({"message": "File uploaded successfully!", "status": "success", "file_path": remote_file_path}), 200
    except Exception as e:
        return jsonify({"message": f"Upload failed: {str(e)}", "status": "error"}), 500

@samples_bp.route('/parse_uploaded_file', methods=['POST'])
@csrf.exempt
def parse_uploaded_file():
    data = request.get_json()
    base_path = data.get('base_path', '').strip()
    file_name = data.get('file_name', '').strip()

    if not base_path or not file_name:
        return jsonify({"message": "Base path and file name are required.", "status": "error"}), 400

    try:
        ssh_client = SSHHook(ssh_conn_id='guru_ssh').get_conn()
        sftp = ssh_client.open_sftp()
        remote_file_path = f"{base_path}/{file_name}"

        with sftp.open(remote_file_path, 'r') as file:
            lines = file.readlines()

        sftp.close()
        ssh_client.close()

        if len(lines) < 2:
            return jsonify({"message": "File is empty or missing required data.", "status": "error"}), 400

        if file_name.endswith(".csv"):
            delimiter = ","
        elif file_name.endswith(".tsv"):
            delimiter = "\t"
        else:  
            delimiter = " "

        sample_names = [line.split(delimiter)[0].strip() for line in lines[1:]]

        return jsonify({"sample_names": sample_names, "status": "success"}), 200

    except Exception as e:
        return jsonify({"message": f"Error parsing file: {str(e)}", "status": "error"}), 500


@samples_bp.route('/validate_email', methods=['POST'])
@csrf.exempt
def validate_email():
    data = request.get_json()
    emails = data.get("email_address", "").strip()
    if not emails:
        return jsonify({"status": "error", "message": "Email is required."}), 400

    email_list = [e.strip() for e in emails.split(',')]
    regex = r'^\S+@\S+\.\S+$'
    invalid = [e for e in email_list if not re.match(regex, e)]
    if invalid:
        return jsonify({"status": "error", "message": f"Invalid email(s): {', '.join(invalid)}"}), 400
    return jsonify({"status": "success", "message": "Valid email address(es)."}), 200


class MyForm(Form):
    sample_group = BooleanField('Samples grouped in different folders.')

class DNAseqBaseView(AppBuilderBaseView):
    default_view = "dnaseqrun"

    @expose("/", methods=['GET', 'POST'])
    @csrf.exempt
    def dnaseqrun(self):
        form = MyForm(request.form)
        if request.method == 'POST' and form.validate():
            # Get selected items (folders or files) from the form
            selected_workflow = request.form.get("selected_workflow", "")
            selected_items = request.form.get("selected_items", "")
            base_path = request.form.get("base_path", "")
            email_address = request.form.get("email_address", "")
            print("Selected Items (comma-separated):", selected_workflow, base_path)

            # Trigger the DAG run
            now = datetime.now()
            dt_string = now.strftime("%d-%m-%Y %H:%M:%S")
            run_id = "downstream_" + dt_string

            dagbag = DagBag('dags')
            dag = dagbag.get_dag('dnaseq_dag')
            dag.create_dagrun(
                run_id=run_id,
                state=State.RUNNING,
                conf={
                    'selected_items': selected_items, 'base_path': base_path, 'selected_workflow': selected_workflow, 'email_address': email_address, 
                }
            )

            # Render the response template
            data = {'selected_items': selected_items, 'base_path': base_path, 'selected_workflow': selected_workflow, 'email_address': email_address}
            data['status_url'] = f"http://{os.environ['AIRFLOW_URL']}:{os.environ['AIRFLOW_PORT']}/dags/dnaseq_dag/graph"
            return self.render_template("dnaseq_response.html", data=data)
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    flash(f'{error}')
            return self.render_template("dnaseq.html", form=form)


# AppBuilder View and Plugin Registration
v_appbuilder_view = DNAseqBaseView()
v_appbuilder_package = {
    "name": "Downstream Analysis",
    "category": "",
    "view": v_appbuilder_view
}

if v_appbuilder_view.blueprint is None:
    v_appbuilder_view.blueprint = Blueprint("dnaseq_plugin", __name__)

v_appbuilder_view.blueprint.register_blueprint(samples_bp)
v_appbuilder_view.blueprint.register_blueprint(workflow_bp)


class AirflowPlugin(AirflowPlugin):
    name = "dnaseq_plugin"
    operators = []
    flask_blueprints = [bp, samples_bp, workflow_bp]
    hooks = []
    executors = []
    admin_views = []
    appbuilder_views = [v_appbuilder_package]
