Automated install of brewpi and docker on Raspberry Pi.

----
Note: The latest version does not have tilt support (yet).
For Tilt Hydrometer support, see [release v0.1](670ded92d556e19fda82ce0d76bd9391b5587a70)

Note: [release v0.1](670ded92d556e19fda82ce0d76bd9391b5587a70) was tested on v0.4.4 of Brewpi code. It might work if applied to the v0.5.5 brewpi code *inside* the container, but that has not been tried or tested here.

----

# Installation
See: [One Time Setup](#one-time-setup)

# Usage
* Docker container management
  ```bash
  ~/brewpi start
  ~/brewpi stop
  ~/brewpi status
  ~/brewpi restart #stop, then start the container
  ```

* Check for brewpi docker updates
  ```bash
  ~/brewpi check-update
  ```

* Update brewpi docker image
  ```bash
  ~/brewpi update
  ```

* Clean up old (stopped) brewpi container
  ```bash
  ~/brewpi stop
  ~/brewpi clean
  ```

# One Time Setup

## OS
1. Install Raspbian Stretch \
   https://www.raspberrypi.org/downloads/

1. Configure OS basics
   1. `sudo raspi-config`
      * Change user password
      * Network - Set Hostname
      * Network - Setup Wi-Fi
      * Localization - Set timezone
      * Localization - Set wifi country
      * Interfacing Options - Enable SSH
      * Finish
      * Reboot

1. Setup Networking
   1. Get the mac from the pi
      * Ethernet: `cat /sys/class/net/eth0/address`
      * Wireless: `cat /sys/class/net/wlan0/address`
   1. Use the mac to assign a static ip (on your router). \
      See your router documentation on how to do this.

## Install brewpi-scripts
1. `sudo apt -y install git`
1. `git clone https://github.com/andylytical/brewpi-scripts.git`
1. `cd brewpi-scripts; git checkout topic/aloftus/update_for_stretch_n_docker; cd`
1. `ln -s /home/pi/brewpi-scripts/brewpi.sh ~/brewpi`

## Finish OS setup
1. `~/brewpi-scripts/os_setup.sh`

## Docker setup
1. `~/brewpi-scripts/docker_setup.sh`
1. `logout`
1. Login again as user __pi__
1. `~/brewpi update`

## Setup Wifi Access To Spark
OPTIONAL - Skip this step if using spark via USB

### Configure wifi on the spark
Note: These instructions were tested on a Spark version 3. \
TODO: Test on Spark v2

1. Connect Spark via USB

1. Put the particle in setup mode \
   Hold the setup button for 5 seconds until the LED is flashing blue to put the Photon in listening mode

1. Install screen
   ```bash
   apt -y install screen
   ```

1. Connect to particle
   ```bash
   screen /dev/ttyACM0
   ```

1. Get MAC address \
   Type: `m` \
   Use the mac to assign a static ip (on your router)

1. Setup wifi \
   Type: `w` \
   Enter information as prompted for SSID and password

1. Exit screen \
   Type: `Ctl-a` then `k`
   Answer _yes_ at prompt to kill screen session.

See also: https://docs.particle.io/guide/tools-and-features/cli/photon/

### Enable wifi access to spark
1. `~/brewpi enable-wifi <SPARK_IP_ADDRESS>` \
    Replace the string _<SPARK_IP_ADDRESS>_ with the ip address you assigned
    to the Spark.
1. `~/brewpi restart`

