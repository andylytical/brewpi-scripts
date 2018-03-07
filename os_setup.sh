#!/bin/bash

__additional_packages=( git less tree vim )


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


apt_update

sudo apt -yqq install "${__additional_pkgs[@]}"
sudo apt -y full-upgrade
sudo reboot
