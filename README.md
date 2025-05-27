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

---

### 2. Clone the Repository

```bash
git clone https://github.com/NYUAD-Core-Bioinformatics/guru-v2
cd guru-v2
```

#### Setting up the environment

Before starting the application, update connection parameters for SSH and email authentication:

Open ```scripts/ssh.sh``` and set ```--conn-host``` and ```--conn-login```.

Open ```scripts/email.sh``` and set ```--conn-login``` and ```--conn-password```.

#### Generate SSH Key Pair

Follow this SSH key generation guide to create a key pair.

Copy the public key (id_rsa.pub) to your remote server, and place the private key (id_rsa) in the keys directory.

```
ssh-copy-id username@servername
cp ~/.ssh/id_rsa keys/id_rsa
chmod 600 keys/id_rsa
```

Note: You can set the IP address for the Guru instance by editing the .env file.
 
#### Building the Application 

Run the following script to start the Guru instance (initialization may take ~5 minutes):

``` bash
sh build.sh
```

#### Accessing the Application

To access the Guru User Interface [localhost:8080](localhost:8080)
and use the credentials **guru**/**admin**.

Then navigate to ```Downstream Analysis``` button to start the analysis. 

Note:- 
- If you run this service on a server, replace the localhost with IP-address or hostname on the browser. 


To delete the guru instance completely from your computer. 

``` bash 
sh prune.sh
```

Note:- To modify ssh configuration, then select Admin -> Connections.
Click on edit button beside ```guru_ssh```. Then update the information and Click save. 