Borrowed heavily from
https://blog.alexellis.io/getting-started-with-docker-on-raspberry-pi/

# Setup RPi
## Setup OS
1. Install Raspbian Stretch \
   https://www.raspberrypi.org/downloads/

1. Reduce gpu memory
   ```bash
   grep gpu_mem /boot/config.txt || echo "gpu_mem=16" >> /boot/config.txt
   ```

1. Updates
   ```bash
   sudo su -
   PACKAGES=( git )
   apt update && apt -y install "${PACKAGES[@]}" && apt -y full-upgrade && reboot
   ```

## Setup docker
1. Install docker
   ```bash
   curl -sSL https://get.docker.com | sh
   ```

1.  Add pi user to docker group
   ```bash
   sudo usermod -aG docker pi
   ```

1. Enable docker at startup
   ```bash
   systemctl enable docker
   ```

1. Start docker
   ```bash
   systemctl start docker
   ```

1. Get latest brewpi docker image
   ```bash
   docker pull brewpi/brewpi-raspbian
   ```

# Start up initial brewpi docker container
```bash
docker run --rm -it \
--name brewpi \
-p 80:80 \
-v ~/brewpi-data:/data \
-v /etc/timezone:/etc/timezone \
-v /etc/localtime:/etc/localtime \
brewpi/brewpi-raspbian bash
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



# Setup wifi on the Brewpi Spark
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
   Type: `m`

1. Setup wifi \
   Type: `w`
