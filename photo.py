#!/usr/bin/env python
import json
import pyexiv2
import logging
import sys
import time
import os
#import sruct

from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler
from bson import BSON
from bson import json_util
from pymongo import MongoClient

client = MongoClient('localhost', 27017)
db = client['fly-database']
collection = db['fly-collection']

namelist = []
picTime = []

"""
class EventHandler(FileSystemEventHandler):
	patterns = ["*.jpg"]
	def process(self, event):
		picStack[count] = event.src_path
		count = count + 1

	def on_created(self, event):
	    self.process(event)
"""
def dataFromTimestamp(timestamp):
	dataset = json.loads('{"pitch": -1, "roll": -1, "yaw": -1, "latitude": -1, "longitude": -1, "heading": -1, "altitude": -1, "relative_alt": -1, "unix30": -1, "unix33": -1, "unixPicName": -1}')

	res30 = list(collection.find({
		"packet_id": 30,
		"$and":[{
				"unix": { "$gte":  float(float(timestamp) - 0.3), "$lte":  float(float(timestamp) + 0.3) }
				}]
		}))

	res33 = list(collection.find({
		"packet_id": 33,
		"$and":[{
				"unix": { "$gte":  float(float(timestamp) - 0.3), "$lte":  float(float(timestamp) + 0.3) }
				}]
		}))

	bestRes30 = findBestMatch(res30, timestamp)
	bestRes33 = findBestMatch(res33, timestamp)

	dataset['yaw']=bestRes30['yaw']
	dataset['pitch']=bestRes30['pitch']
	dataset['roll']=bestRes30['roll']
	dataset['latitude']=bestRes33['lat']
	dataset['longitude']=bestRes33['lon']
	dataset['altitude']=bestRes33['alt']
	dataset['heading']=bestRes33['hdg']
	dataset['relative_alt']=bestRes33['relative_alt']
	dataset['unix30']=bestRes30['unix']
	dataset['unix33']=bestRes33['unix']
	dataset['unixPicName']=timestamp

	return dataset

def findBestMatch(datasets, timestamp):
	index = min(range(len(datasets)), key=lambda i: abs(datasets[i]['unix']-float(timestamp)))
	print index
	return datasets[index]

def matchTimeFormat(timestamp):
	return timestamp[:10] + '.' + timestamp[10:]

def to_deg(value, loc):
	if value < 0:
	   loc_value = loc[0]
	elif value > 0:
	   loc_value = loc[1]
	else:
	   loc_value = ""
	abs_value = abs(value)
	deg =  int(abs_value)
	t1 = (abs_value-deg)*60
	min = int(t1)
	sec = round((t1 - min)* 60, 5)
	return (deg, min, sec, loc_value)

def picInception(file_name, lat, lng, hdg, alt, rll, pch):

	lat_deg = to_deg(lat, ["S", "N"])
	lng_deg = to_deg(lng, ["W", "E"])

	if alt < 0:
	   	rel_byte = '1'
	else:
		rel_byte = '0'

	print lat_deg
	print lng_deg

	# convert decimal coordinates into degrees, munutes and seconds
	exiv_lat = (pyexiv2.Rational(lat_deg[0]*60+lat_deg[1],60),pyexiv2.Rational(lat_deg[2]*100,6000), pyexiv2.Rational(0, 1))
	exiv_lng = (pyexiv2.Rational(lng_deg[0]*60+lng_deg[1],60),pyexiv2.Rational(lng_deg[2]*100,6000), pyexiv2.Rational(0, 1))
	exiv_hdg = pyexiv2.Rational(hdg, 360)
	exiv_alt = pyexiv2.Rational(alt, 100000000)

	print exiv_lat
	print exiv_lng

	exiv_image = pyexiv2.ImageMetadata(file_name)
	exiv_image.read()
	exif_keys = exiv_image.exif_keys

#	exiv_r_b = bytarray(struct.pack("f", rll))
#	exiv_p_b = bytarray(struct.pack("f", pch))

#	exiv_r_p = exiv_r_b.append(exiv_p_b)
	print exiv_lat, exiv_lng
	exiv_image["Exif.GPSInfo.GPSLatitude"] = exiv_lat
	exiv_image["Exif.GPSInfo.GPSLatitudeRef"] = lat_deg[3]
	exiv_image["Exif.GPSInfo.GPSLongitude"] = exiv_lng
	exiv_image["Exif.GPSInfo.GPSLongitudeRef"] = lng_deg[3]
	exiv_image["Exif.Image.GPSTag"] = 654
	exiv_image["Exif.GPSInfo.GPSMapDatum"] = "WGS-84"
	exiv_image["Exif.GPSInfo.GPSVersionID"] = '2 0 0 0'
	exiv_image["Exif.GPSInfo.GPSDestBearing"] = exiv_hdg
	exiv_image["Exif.GPSInfo.GPSDestBearingRef"] = 'M'
	exiv_image["Exif.GPSInfo.GPSAltitude"] = exiv_alt
	exiv_image["Exif.GPSInfo.GPSAltitudeRef"] = rel_byte
#	exiv_image["Exif.Photo.UserComment"] = exiv_r_p

	exiv_image.write()

def main():
	path='/home/dronolab/dev/photo/captures/'

	try:
		while True:
			picTime = []
			namelist = []
			fileList = []
			try:
				#fileList = dict ([(f, f.split('.')[0]) for f in os.listdir(path) if f.split('.')[1] == "jpg" if f[0] == '1'])
				for f in os.listdir(path):
					if f.split('.')[1] == "jpg":
						if f[0] == '1':
							fileList = dict([(f, f.split('.')[0])])
							print fileList
							for key, value in fileList.items():
								namelist.append(value)
								picTime.append(matchTimeFormat(value))

							print picTime
							if len(picTime) != 0:
								for i in range(0, len(picTime)):
									picPath=path + namelist[i] + '.jpg'
									print picTime[i]
									print picPath
									rawDatasets = dataFromTimestamp(picTime[i])
									print rawDatasets
									print float(rawDatasets['latitude']), float(rawDatasets['longitude']), float(rawDatasets['heading']), float(rawDatasets['relative_alt']), float(rawDatasets['roll']), float(rawDatasets['pitch'])
									picInception(picPath, float(rawDatasets['latitude']), float(rawDatasets['longitude']), float(rawDatasets['heading']), float(rawDatasets['relative_alt']), float(rawDatasets['roll']), float(rawDatasets['pitch']))
									os.rename(picPath, path+'R-'+namelist[i]+'.jpg')
							else:
								print "NO PICTURES IN DICK  PIC : len(picTime) = 0"
				time.sleep(0.5)
			except:
				pass

	except (KeyboardInterrupt, SystemExit):
		raise

if __name__ == "__main__":
	main()



