# DRONOLAB - OBC PHOTO

## Requirements

* Python 3.x
* virtualenv-3.x

## Deploy

* `/etc/systemd/system/`

* `systemctl status photo@root.service`

* `systemctl status syncthing@dronolab.service`

* `systemctl status mongodb.service`

* `systemctl daemon-reload`


#MongoDB

* `nano /etc/mongod.conf`
* dbPath: `/var/lib/mongodb`
