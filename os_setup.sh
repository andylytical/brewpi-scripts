#!/bin/bash

__additional_pkgs=( git less tree vim jq )


### Process cmdline options
DEBUG=0
while getopts ":d" opt; do
    case $opt in
        d) DEBUG=1 ;;
    esac
done
[[ $DEBUG -eq 1 ]] && set -x


### Source common functions
fn="$(readlink -e ${BASH_SOURCE[$i]%/*})"/bash.common
[[ -r $fn ]] || { echo "Cant access file '$fn'" 1>&2; exit 1
}
source $fn


echo "Downloading catalogs (this could take a few minutes)..."
apt_update

# Install additional packages
sudo apt -y install "${__additional_pkgs[@]}"

# Perform full OS update
sudo apt -y full-upgrade

# Minimize RAM dedicated to GPU
grep -q gpu_mem /boot/config.txt || sudo sed -ie '$agpu_mem=16' /boot/config.txt

sudo reboot
