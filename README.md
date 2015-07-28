# i3-xfce
This tool will install packages and scripts in order to use i3 with xfce. Amongst other things, it replaces
the builtin windows manager (xfwm4) and disable the builtin desktop (xfdesktop).

### Dependencies
- Ubuntu 15.04
- Ansible 1.9 (www.ansible.com)
- Python-YAML

### Usage
##### Install all
$> ./i3-xfce install
##### Install parts
$> ./i3-xfce install -p <parts>
##### Install all
$> ./i3-xfce install -h
##### Uninstall all
$> ./i3-xfce uninstall
##### Uninstall parts
$> ./i3-xfce uninstall -p <parts>
##### Uninstall all
$> ./i3-xfce uninstall -h

### Screenshots
![alt tag](https://raw.github.com/aacebedo/i3-xfce/master/screenshot.png)
### License
LGPL
