# Guru Downstream Analysis Instance ( Guru-v2)

## Overview

**Guru-v2** is a downstream analysis platform that can be deployed quickly using Docker. This guide will help you install and configure the instance locally or on a server.

This setup comes with ```Default``` and ```Custom``` based views for processing and submitting slurm jobs using Biosails. 

With ```Default``` view, the working directory expects this ```/scratch/<net-id>/Some-dir/UnAligned/data/processed``` directory structure. 

With ```Custom``` it can be anywhere on your working directory. This is still inprogress. 

---

## Installation

The easiest way to get started is by using [Docker](https://www.docker.com/).

### 1. Prerequisites

- [Install Docker (version 28.0.0+)](https://www.docker.com/get-started)
- [Install gitbash](https://git-scm.com/downloads) for Windows users

### 2. Launch Docker application 

Launch and start the docker service on your laptop or server. 

### 3. Clone the Repository

Launch terminal for Linux/OSX and open gitbash application for windows.

```bash
git clone https://github.com/NYUAD-Core-Bioinformatics/guru-v2
cd guru-v2
```

#### 4. Setting up the environment

Before starting the application, update connection parameters for SSH and email authentication:
Note:- Email credentials will be sharing privately by guru admins due to security reasons. 

Open ```scripts/ssh.sh``` and set ```--conn-host``` and ```--conn-login```.

Open ```scripts/email.sh``` and set ```--conn-login``` and ```--conn-password```.

#### 5. Generate SSH Key Pair

Follow this [SSH key generation](https://www.ssh.com/academy/ssh/keygen) guide to create a key pair.

Copy the public key (id_rsa.pub) to your remote server (path: $HOME/.ssh/id_rsa.pub), and place the private key (id_rsa) in the keys directory.
Note:- For windows users, copy the ```id_rsa.pub``` to remote server (path: $HOME/.ssh/id_rsa.pub) using ```filezilla/winscp``` GUI application. Then place ```id_rsa``` to ```keys``` folder.

```
cp ~/.ssh/id_rsa keys/id_rsa
chmod 644 keys/id_rsa
```

Note: If you run guru on server or cloud. Replace ```AIRFLOW_URL=localhost``` to IP address from ```.env``` file.
 
#### 6. Building the Application 

Run the following script to start the Guru instance (initialization may take ~5 minutes):

For Linux/MacOSX:

``` bash
sh build.sh
```

For Windows:

``` bash
docker compose up --build -d
sh scripts/email.sh
sh scripts/ssh.sh
sh scripts/user.sh
sh scripts/email.sh
docker compose restart
```

#### 7. Accessing the Application

To access the Guru User Interface [***localhost:8080***](localhost:8080)
and use the credentials **guru**/**admin**.

Note:- 
- If you run this service on a server, replace the localhost with IP-address or hostname on the browser. 

Then navigate to ```Downstream Analysis``` button to begin with the analysis. 

Guru classified the downstream analysis into two selections.

1) Default Section

Maintain the directory structure as ```UnAligned/data/processed``` in the base path and put the QC/QT fastq under processed folder.
For eg:- if you set the base path as ```/scratch/user1/nextseq/20922123``` then the followed fastq folders present after this base path followed by ```/scratch/user1/nextseq/20922123/UnAligned/data/processed/sample1/fastp```, ```/scratch/user1/nextseq/20922123/UnAligned/data/processed/sample2/fastp` etc..

2. Custom Section

Place all the fastq files in the base path excluding the folder structure. 
For eg:- if you set the base path as ```/scratch/user1/nextseq/20922123``` then the fastq files present just inside the basepath by ```/scratch/user1/nextseq/20922123/sampleS2_20252211_L001_fastp_read1.fastq```,```/scratch/user1/nextseq/20922123/sampleS2_20252211_L001_fastp_read2.fastq``` etc.

Then you should provide us the sample metadata in ```.csv``` or ```.txt``` file format.

Below is an example and we expect the sample names with read1 and read2 in the below format

```
Sample_name,read1,read2
sampleS2_20252211_L001,sampleS2_20252211_L001_fastp_read1.fastq.gz,sampleS2_20252211_L001_fastp_read2.fastq.gz
sampleS3_20252211_L001,sampleS3_20252211_L001_fastp_read1.fastq.gz,sampleS3_20252211_L001_fastp_read2.fastq.gz
```



To delete the guru instance completely from your computer. 

``` bash 
sh prune.sh
```

Note:- To modify ssh configuration, then select Admin -> Connections.
Click on edit button beside ```guru_ssh```. Then update the information and Click save. 
