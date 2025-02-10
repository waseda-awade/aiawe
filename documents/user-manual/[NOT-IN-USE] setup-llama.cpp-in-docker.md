# Setup llama.cpp in docker

> NOT-IN-USE, the native llama.cpp is used instead

[Post](https://stackoverflow.com/a/77269071/1938012)


Configure the repository:

``` sh
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey |sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg \
&& curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list | sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list \
&& sudo apt-get update
```

Install the NVIDIA Container Toolkit packages:

``` sh
sudo apt-get install -y nvidia-container-toolkit
```

Configure the container runtime by using the nvidia-ctk command:

``` sh
sudo nvidia-ctk runtime configure --runtime=docker
```

Restart the Docker daemon:

``` sh
sudo systemctl restart docker
```


## Install cuda driver

[CUDA Driver](https://developer.nvidia.com/cuda-downloads?target_os=Linux&target_arch=x86_64&Distribution=Ubuntu&target_version=24.04&target_type=deb_network)


### CUDA Toolkit Installer

Installation Instructions:

``` sh
wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2404/x86_64/cuda-keyring_1.1-1_all.deb
sudo dpkg -i cuda-keyring_1.1-1_all.deb
sudo apt-get update
sudo apt-get -y install cuda-toolkit-12-8
```

Additional installation options are detailed here.

### Driver Installer

NVIDIA Driver Instructions (choose one option)
To install the open kernel module flavor:

``` sh
sudo apt-get install -y nvidia-open
```

``` txt
Your system has UEFI Secure Boot enabled.

UEFI Secure Boot requires additional configuration to work with third-party drivers.

The system will assist you in configuring UEFI Secure Boot. To permit the use of third-party drivers, a new Machine-Owner Key (MOK) has been generated. This key now needs to be enrolled in your system's firmware.

To ensure that this change is being made by you as an authorized user, and not by an attacker, you must choose a password now and then confirm the change after reboot using the same password, in both the "Enroll MOK" and "Change Secure Boot state" menus that will be presented to you when this system reboots.

If you proceed but do not confirm the password upon reboot, Ubuntu will still be able to boot on your system but any hardware that requires third-party drivers to work correctly may not be usable.
 ```

<!-- To install the legacy kernel module flavor:

``` sh
sudo apt-get install -y cuda-drivers
``` -->
