# Brewpi Scripts
Useful scripts for automated setup of brewpi and tiltHydrometer

# Automated install of BrewPi and TiltHydrometer

NOTES:

1. Assume logged in as `pi` user and current working dir is `/home/pi`.
2. Tested on Raspberry Pi 3 running "Raspbian GNU/Linux 8 (jessie)", Spark
   Photon V2, and Tilt model LBM313-2540-256

## Install Raspbian image on SD card
1. Download Raspbian Jessie Lite (https://www.raspberrypi.org/downloads/raspbian/)
1. Copy image onto SD card
   * (Windows) Win32DiskImager (https://sourceforge.net/projects/win32diskimager/)

## Initialize OS
1. Login as `pi` (default password is `raspberry`)
1. `sudo raspi-config`
   * Change user password
   * Set hostname
   * Set timezone
   * Expand filesystem
   * Enable SSH (Optional: needed only if logging in remotely)
1. Reboot
   * `sudo reboot`
1. Update OS
   * ```sudo apt-get update && sudo apt-get -y dist-upgrade && sudo apt-get clean && sudo reboot```

## Brewpi Software Setup
1. ```sudo apt-get -y install git```
1. ```git clone https://github.com/andylytical/brewpi-scripts.git```
1. ```sudo brewpi-scripts/brewpi_install.sh```

## Tilt Hydrometer Setup
1. ```sudo brewpi-scripts/tilt_install.sh```
1. Edit calibration files GRAVITY.colour and TEMPERATURE.colour (as directed by
   the output of the script above).
1. In brewpi web interface, start a new brew.

# See also:
https://github.com/andylytical/brewpi-backup
