# Use the official ubuntu
FROM ubuntu:latest

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV AIRFLOW_HOME=/opt/airflow
ENV PATH=/opt/airflow/.local/bin:$PATH

# Install system dependencies
RUN apt-get update
RUN apt-get install software-properties-common -y
RUN add-apt-repository ppa:deadsnakes/ppa -y

RUN apt-get update && apt-get install -y \
    build-essential \
    default-libmysqlclient-dev \ 
    git \
    curl \
    wget \
    vim \
    netcat \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Install Python 3.8
RUN apt update && apt install -y python3.8 python3.8-distutils python3.8-dev
RUN curl -sS https://bootstrap.pypa.io/get-pip.py | python3.8
RUN ln -s /usr/bin/python3.8 /usr/bin/python

# Include configuration and necessary files into image
RUN mkdir -p $AIRFLOW_HOME
COPY requirements.txt /opt/airflow/
COPY dags /opt/airflow/dags
COPY airflow.cfg /opt/airflow/airflow.cfg

# Install Apache Airflow and other python packages from requirements
RUN pip install -r /opt/airflow/requirements.txt

# Set up a non-root user
RUN useradd -ms /bin/bash airflow --uid 50000

# Create the AIRFLOW_HOME directory and set ownership
RUN chown -R airflow: $AIRFLOW_HOME

# Remove unnecessary packages from image(which has high level vulnerability)
RUN apt-get remove --auto-remove linux-libc-dev -y 

# Switch to the non-root user
USER airflow

# Set the working directory
WORKDIR /opt/airflow/
COPY entrypoint.sh entrypoint.sh

# Expose the necessary ports
EXPOSE 8080 5555 8793

ENTRYPOINT ["./entrypoint.sh"]
