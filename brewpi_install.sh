#!/bin/bash

DEBUG=1
BASE=/tmp/brewpi-install
BREWPI_BASE=$BASE/brewpi-tools
BREWPI_URL=https://github.com/BrewPi/brewpi-tools.git


function die() {
  echo "FATAL ERROR: $*" >&2
  exit 1
}


# Expect this script to run as root
[[ $(id -u) -eq 0 ]] || die "Run this script as root"


# Install brewpi
$BREWPI_BASE/install.sh


# Update brewpi code and connected devices
$BREWPI_BASE/updater.sh


