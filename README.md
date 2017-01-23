# Building a new brewpi from scratch

NOTE: Assume logged in as `pi` user and current working dir is `/home/pi`.

## Install Raspbian image on SD card
1. Download Raspbian Jessie Lite (https://www.raspberrypi.org/downloads/raspbian/)
1. Copy image onto SD card
   * (Windows) Win32DiskImager (https://sourceforge.net/projects/win32diskimager/)

## Initialize OS
1. Login as `pi` (default password is `raspberry`)
1. ```sudo raspi-config```
   * Expand Filesystem
   * Change user password
   * Set timezone (International / Localization)
   * Set hostname (Advanced options)
   * Enable ssh (Advanced options) (Optional: needed only if logging in remotely)
1. Reboot
1. Update OS
   * ```sudo apt-get update && sudo apt-get -y dist-upgrade && sudo apt-get clean && sudo reboot```

## Brewpi Software Setup
1. ```sudo apt-get -y install git```
1. ```git clone https://github.com/andylytical/brewpi-scripts.git```
1. ```sudo brewpi-scripts/brewpi_install.sh```

## Tilt Hydrometer Setup
1. ```sudo brewpi-scripts/tilt_install.sh```
