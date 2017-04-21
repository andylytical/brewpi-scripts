#!/bin/bash

WWW=/var/www/html

PRGDIR=$(dirname $0)

css=$PRGDIR/dygraph.2.0.0.min.css
js=$PRGDIR/dygraph.2.0.0.min.js


for x in css js; do
    fn_src=${!x}
    fn_tgt=$WWW/$x/
    set -x
    cp $fn_src $fn_tgt
    set +x
done
