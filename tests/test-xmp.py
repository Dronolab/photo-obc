#!/usr/bin/env python
import json
import pyexiv2
import logging
import sys
import time
import os
import struct
import datetime

TZ = -5.0

def to_dddmm_mmmmk(value, loc):
	if value < 0:
	   loc_value = loc[0]
	elif value > 0:
	   loc_value = loc[1]
	else:
	   loc_value = ""
	value = abs(value)
	a, b = divmod(value, 1)
	a = int(a)
	b = b * 60
	b = "{:.4f}".format(b)
	return str(a)+','+str(b)+loc_value

def toFormatTimestamp(dt):
    return datetime.datetime.utcfromtimestamp(dt).strftime("%Y-%m-%d %H:%M:%S")

def picXMPInception(file_path, altAGL, altMSL, lat, lng, hdg, drll, dpch, dyaw, imgw, ts):
	lat_deg = to_dddmm_mmmmk(lat, ["S", "N"])
	lng_deg = to_dddmm_mmmmk(lng, ["W", "E"])

	print "writing exif"
	metadata = pyexiv2.ImageMetadata(file_path)
	metadata.read()
	pyexiv2.xmp.register_namespace('http://dronolab.com/', 'dronolab')


	metadata['Xmp.dronolab.RelativeAltitude'] = str(altAGL)
	metadata['Xmp.dronolab.AbsoluteAltitude'] = str(altMSL)
	metadata['Xmp.dronolab.GPSLongitude'] = lng_deg
	metadata['Xmp.dronolab.GPSLatitude'] = lat_deg
	metadata['Xmp.dronolab.GPSBearing'] = str(hdg)
	metadata['Xmp.dronolab.GPSBearingRef'] = 'MAGNETIC'
	metadata['Xmp.dronolab.GimbalRollDegree'] = str(drll)
	metadata['Xmp.dronolab.GimbalPitchDegree'] = str(dpch)
	metadata['Xmp.dronolab.GimbalYawDegree'] = str(dyaw)
	metadata['Xmp.dronolab.DroneRollDegree'] = str(drll)
	metadata['Xmp.dronolab.DronePitchDegree'] = str(dpch)
	metadata['Xmp.dronolab.DroneYawDegree'] = str(dyaw)
	metadata['Xmp.dronolab.ImageWeight'] = str(imgw)
	metadata['Xmp.dronolab.TimeStamp'] = toFormatTimestamp(float(ts))

	metadata.write()
	print "writing out"

def main():
	path='/home/drono/obc/dev/photo/captures/R-147789091502958.jpg'
	fakeDataset = json.loads('{"gpch": 6.124, "grll": -5.124, "gyaw": 7.98, "lat": 50.89, "lon": 69.69, "hdg": 169.2, "altMSL": 123.12, "altAGL": 127.45, "imgw": 10, "ts": "1479478117000"}')
	picXMPInception(path, fakeDataset['altAGL'], fakeDataset['altMSL'], fakeDataset['lat'], fakeDataset['lon'], fakeDataset['hdg'], fakeDataset['grll'], fakeDataset['gpch'], fakeDataset['gyaw'], fakeDataset['imgw'],fakeDataset['ts'][:10])
	print "success"
if __name__ == "__main__":
	main()