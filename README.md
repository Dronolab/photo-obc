# DRONOLAB - OBC PHOTO

## Requirements

* Python 2.7

## Deploy

* `/etc/systemd/system/`

* `systemctl status photo@root.service`

* `systemctl status syncthing@dronolab.service`

* `systemctl status mongodb.service`

* `systemctl daemon-reload`


# MongoDB

* `nano /etc/mongod.conf`
* dbPath: `/var/lib/mongodb`

# Photo renaming :

* X : with metadata
* U : no metadata found
* nothing : not process yet

## Usage

* requires to have GPS lock on pixhawk to have XMP tagging

* `ssh dronolab@192.168.1.112`

* remove or move old pictures :
  * `rm ~/dev/photo/captures/*`

* start MAVProxy :
  * `sudo sh ~/dev/photo/start-MAVProxy.sh`

* ensure MAVProxy is running --»n look for mavproxy in running process
  * `htop`

* check service status --» 3 services should appear as active
  * `sh ~/dev/photo/check-services.sh`

* plug the camera --» it should take pictures

* run photo tagging app :
  * `cd /home/dronolab/dev/photo`
 * `python photo.py`
