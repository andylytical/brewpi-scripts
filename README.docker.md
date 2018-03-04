Borrowed heavily from
https://blog.alexellis.io/getting-started-with-docker-on-raspberry-pi/

# Setup OS
## Install Raspbian Stretch
https://www.raspberrypi.org/downloads/

## Reduce gpu memory
```
grep gpu_mem /boot/config.txt || echo "gpu_mem=16" >> /boot/config.txt
```

## Updates
```
sudo su -
PACKAGES=( git )
apt update && apt -y install "${PACKAGES[@]}" && apt -y full-upgrade && reboot
```


# Setup docker
## Install docker
```
curl -sSL https://get.docker.com | sh
```

## Add pi user to docker group
```
sudo usermod -aG docker pi
```

## Enable docker at startup
```
systemctl enable docker
```

## Start docker
```
systemctl start docker
```

## Get latest brewpi docker image
```
docker pull brewpi/brewpi-raspbian
```

# Start up initial brewpi docker container
docker run --rm -it \
--name brewpi \
-p 80:80 \
-v ~/brewpi-data:/data \
-v /etc/timezone:/etc/timezone \
-v /etc/localtime:/etc/localtime \
brewpi/brewpi-raspbian bash

# Start up brewpi docker container
docker run -d \
--name brewpi \
-p 80:80 \
-v ~/brewpi-data:/data \
-v /etc/timezone:/etc/timezone \
-v /etc/localtime:/etc/localtime \
--restart always \
brewpi/brewpi-raspbian




# Setup wifi on the Brewpi Spark
See also:
* https://docs.particle.io/guide/tools-and-features/cli/photon/

## Easier method
1. Install screen
   1. `apt -y install screen`
1. Put the particle in setup mode
   1. Hold the setup button for 5 seconds until the LED is flashing blue to put the Photon in listening mode
1. Connect to particle
   1. `screen /dev/ttyACM0`
1. Get MAC address
   1. `m`
1. Setup wifi
   1. `w`

## Harder
### Install the Particle CLI
```
bash <( curl -sL https://particle.io/install-cli )
```
### Put particle in setup mode
Hold the setup button for 5 seconds until the LED is flashing blue to put the Photon in listening mode
### Run wifi setup command
```
bin/particle serial wifi
```
