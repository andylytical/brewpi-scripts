# brewpi-scripts
Useful scripts for setting up brewpi and tiltHydrometer

# Building a new brewpi from scratch
## Install Raspbian image on SD card
1. Download Raspbian Jessie Lite (https://www.raspberrypi.org/downloads/raspbian/)
1. Copy image onto SD card
   * (Windows) Win32DiskImager

## Initialize OS
1. Expand SD
1. sudo raspi-config
   * Set timezone (International / Localization)
   * Change hostname
   * Change password
   * Enable ssh (Advanced options)
1. Update OS
   * sudo aptitude update && sudo aptitude -y full-upgrade && sudo aptitude clean

## Brewpi Software Setup
1. sudo aptitude -y install git
1. git clone https://github.com/andylytical/brewpi-scripts.git
1. sudo brewpi-scripts/brewpi_install.sh

## Tilt Hydrometer Setup
1. sudo brewpi-scripts/tilt_install.sh
