#!/bin/bash
set -euo pipefail
cd $(dirname "$0")

# sudo apt install imagemagick libopenjp2-7 python3-pip
# sudo pip3 install --upgrade brother_ql

caption=$1

tmpfile=$(mktemp /tmp/label-image.XXXXXX.png)
convert -size 1109x696 -background white -gravity Center -pointsize 100 -font "FreeMono" caption:"$caption" "$tmpfile"

brother_ql -m QL-820NWB -p /dev/usb/lp0 print -l 62x100 -d "$tmpfile"
rm "$tmpfile"
