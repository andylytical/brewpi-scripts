Automated install of brewpi and docker on Raspberry Pi.

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

1. Reduce gpu memory (optional)
   ```bash
   grep -q gpu_mem /boot/config.txt || sudo sed -ie '$agpu_mem=16' /boot/config.txt
   ```

1. Setup Networking
   1. Get the mac from the pi
      * Ethernet: `cat /sys/class/net/eth0/address`
      * Wireless: `cat /sys/class/net/wlan0/address`
   1. Use the mac to assign a static ip (on your router). \
      See your router documentation on how to do this.
   1. Wifi setup only: \
      Configure wifi on the pi
      * `sudo raspi-config`
      * Browse through options to find wifi setup

1. Updates
   ```bash
   PACKAGES=( git )
   sudo apt update && apt -y install "${PACKAGES[@]}" && apt -y full-upgrade && reboot
   ```

## Docker
1. `git clone https://github.com/andylytical/brewpi-scripts.git`
1. `ln -s /home/pi/brewpi-scripts/brewpi.sh ~/brewpi`
1. `/home/pi/brewpi-scripts/docker_install.sh`
1. `docker pull brewpi/brewpi-raspbian`


## Setup Wifi Access To Spark
OPTIONAL - Skip this step if using spark via USB

### Setup wifi on the spark
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
1. `~/brewpi mkdatadir`
1. `~/brewpi enable-wifi <SPARK_IP_ADDRESS>` \
    Replace the string _<SPARK_IP_ADDRESS>_ with the ip address you assigned
    to the Spark.

