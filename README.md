<!--
Copyright © 2023 Intel Corporation

SPDX-License-Identifier: Apache License 2.0
-->

[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/sigopt/sigopt-server/main.svg)](https://results.pre-commit.ci/latest/github/sigopt/sigopt-server/main)

Sigopt-Server is an open-source tool for managing adaptive experiments, especially for hyperparameter optimization. It uses algorithms to determine the best spots in parameter space for metric optimization, and includes web visualizations so you can improve your models. For more information you can [read about our service offering](https://sigopt.com/). Our documentation is [here](https://docs.sigopt.com/)

# Installation

All you need to get started with SigOpt Server is Docker, Docker Compose and Git. We recommend that you get the latest version of each, and you will need at least Docker version 1.6.0 and Docker Compose version 2.6.1. Instructions are provided below for installing SigOpt Server on Debian, Ubuntu and OSX.

<details>
<summary>Installation (Debian and Ubuntu)</summary>

From a default ubuntu install. We have tested this on Ubuntu 22.04 Jammy from a clean AWS image. If you are an another variant of Linux you can proceed at your own risk, adapting as you go.

## Install Git and Docker

First, install git.

```bash
sudo apt-get install git
```

## Get the Code

Checkout the repository:

```bash
git clone https://github.com/sigopt/sigopt-server.git
cd sigopt-server
```

## Install some necessary packages

Add the repo for the Debian release we base our docker images on. Then you need to install the docker engine. We have provided a convenience script, "./scripts/compile/install_docker_debian.sh" but it makes fairly large changes to your base operating system. If you feel capable of managing that yourself, we recommend you do it for yourself [at the Docker website.](https://docs.docker.com/engine/install/ubuntu/) Finally, add the current user to the docker group, so your user can connect to the Docker daemon.

```bash
./scripts/compile/install_docker_debian.sh
sudo groupadd docker
sudo usermod -aG docker "$(id -u -n)"
```

You will need to log out or exit your current session for these changes to take effect.

</details>

<details>
<summary>Installation (Mac OSX)</summary>

The expected development platform is a Mac running the latest OSX. This has been tested on OS X Ventura and Monterey, if you are on an older OS X you can proceed at your own risk or upgrade.

## Install Docker

This has been tested with Docker for Mac 4.1.0. You can use other versions but proceed at your own risk. You can download and install this version of Docker [here](https://docs.docker.com/desktop/release-notes/#401).

### Docker Configuration

After installing and starting Docker, you should configure some settings.
This can be done from the system tray icon (top right) by selecting `Preferences...`.

#### Configure resources

From the Docker system tray icon, select `Preferences...`, then navigate to the `Resources` tab.
Select 4CPU and 4GB memory.
Apply and restart.

<details>
<summary> Resource Usage Warning (Mac) </summary>

##### CPU

Sometimes Docker appears to use a large amout of CPU while apparently being idle.
Make sure there really is nothing running with `docker ps`.
If there is indeed nothing running, try reducing the number of CPUs allocated to Docker.
This will require a restart of Docker.

</details>
</details>

# Setup for Running Experiments

If you don't wish to do any development on SigOpt, and just want to run experiments using the full capabilities of the SigOpt system, we have an automated configuration script for you to run one time. In order to provide secure connections it will create new, locally generated TLS certificates, and you will need to add them to your trust stores to be able to interact with SigOpt, either through the client in your code or to view the results of your experiments on the web. If you already have TLS certificates- and if you aren't sure you probably don't- you can place them as `tls.crt` and `tls.key` in the `artifacts/tls` directory of the sigopt-server install and they should work just fine (presuming they are in PEM encoded format). If you are using self-signed certificates, you will need to add the `root-ca.crt` into your keychain or you will get a lot of errors about unsafe and insecure connections.

From the terminal in the `sigopt-server` directory you created in the git clone command above, type:

```bash
./setup.sh
```

When the command has finished, make a note of the default log in information. You will need this to sign in later.

On AWS clean installs, you might need to restart the instance after adding yourself to the `docker` group.

This should set-up everything you need to just run SigOpt. You will need to add the file `root-ca.crt` generated in the `artifacts/tls` directory into your keychain if you are using the self-signed certificates, and then run

```bash
echo "127.0.0.1 sigopt.ninja" | sudo tee -a /etc/hosts
```

This will make sure that the self-signed certificates match the URL you are using. In order to protect you as much as possible with this self-signed cert, we have deleted the original key file associated with that certificate after we created a child certificate, so no attacker could cause mischief on your machine with it. If you are using other certificates you can just delete the `root-ca.crt` file and replace the `tls.crt` and `tls.key` files with your own certificates and you should be good to go.

Note that the creation script for both certs will pause in `vi` to let you edit who owns the certs, if you wish to change the defaults you can. You can change your editor by setting the `EDITOR` environment variable, ex. `export EDITOR=nano`. If you are stuck in `vi` and/or just want to accept the defaults you can press `<escape>:wq` and it will advance. You should need to do this twice, the first time for the root certificate and the second time for the leaf certificate.

Once successfully configured, you can run the SigOpt system- allowing you to run experiments and view their results on a local website, by calling

```bash
./start.sh
```

from the same sigopt-server directory you ran the configuration script from. Ctrl-c will allow you to quit.

## Everything is running

The website is now [running](https://sigopt.ninja:4443/)! Sign in with the credentials from the `./setup.sh` step.

With an [API Token](https://sigopt.ninja:4443/tokens/info) for your account you can use the [client](https://github.com/sigopt/sigopt-python) and conduct experiments with the SigOpt system and view the results on the [website](https://sigopt.ninja:4443/).

## Hooray, you've set up SigOpt for use!

If you reboot your machine, you should make sure that Docker is running (either Docker desktop or the daemon), then retype

```bash
./start.sh
```

From the sigopt-server directory and it will launch again. To stop running, a single `ctrl-c` from within the terminal window running the Sigopt Server will end it.

# Contributing your own code

If you are interested in contributing to the development of SigOpt Server, we have instructions for setting up the code for local development [here](./DEVELOPMENT.md). We love getting pull requests!
