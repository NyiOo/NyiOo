#!/usr/bin/env bash

cd..
path=`pwd`

target=/$HOME/Desktop/DirectionFinder.desktop

cat << EOF > $target

[Desktop Entry]
Version=1.0
Name=Direction Finder
Comment=Kerberrossdr Direction Finder
Exec=$path/run.sh
Icon=$path/icon/signal.png
StartupNotify=false
Terminal=false
Type=Application
Path=$path
EOF

chmod +x $target
