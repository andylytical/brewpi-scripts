#!/bin/bash

BASE=/home/pi
MAXAGE=604800


function ensure_docker() {
    which docker &>/dev/null \
    || curl -sSL https://get.docker.com | sh
}


function configure_docker() {
    id -nG pi | grep -q docker || {
        usermod -aG docker pi
        systemctl enable docker
    }
}


function start_docker() {
    systemctl start docker
}


### Process cmdline options
DEBUG=0
while getopts ":fd" opt; do
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

configure_docker || die "Failed


## Ensure latest brewpi codebase
#is_recent $BREWPI_BASE $MAXAGE || {
#    find $BREWPI_BASE -delete 2>/dev/null
#    git clone $BREWPI_URL $BREWPI_BASE
#} || die "git clone brewpi-tools failed"
#
#
## Install brewpi
#is_recent $BREWPI_INSTALL_LOG $MAXAGE \
#|| $BREWPI_BASE/install.sh \
#|| die "brewpi install failed"
#
#
## Update brewpi code and connected devices
#$BREWPI_BASE/updater.py || die "brewpi update failed"
