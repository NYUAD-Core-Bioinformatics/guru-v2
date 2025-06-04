FROM apache/airflow:2.11.0
ENV TZ=Asia/Dubai
USER root
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
RUN echo "alias ll='ls -lah'" >> /home/airflow/.bashrc && \
    chown -R airflow: /home/airflow
USER airflow
COPY img/navbar.html /home/airflow/.local/lib/python3.12/site-packages/airflow/www/templates/appbuilder/navbar.html
COPY img/mylogo.png /home/airflow/.local/lib/python3.12/site-packages/airflow/www/static/mylogo.png
COPY img/favicon.ico /home/airflow/.local/lib/python3.12/site-packages/airflow/www/static/pin_32.png
RUN sed -i 's|flask_app.config\["APP_NAME"\] = instance_name|flask_app.config["APP_NAME"] = "GURU"|' /home/airflow/.local/lib/python3.12/site-packages/airflow/www/app.py
WORKDIR /opt/airflow
