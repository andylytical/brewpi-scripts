#!/bin/bash

function mkhdr() {
    set +x
    str=$( echo "$1" | tr '[a-z]' '[A-Z]' )
    echo "------------ $str ------------"
    set -x
}

set -x

WEBDIR=/var/www/html
BREWPI_HOME=/home/brewpi
BREWPI_USER=brewpi


mkhdr "check /home/brewpi files"
find $BREWPI_HOME ! -user $BREWPI_USER | wc -l


mkhdr "check tilt temperature and gravity files"
find $BREWPI_HOME/tiltHydrometer -name 'TEMPERATURE*' -o -name 'GRAVITY*' \
| grep -v colour \
| while read; do
  ls -l $REPLY
  wc -l $REPLY
  cat -A $REPLY
done


mkhdr "CHECK WEB DIR PERMISSIONS"
ls -ld $WEBDIR
ls -ld $WEBDIR/data
ls -l $WEBDIR/data


mkhdr "check python pip libraries"
pip freeze | grep -i tabulate


mkhdr "parse brewpi json"
tmpfn=$( mktemp )
/home/pi/brewpi-scripts/parse_brewpi_json.py > $tmpfn
head -6 $tmpfn
tail -n 3 $tmpfn
rm -f $tmpfn
