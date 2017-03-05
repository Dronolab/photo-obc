#!/bin/bash

echo "photo looooooooooop :"
systemctl status photo@root.service | grep active

echo "mongodb"
systemctl status mongodb.service | grep active

echo "syncthing"
systemctl status syncthing@dronolab.service | grep active

echo "mavproxy"
systemctl status  mavproxy@root.service | grep active
