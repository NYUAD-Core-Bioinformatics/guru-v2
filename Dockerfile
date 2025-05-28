FROM apache/airflow:2.10.5
ENV TZ=Asia/Dubai
USER root
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
RUN echo "alias ll='ls -lah'" >> /home/airflow/.bashrc && \
    chown airflow: /home/airflow/.bashrc
USER airflow
WORKDIR /opt/airflow
