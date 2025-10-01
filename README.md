# Guru Downstream Analysis Instance ( Guru-v2)

## Overview

**Guru-v2** is a downstream analysis platform that can be deployed quickly using Docker. This guide will help you install and configure the instance locally or on a server.

This setup supports two processing modes ```Default``` and ```Custom``` both designed for submitting SLURM jobs using [BioSAILs](https://github.com/nizardrou/BioSAILs-WMS). 

With ```Default``` view, the working directory expects this ```/scratch/user1/dir1/UnAligned/data/processed``` directory structure. 

With ```Custom``` view, the working directory can be flexible.

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

Before starting the application, update connection parameters for SSH and email authentication. 
If the email account and ssh is not created, please refer below a and b section and update the details in the below scripts files.

Open ```scripts/ssh.sh``` and set ```--conn-host``` and ```--conn-login```.

Open ```scripts/email.sh``` and set ```--conn-login``` and ```--conn-password```.


###### a. Generate SSH Key Pair

Follow this [SSH key generation](https://www.ssh.com/academy/ssh/keygen) guide to create a key pair.

Copy the public key ```id_rsa.pub``` to your remote server.
```
$HOME/.ssh/id_rsa.pub
```

Move the private key ```id_rsa``` to the ```keys/``` directory:
```
cp ~/.ssh/id_rsa keys/id_rsa
chmod 644 keys/id_rsa
```

    Note (Windows users):
    Use a GUI tool like FileZilla or WinSCP to copy id_rsa.pub to the remote server, and place id_rsa in the keys/ folder locally.

    Note:
    If you're running Guru on a server or cloud, replace AIRFLOW_URL=localhost with your server's IP address in the .env file.

###### b. Generate Email Account

Enable 2-Step Verification by referring this [link](https://myaccount.google.com/security)

Then access below [page](https://myaccount.google.com/apppasswords) to create a app password. 
Note:- Remove the whitespace from the app password.



#### 5. Build the Application 

Start the Guru instance using the following scripts. Initialization may take ~5 minutes.

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

#### 6. Accessing the Application

To access the Guru User Interface, visit [***localhost:8080***](localhost:8080)
Use the credentials **guru**/**admin**.

> **Note:**  
> If you run this service on a server, replace `localhost` with the server's IP address or hostname in your browser.

Then navigate to ```Downstream Analysis``` button to begin with the analysis. 

#### 7. Running a Downstream Analysis

Guru classifies downstream analysis into two options:

##### 1) Default Section

Maintain the directory structure as:
```
UnAligned/data/processed
```
Place the QC/QT ```fastq``` files under the ```processed``` folder.

Example:
If you set the base path as:
```
/scratch/user1/nextseq/20922123
```

Then the ```fastq``` folders should be located as:
```
/scratch/user1/nextseq/20922123/UnAligned/data/processed/sample1/fastp
/scratch/user1/nextseq/20922123/UnAligned/data/processed/sample2/fastp
```

Once you set the base path and click List folders, you'll be able to select samples to proceed with the analysis.


##### 2. Custom Section

Place all fastq files directly under the base path (without any folder structure).

Example:
If you set the base path as:
```
/scratch/user1/nextseq/20922123
```

Then the ```fastq``` files should be directly inside that folder, such as:
```
/scratch/user1/nextseq/20922123/sampleS2_20252211_L001_fastp_read1.fastq.gz
/scratch/user1/nextseq/20922123/sampleS2_20252211_L001_fastp_read2.fastq.gz
```

You should also provide the sample metadata in ```.csv``` or ```.txt``` format.

Below is an example format. The file should list sample names along with their corresponding ```read1``` and ```read2``` file names:
```
Sample_name,read1,read2
sampleS2_20252211_L001,sampleS2_20252211_L001_fastp_read1.fastq.gz,sampleS2_20252211_L001_fastp_read2.fastq.gz
sampleS3_20252211_L001,sampleS3_20252211_L001_fastp_read1.fastq.gz,sampleS3_20252211_L001_fastp_read2.fastq.gz
```

Once uploaded, you’ll be able to select the samples and proceed with the analysis.


To delete the Guru instance completely from your computer:

``` bash 
sh prune.sh
```

#### To Modify the SSH Configuration:

1. Go to **Admin → Connections**
2. Click the **Edit** button next to `guru_ssh`
3. Update the necessary details
4. Click **Save**


### Contact

If you need to contact us for feedback, queries, or to raise an issue, you can do so using the issues page [Github issue](https://github.com/NYUAD-Core-Bioinformatics/guru-v2/issues).

### Citation

If you use GURU in your research or publications, please cite our [Github page](https://github.com/NYUAD-Core-Bioinformatics/guru-v2).

### Acknowledgements

This work was supported by Tamkeen under the NYU Abu Dhabi Research Institute Award to the NYUAD Center for Genomics and Systems Biology (ADHPG-CGSB). We would also like to acknowledge the High Performance Computing department at NYU Abu Dhabi for the computational resources and their continuous support.

### Other Useful Links

- [CGSB Webpage](https://cgsb.abudhabi.nyu.edu) : for news and updates
- [BioSAILs](https://www.biorxiv.org/content/biorxiv/early/2019/01/02/509455.full.pdf)
- [Airflow](https://airflow.apache.org/) 
- [Docker](https://www.docker.com/)