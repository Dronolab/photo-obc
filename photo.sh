#!/bin/bash

# Define a timestamp function
timestamp() {
  date +%s%N | cut -b1-15
}

cd /home/dronolab/dev/photo/captures

while true; do
	timest=$(timestamp)
	ext=".jpg"
	filename=$timest$ext
	gphoto2 --capture-image-and-download --force-overwrite --filename=$filename
	chmod 777 $filename
done
