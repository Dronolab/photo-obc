#!/bin/bash


# Define a timestamp function
timestamp() {
  date +%s%N | cut -b1-15
}

cd $1

while true; do
	timest=$(timestamp)
	ext=".jpg"
	filename=$timest$ext
	sudo gphoto2 --capture-image-and-download --force-overwrite --filename=$filename
done


