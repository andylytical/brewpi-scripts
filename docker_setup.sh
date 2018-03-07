#!/bin/bash


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
fn="$(readlink -e ${BASH_SOURCE[$i]%/*})"/bash.common
[[ -r $fn ]] || { echo "Cant access file '$fn'" 1>&2; exit 1
}
source $fn


### Expect this script to run as root
assert_root || die "Run this script as root"

ensure_docker || die "Failed at: ensure_docker"

configure_docker || die "Failed at: configure_docker"

start_docker || die "Failed at: start_docker"
