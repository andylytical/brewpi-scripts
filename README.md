# Brewpi Scripts
There are two parts to this repository:
1. Automated install of BrewPi code and TiltHydrometer additions.
1. Backup of brewlog data & offline-brewlog graph viewing


----
# Part 1 - Automated install of BrewPi and TiltHydrometer

Note 1: Assume logged in as `pi` user and current working dir is `/home/pi`.

Note 2: Tested on Raspberry Pi 3 running "Raspbian GNU/Linux 8 (jessie)", Spark
Photon V2, and Tilt model LBM313-2540-256

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
1. Edit calibration files GRAVITY.colour and TEMPERATURE.colour (as directed by
   the output of the script above).
1. In brewpi web interface, start a new brew.

----

# Part 2 - Backup brewlog data and create static HTML for viewing brewlog graph offline (from Dropbox)
NOTES:
1. Assume logged in as user `pi` with default home at `/home/pi` and default brewpi web dir at `/var/www/html`

## Dependencies
* https://github.com/andreafabrizi/Dropbox-Uploader
* Dropbox account
  * A free account provides 2GB of space.  A single brew (about 1 month of data) uses approximately 20MB of space, which allows for up to 100 brews before some data would have to be *archived* to a different location.

## Installation
1. Install Dropbox-Uploader
   1. Follow instructions at https://github.com/andreafabrizi/Dropbox-Uploader to **clone** the repo and configure access to Dropbox.
1. Install local copies of updated Dygraphs libraries
   1. `/home/pi/brewpi-scripts/backup/install.sh`
1. Create new cron job to run every 4 hours to generate new offline graphs and backup new data to Dropbox
   1. `crontab -e`
   ```
   01 */4 * * * python3 /home/pi/brewpi-scripts/backup/mk_brewlog_graphs.py
   12 */4 * * * python3 /home/pi/brewpi-scripts/backup/backup_brewlogs.py
   ```
## Verify installation
### Manually generate static HTML pages with brewlog graphs
1. `python3 /home/pi/brewpi-scripts/backup/mk_brewlog_graphs.py`
### Force live backup of brewlog data
1. `python3 /home/pi/brewpi-scripts/backup/backup_brewlogs.py`
### Verify brewlog backup graphs
1. On your local computer, browse to dropbox sync folder
1. Go to the folder you created in the first step of Installation above (ie: *configure access to Dropbox*)
1. Double-click an HTML file from the current or a previous brewlog


