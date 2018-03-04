#!/bin/bash

# TODO - Pass in tilt colors, temp and gravity calibrations on cmdline
# TODO   or in a file
# TODO - Automate hack to remove tilt temp from graph

# Adjust these for the tilt colors you have
TILT_COLORS=( red )

# Adjust these based on your answers to the brewpi-tools installer
# The values here are the defaults from brewpi-tools installer for Raspbian Jessie
WEBDIR=/var/www/html
BREWPI_HOME=/home/brewpi
BREWPI_USER=brewpi

###
# End of user configurable settings
# (shouldn't need to change anything below here)
###

BASE=/tmp/tilt-install
BREWOMETER_BASE=$BASE/brewpi-brewometer
BREWOMETER_URL=https://github.com/sibowler/brewpi-brewometer.git
REQUIRED_PKGS=( bluez python-bluez python-scipy python-numpy libcap2-bin )
MAXAGE=86400


# Import common functions
fn=brewpi-scripts/bash.common
[[ -r $fn ]] || { echo "Cant access file '$fn'"; exit 1
}
source $fn


# Expect this script to run as root
assert_root || die "Run this script as root"


FORCE=0
DEBUG=0
VERBOSE=0
# Process cmdline options
while getopts ":fvd" opt; do
    case $opt in
        f) FORCE=1 ;;
        v) VERBOSE=1 ;;
        d) DEBUG=1 ;;
    esac
done
shift $((OPTIND-1))
[[ $DEBUG -eq 1 ]] && set -x


# Ensure required packages
apt_update
echo -n 'Installing required pkgs... '
apt -yqq install "${REQUIRED_PKGS[@]}" || die 'required packages'
echo 'OK'


# Needed for parse_brewpi_json
echo -n 'Installing python tabulate... '
pip install tabulate || die 'install python tabulate'
echo 'OK'


echo -n 'Enabling python read socket... '
pyexe=$( readlink -f $( which python ) )
setcap cap_net_raw+eip "$pyexe" || die 'setcap'
echo 'OK'


echo -n 'Get brewometer code... '
[[ $FORCE -eq 1 ]] && find $BREWOMETER_BASE -delete
is_recent $BREWOMETER_BASE $MAXAGE \
|| git clone $BREWOMETER_URL $BREWOMETER_BASE \
|| die "git clone"
echo 'OK'

echo -n 'Installing tilt web files... '
copy_files $BREWOMETER_BASE/brewpi-web $WEBDIR || die 'install tilt web files'
echo 'OK'


echo -n 'Installing tilt brewpi files... '
copy_files $BREWOMETER_BASE/brewpi-script $BREWPI_HOME || die 'install tile brewpi files'
echo 'OK'


# Setup Tilt calibration files
echo -n 'Installing (default) tilt calibration files... '
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
echo 'OK'

# Test tilt connectivity
testfn=TiltHydrometerTest.py
testdir=$( find "$BREWOMETER_BASE" -name $testfn -printf '%h' )
# HACKTHIS - fix test to run only a few times
orig=$testdir/$testfn
copy=$testdir/${testfn}.copy
cp $orig $copy
sed -e '/for num in range(1,120):/c\for num in range(1,5):' $copy > $orig
echo "Testing connection to tilt (as user $BREWPI_USER):"
( cd $testdir; sudo -u $BREWPI_USER python $testfn )

set +x 

echo
echo
echo "Be sure to edit the Tilt calibration files for each colour Tilt you own..."
for color in "${TILT_COLORS[@]}"; do
    for fn in $( find "$BREWPI_HOME" -name "*.$color" ); do
        echo $fn
        cat $fn
    done
    echo
done

