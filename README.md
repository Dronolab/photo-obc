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
