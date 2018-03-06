Borrowed heavily from
https://blog.alexellis.io/getting-started-with-docker-on-raspberry-pi/

# One Time Setup
## OS
1. Install Raspbian Stretch \
   https://www.raspberrypi.org/downloads/

1. Reduce gpu memory (optional)
   ```bash
   grep gpu_mem /boot/config.txt || echo "gpu_mem=16" >> /boot/config.txt
   ```

1. Updates
   ```bash
   sudo su -
   PACKAGES=( git )
   apt update && apt -y install "${PACKAGES[@]}" && apt -y full-upgrade && reboot
   ```

## Docker
1. `git clone https://github.com/andylytical/brewpi-scripts.git`
1. `cd brewpi-scripts`
1. `git submodule update --init`
1. `./docker_install.sh`
1. `docker pull brewpi/brewpi-raspbian`


## Setup Wifi Access To Spark
OPTIONAL - Skip this step if using spark via USB

#### Setup wifi on ths spark
See also:
* https://docs.particle.io/guide/tools-and-features/cli/photon/

1. Install screen
   ```bash
   apt -y install screen
   ```

1. Put the particle in setup mode \
   Hold the setup button for 5 seconds until the LED is flashing blue to put the Photon in listening mode

1. Connect to particle
   ```bash
   screen /dev/ttyACM0
   ```

1. Get MAC address \
   Type: `m` \
   If necessary, add this mac to your wifi router mac filter to allow access

1. Setup wifi \
   Type: `w` \
   Enter information as prompted for SSID and password


#### Configure brewpi to spark access
1. Start docker container to create `~/brewpi-data`, then exit immediately
   ```bash
   /home/pi/brewpi-scripts/dbp mkdata
   ```
```bash
docker run --rm -it \
--name brewpi \
-p 80:80 \
-v ~/brewpi-data:/data \
-v /etc/timezone:/etc/timezone \
-v /etc/localtime:/etc/localtime \
brewpi/brewpi-raspbian sleep 2
```

# Start up brewpi docker container
```bash
docker run -d \
--name brewpi \
-p 80:80 \
-v ~/brewpi-data:/data \
-v /etc/timezone:/etc/timezone \
-v /etc/localtime:/etc/localtime \
--restart always \
brewpi/brewpi-raspbian
```


