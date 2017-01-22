#!/bin/bash

DEBUG=1
BASE=/tmp/brewpi-install
BREWPI_BASE=$BASE/brewpi-tools
BREWPI_URL=https://github.com/BrewPi/brewpi-tools.git
BREWPI_INSTALL_LOG=install.log #this is always in the local dir
# Don't re-run installs or downloads unless MINAGE seconds have passed since last time
MINAGE=604800
TS_NOW=$( date '+%s' )


function die() {
    echo "FATAL ERROR: $*" >&2
    exit 1
}


function is_recent() {
  # PARAMS:
  # 1. path - path to dir or file
  # If path exists and mtime is less than MINAGE, return 0
  # Otherwise, return 1
    path=$1
    rv=1
    if [[ -e $path ]] ; then
        ts=$( stat -c '%Y' $path )
        let "age = $TS_NOW - $ts"
        if [[ $age -lt $MINAGE ]] ; then
            rv=0
        fi
    fi
  return $rv
}


[[ $DEBUG -gt 0 ]] && set -x


# Expect this script to run as root
[[ $(id -u) -eq 0 ]] || die "Run this script as root"


# Ensure latest brewpi codebase
is_recent $BREWPI_BASE || {
    find $BREWPI_BASE -delete 2>/dev/null
    git clone $BREWPI_URL $BREWPI_BASE
} || die "git clone brewpi-tools failed"
exit 1


# Install brewpi
is_recent $BREWPI_INSTALL_LOG \
|| $BREWPI_BASE/install.sh \
|| die "brewpi install failed"


# Update brewpi code and connected devices
$BREWPI_BASE/updater.py || die "brewpi update failed"


