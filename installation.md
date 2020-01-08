# Installation

This document aims to explain how to setup the cctv project in Ubuntu Server (v. 18.04 Bionic Beaver).

The installation comprises three main parts: 
* The installation of tensorflow-gpu
* the installation of tensorflow object detection API
* the creation of a cron task.

## installation of tensorflow-gpu
Tensorflow supports CUDA 10.0. A more recent version of CUDA may not be supported.

### Removing CUDA Toolkit and Driver (if CUDA > 10.0)

This step may not be neccessary if one can install cuda 10.0 alongside more recent versions of cuda and make .bashrc file point to it. However to strictly follow tensorflow installation instructions it maybe better to previously uninstall cuda.

''' bash
# To remove CUDA Toolkit: 
sudo apt-get --purge remove "*cublas*" "cuda*"
# To remove NVIDIA Drivers: 
sudo apt-get --purge remove "*nvidia*"
sudo apt autoremove
'''

Check usr/local/. Shouldn’t exist any cuda files or directories.

source: https://docs.nvidia.com/cuda/cuda-installation-guide-linux/index.html#removing-cuda-tk-and-driver

### Install cuda and nvidia drivers according  to tensorflow instructions

**Requires Python > 3.4 and pip >= 19.0**

'''
sudo apt update
sudo apt install python3-dev python3-pip
'''
source: https://www.tensorflow.org/install/pip

Add NVIDIA package repositories (https://www.tensorflow.org/install/gpu)

Reboot the machine and check that  cuda is installled with  “nvidia-smi”.

**Note**: Dont’t install “virtualenv” but work with installed “venv”: https://realpython.com/python-virtual-environments-a-primer/

Finally:
'''
pip3 install virtualenvwrapper
'''

