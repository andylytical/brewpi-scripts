#!/bin/bash

DEBUG=1

# Adjust these for the tilt colors you have
TILT_COLORS=( red )

# Adjust these based on your answers to the brewpi-tools installer
# The values here are the defaults from brewpi-tools installer for Raspbian Jessie
WEBDIR=/var/www/html
BREWPI_HOME=/home/brewpi
BREWPI_USER=brewpi

#
# End of user configurable settings
# (shouldn't need to change anything below here)
#

BASE=/tmp/tilt-install
BREWOMETER_BASE=$BASE/brewpi-brewometer
BREWOMETER_URL=https://github.com/sibowler/brewpi-brewometer.git
REQUIRED_PKGS=( bluez python-bluez python-scipy python-numpy libcap2-bin )


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


[[ $DEBUG -eq 1 ]] && set -x


# Ensure required packages
aptitude -q -y update
aptitude -q -y install "${REQUIRED_PKGS[@]}" || die "required packages"


# Needed for parse_brewpi_json
pip install tabulate


# Enable python to read socket
pyexe=$( readlink -f $( which python ) )
setcap cap_net_raw+eip "$pyexe" || die "setcap"


# Get repo if not already local
[[ -d $BREWOMETER_BASE ]] || \
git clone $BREWOMETER_URL $BREWOMETER_BASE || die "git clone"


# Copy brewpi-web files
copy_files $BREWOMETER_BASE/brewpi-web $WEBDIR


# Copy brewpi-script files
copy_files $BREWOMETER_BASE/brewpi-script $BREWPI_HOME


# Setup Tilt calibration files
tiltdir=$( 
    find $BREWPI_HOME -type f -name 'TEMPERATURE.colour' -printf '%h' \
    | head -1 )
for color in "${TILT_COLORS[@]}"; do
    for pfx in TEMPERATURE GRAVITY; do
        src_fn=$tiltdir/${pfx}.colour
        tgt_fn=$tiltdir/${pfx}.$color
        [[ -f $fn ]] || grep '^[0-9]' $src_fn > $tgt_fn
    done
done


# Test retrieve data from Tilt
testfn=TiltHydrometerTest.py
testdir=$( find "$BREWOMETER_BASE" -name $testfn -printf '%h' )
# fix test to run only a few times
orig=$testdir/$testfn
copy=$testdir/${testfn}.copy
cp $orig $copy
sed -e '/for num in range(1,120):/c\for num in range(1,5):' $copy > $orig
echo "Testing connection to tilt (as user $BREWPI_USER):"
( cd $testdir; sudo -u $BREWPI_USER python $testfn )

set +x 

echo
echo "Be sure to edit the Tilt calibration files for each colour Tilt you own..."
for color in "${TILT_COLORS[@]}"; do
    for fn in $( find "$BREWPI_HOME" -name "*.$color" ); do
        echo $fn
        cat $fn
    done
    echo
done

