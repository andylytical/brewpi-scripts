#!/bin/bash

BASE=/home/pi
MAXAGE=604800


function ensure_docker() {
    [[ $DEBUG -eq 1 ]] && set -x
    which docker &>/dev/null \
    || curl -sSL https://get.docker.com | sh
}


function configure_docker() {
    [[ $DEBUG -eq 1 ]] && set -x
    id -nG pi | grep -q docker || {
        usermod -aG docker pi
        systemctl enable docker
    }
}


function start_docker() {
    [[ $DEBUG -eq 1 ]] && set -x
    systemctl start docker
}


### Process cmdline options
DEBUG=0
while getopts ":d" opt; do
    case $opt in
        d) DEBUG=1 ;;
    esac
done
[[ $DEBUG -eq 1 ]] && set -x


### Source common functions
fn=$BASE/brewpi-scripts/bash.common
[[ -r $fn ]] || { echo "Cant access file '$fn'" 1>&2; exit 1
}
source $fn


### Expect this script to run as root
assert_root || die "Run this script as root"

try ensure_docker
ensure_docker || die "Failed at step: ensure_docker"

configure_docker || die "Failed"
