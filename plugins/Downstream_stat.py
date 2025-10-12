from airflow.plugins_manager import AirflowPlugin
from airflow.www.app import csrf
from airflow.models import DagBag, DagRun
from airflow.utils.state import State
from airflow.utils import timezone
from flask_appbuilder import expose, BaseView as AppBuilderBaseView
from flask import Flask, Blueprint, render_template, request, flash, jsonify, send_file
from wtforms import Form, StringField
import os
from datetime import datetime
import pandas as pd
from wtforms.validators import ValidationError, InputRequired, EqualTo

from airflow.providers.ssh.operators.ssh import SSHOperator
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.providers.ssh.hooks.ssh import SSHHook


# Blueprints for the plugin
bp = Blueprint(
    "down_stat",
    __name__,
    template_folder="templates",
)

"""Function to check if the work directory given is exist or not."""
def file_validate(form, field):
    # Get the path and assign to a list
    ssh_hook = SSHHook(ssh_conn_id='guru_ssh')
    ssh_client = ssh_hook.get_conn()
    sftp = ssh_client.open_sftp()
    dir = field.data
    try:
        files = sftp.listdir(dir)
    except FileNotFoundError as e:
        raise ValidationError(f'Directory path {dir} does not exist on the remote server')
    sftp.close()


class MyForm(Form):
    status_dir = StringField('Status Run Directory',[InputRequired(),file_validate], render_kw={"placeholder": "Specify the Complete Downstream status path - **/**/logs/000_hpcrunner_logs/stats received in the email."  })

class DownseqStatView(AppBuilderBaseView):
    default_view = "down_stat_run"

    @expose("/", methods=['GET', 'POST'])
    @csrf.exempt
    def down_stat_run(self):
        form = MyForm(request.form)
        if request.method == 'POST' and form.validate():
            # Trigger the DAG run
            now = datetime.now()
            dt_string = now.strftime("%d-%m-%Y %H:%M:%S")
            run_id = "downstream_" + dt_string
            status_dir = form.status_dir.data.strip()
            dagbag = DagBag('dags')
            dag = dagbag.get_dag('downstat_dag')
            dag.create_dagrun(
                run_id=run_id,
                state=State.RUNNING,
                conf={
                    'status_dir': status_dir, 
                }
            )
            # Render the response template
            data = {'status_dir': status_dir}
            data['status_url'] = f"http://{os.environ['AIRFLOW_URL']}:{os.environ['AIRFLOW_PORT']}/dags/downstat_dag/graph"
            return self.render_template("down_stat_response.html", data=data)
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    flash(f'{error}')
            return self.render_template("down_stat.html", form=form)


# AppBuilder View and Plugin Registration
v_appbuilder_view = DownseqStatView()
v_appbuilder_package = {
    "name": "Downstream Status Run",
    "category": "",
    "view": v_appbuilder_view
}

if v_appbuilder_view.blueprint is None:
    v_appbuilder_view.blueprint = Blueprint("down_stat", __name__)


class AirflowPlugin(AirflowPlugin):
    name = "down_stat"
    operators = []
    flask_blueprints = [bp]
    hooks = []
    executors = []
    admin_views = []
    appbuilder_views = [v_appbuilder_package]
