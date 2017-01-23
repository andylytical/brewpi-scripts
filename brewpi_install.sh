#!/bin/bash

BASE=/tmp/brewpi-install
BREWPI_BASE=$BASE/brewpi-tools
BREWPI_URL=https://github.com/BrewPi/brewpi-tools.git
BREWPI_INSTALL_LOG=install.log #this is always in the local dir
MAXAGE=604800

fn=brewpi-scripts/bash.common
[[ -r $fn ]] || { echo "Cant access file '$fn'"; exit 1
}
source $fn


# Process cmdline options
DEBUG=0
while getopts ":fd" opt; do
    case $opt in
        d) DEBUG=1 ;;
    esac
done
[[ $DEBUG -eq 1 ]] && set -x


# Expect this script to run as root
assert_root || die "Run this script as root"


# Ensure latest brewpi codebase
is_recent $BREWPI_BASE $MAXAGE || {
    find $BREWPI_BASE -delete 2>/dev/null
    git clone $BREWPI_URL $BREWPI_BASE
} || die "git clone brewpi-tools failed"


# Install brewpi
is_recent $BREWPI_INSTALL_LOG $MAXAGE \
|| $BREWPI_BASE/install.sh \
|| die "brewpi install failed"


# Update brewpi code and connected devices
$BREWPI_BASE/updater.py || die "brewpi update failed"
