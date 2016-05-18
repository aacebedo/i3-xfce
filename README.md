# i3-xfce
This tool will install packages and scripts in order to use i3 with xfce. Amongst other things, it replaces
the builtin windows manager (xfwm4) and disable the builtin desktop (xfdesktop).
It has been designed to work with deb packages system and more specifically with ubuntu flavor.
It has been successfully tested with ubuntu 15.04/15.10/16.04 and xubuntu 15.04/15.10/16.04.

### Dependencies
- *Ubuntu 15.04/15.10/16.04
- Ansible >=1.9.0 (www.ansible.com)
- Python2 >=2.7.0
- Python3 >=3.0.0
- Python-yaml
- Python-progressbar

### Install and configure
$> ./setup.py install -prefix=<install path>

### Usage
##### Install all
$> ./i3-xfce install
##### Install parts
$> ./i3-xfce install -p <parts>
##### Install help
$> ./i3-xfce install -h
##### Uninstall all
$> ./i3-xfce uninstall
##### Uninstall parts
$> ./i3-xfce uninstall -p <parts>
##### Uninstall help
$> ./i3-xfce uninstall -h

### PPA
PPA for ubuntu is available here:
ppa:aacebedo/i3-xfce-stable 

### Screenshots
![alt tag](https://raw.github.com/aacebedo/i3-xfce/master/screenshot.png)
### License
LGPL
