# rna_editing_pipeline

This project requires a singularity image built from a Docker container. 

To install [Docker](https://docs.docker.com/engine/installation/linux/ubuntulinux/): 


```bash
sudo apt-get update
sudo apt-get install apt-transport-https ca-certificates
sudo apt-key adv --keyserver hkp://p80.pool.sks-keyservers.net:80 --recv-keys 58118E89F3A912897C070ADBF76221572C52609D
```

On ubuntu 14.04: 

```bash
deb https://apt.dockerproject.org/repo ubuntu-trusty main

sudo apt-get update
sudo apt-get purge lxc-docker
apt-cache policy docker-engine
sudo apt-get install docker-engine
```
 
To install [Singularity](http://singularity.lbl.gov/): 


```bash
sudo apt-get install singularity
```

To create a Docker image:
```bash
docker build -t rnae-ubuntu-image .
docker create --name rnae-ubuntu-label rnae-ubuntu-image
```

To build and import the docker container into a singularity image: 

1. Do some weird thing

```bash
mkdir -p /usr/local/var/singularity/mnt
```

2. Create and export Docker into Singularity image

```bash
sudo singularity create -s 1500 rnae-ubuntu.img
docker export rnae-ubuntu-label | sudo singularity import rnae-ubuntu.img
```

Finally, create and edit the /singularity executable (and make sure to make it executable):

```bash
#!/bin/bash

export PATH="/opt/conda/bin:/usr/bin:$PATH"

"$@"
```

```bash
chmod +x /singularity
```
