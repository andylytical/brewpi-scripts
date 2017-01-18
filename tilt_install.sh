#!/bin/bash

DEBUG=1
BASE=/tmp/tilt-install
BREWOMETER_BASE=$BASE/brewpi-brewometer
BREWOMETER_URL=https://github.com/sibowler/brewpi-brewometer.git
REQUIRED_PGKS=( bluez python-bluez python-scipy python-numpy libcap2-bin )
WEBDIR=/var/www/html
BREWPI_HOME=/home/brewpi
BREWPI_USER=brewpi
TILT_COLORS=( red )


function die() {
  echo "FATAL ERROR: $*" >&2
  exit 1
}


###
#  Recursively sync files from SRCDIR to TGTDIR
#  Perform a chown on each file changed in TGTDIR
###
function copy_files() {
    tmpfn=$( mktemp )
    [[ $DEBUG -eq 1 ]] && set -x
    srcdir="$1"
    tgtdir="$2"
    #get owner:group of tgtdir
    usr_grp=$( stat -c '%u:%g' "$tgtdir" )
    rsync -rvic "$srcdir/" "$tgtdir/" \
    | awk '/^[>c]/ {print substr($0,13);}' \
    | tee $tmpfn \
    | xargs -I{} chown $usr_grp "$tgtdir/{}"
    [[ $DEBUG -eq 1 ]] && { 
        echo "Copied the following files to '$tgtdir':"
        cat $tmpfn
    }
    rm -f $tmpfn
}


# Expect this script to run as root
[[ $(id -u) -eq 0 ]] || die "Run this script as root"


# Ensure required packages
aptitude -q -y update
aptitude -q -y install "${REQUIRED_PKGS[@]}" || die "required packages"


# Enable python to read socket
pyexe=$( readlink -f $( which python ) )
setcap cap_net_raw+eip "$pyexe" || die "setcap"


[[ $DEBUG -eq 1 ]] && set -x


# Get repo if not already local
[[ -d $BREWOMETER_BASE ]] || \
git clone $BREWOMETER_URL $BREWOMETER_BASE || die "git clone"


# Copy brewpi-web files
copy_files $BREWOMETER_BASE/brewpi-web $WEBDIR


# Copy brewpi-script files
copy_files $BREWOMETER_BASE/brewpi-script $BREWPI_HOME


# Setup Tilt calibration files
tiltdir=$( 
    find $BREWPI_HOME -type f -name 'TEMPERATURE.colour' -printf '%h\n' \
    | head -1 )
for color in "${TILT_COLORS[@]}"; do
    for pfx in TEMPERATURE GRAVITY; do
        src_fn=$tiltdir/${pfx}.colour
        tgt_fn=$tiltdir/${pfx}.$color
        [[ -f $fn ]] || grep '^[0-9]' $src_fn > $tgt_fn
    done
done


set +x 


# Test retrieve data from Tilt
testfn=TiltHydrometerTest.py
testdir=$( find "$BREWOMETER_BASE" -name $testfn -printf '%h' )
echo
echo "Running test connection to tilt:"
( cd $testdir; sudo -u $BREWPI_USER python $testfn )

echo
echo "Be sure to edit the Tilt calibration files for each colour Tilt you own..."
find "$BREWPI_HOME" -name 'TEMPERATURE*' | grep -v colour
find "$BREWPI_HOME" -name 'GRAVITY*' | grep -v colour

