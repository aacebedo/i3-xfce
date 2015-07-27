#!/bin/bash


if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root" 1>&2
   exit 1
fi

sudo apt-get install xfce4-panel-dev libjson-glib-dev libxcb1-dev gobject-introspection gtk-doc-tools libxfce4util-dev libglib2.0-dev xfce4-dev-tools libX11-dev xfce4-panel-dev libxfce4ui-1-dev libgtk2.0-dev
cd /tmp
wget https://github.com/acrisci/i3ipc-glib/archive/v0.6.0.tar.gz
wget https://github.com/denesb/xfce4-i3-workspaces-plugin/archive/1.1.0.tar.gz
tar xvzf ./v0.6.0.tar.gz
tar xvzf ./1.1.0.tar.gz
cd i3ipc-glib-0.6.0
./autogen.sh
./configure --prefix=/usr/local/
make
sudo make install
./configure --prefix=/vagrant/output/
make install
cd ../xfce4-i3-workspaces-plugin-1.1.0
./autogen.sh
./configure --prefix=/usr/local
make
sudo make install
./configure --prefix=/vagrant/output
make install


