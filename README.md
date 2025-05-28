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
chmod 600 keys/id_rsa
```

Note: You can set the IP address for the Guru instance by editing the .env file.
 
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

Then navigate to ```Downstream Analysis``` button to start the analysis. 

In the Default section, you need to maintain the directory structure as ```UnAligned/data/processed``` and put the QC/QT under processed folder.

Note:- 
- If you run this service on a server, replace the localhost with IP-address or hostname on the browser. 


To delete the guru instance completely from your computer. 

``` bash 
sh prune.sh
```

Note:- To modify ssh configuration, then select Admin -> Connections.
Click on edit button beside ```guru_ssh```. Then update the information and Click save. 