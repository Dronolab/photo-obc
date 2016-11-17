#!/usr/bin/env python
import json
import pyexiv2
import logging
import sys
import time
import os
import struct

from pymongo import MongoClient

client = MongoClient('localhost', 27017)
db = client['fly-database']
collection = db['fly-collection']

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

	dataset['yaw']=float(bestRes30['yaw'])
	dataset['pitch']=float(bestRes30['pitch'])
	dataset['roll']=float(bestRes30['roll'])
	dataset['latitude']=float(bestRes33['lat'])
	dataset['longitude']=float(bestRes33['lon'])
	dataset['altitude']=float(bestRes33['alt'])
	dataset['heading']=float(bestRes33['hdg'])
	dataset['relative_alt']=float(bestRes33['relative_alt'])
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

def picExifInception(file_path, lat, lng, hdg, alt, rll, pch):

	lat_deg = to_deg(lat, ["S", "N"])
	lng_deg = to_deg(lng, ["W", "E"])

	if alt < 0:
	   	rel_byte = '1'
	else:
		rel_byte = '0'

	exiv_lat = (pyexiv2.Rational(lat_deg[0]*60+lat_deg[1],60),pyexiv2.Rational(lat_deg[2]*100,6000), pyexiv2.Rational(0, 1))
	exiv_lng = (pyexiv2.Rational(lng_deg[0]*60+lng_deg[1],60),pyexiv2.Rational(lng_deg[2]*100,6000), pyexiv2.Rational(0, 1))
	exiv_hdg = pyexiv2.Rational(hdg, 360)
	exiv_alt = pyexiv2.Rational(alt, 100000000)

	exiv_image = pyexiv2.ImageMetadata(file_path)
	exiv_image.read()
	exif_keys = exiv_image.exif_keys

	exiv_r_b = bytarray(struct.pack("f", rll))
	exiv_p_b = bytarray(struct.pack("f", pch))
	exiv_r_p = exiv_r_b.append(exiv_p_b)

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
	exiv_image["Exif.Photo.UserComment"] = exiv_r_p

	exiv_image.write()

def picXMPInception(file_path, altAGL, altMSL, lat, lng, hdg, grll, gpch, gyaw, imgw, ts):

	print "writing exif"
	metadata = pyexiv2.ImageMetadata(file_path)
	metadata.read()
	pyexiv2.xmp.register_namespace('http://dronolab.com/', 'dronolab')

	formatLat = (pyexiv2.Rational(lat_deg[0]*60+lat_deg[1],60),pyexiv2.Rational(lat_deg[2]*100,6000), pyexiv2.Rational(0, 1))
	formatLng = (pyexiv2.Rational(lng_deg[0]*60+lng_deg[1],60),pyexiv2.Rational(lng_deg[2]*100,6000), pyexiv2.Rational(0, 1))

	metadata['Xmp.dronolab.RelativeAltitude'] = altAGL
	metadata['Xmp.dronolab.AbsoluteAltitude'] = altMSL
	metadata['Xmp.dronolab.GPSLongitude'] = formatLng
	metadata['Xmp.dronolab.GPSLatitude'] = formatLat
	metadata['Xmp.dronolab.GPSBearing'] = hdg
	metadata['Xmp.dronolab.GPSBearingRef'] = 'MAGNETIC'
	metadata['Xmp.dronolab.GimbalRollDegree'] = grll
	metadata['Xmp.dronolab.GimbalPitchDegree'] = gpch
	metadata['Xmp.dronolab.GimbalYawDegree'] = gyaw
	metadata['Xmp.dronolab.ImageWeight'] = imgw
	metadata['Xmp.dronolab.TimeStamp'] = ts

	metadata.write()
	print "writing out"


def main():
	path='/home/drono/obc/dev/photo/captures/'
	fakeDataset = json.loads('{"gpch": 6.124, "grll": -5.124, "gyaw": 7.98, "lat": 50.89, "lon": 69.69, "hdg": 169.2, "altMSL": 123.12, "altAGL": 127.45, "imgw": 10, "ts": "2016-10-11 21-22-22"}')
	try:
		while True:
			picTime = []
			namelist = []
			fileList = []
			try:
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
									print rawDatasets['latitude'], rawDatasets['longitude'], rawDatasets['heading'], rawDatasets['relative_alt'], rawDatasets['roll'], rawDatasets['pitch']

									picExifInception(picPath,
										rawDatasets['latitude'],
										rawDatasets['longitude'],
										rawDatasets['heading'],
										rawDatasets['relative_alt'],
										rawDatasets['roll'],
										rawDatasets['pitch'])

									picXMPInception(picPath,
										fakeDataset['altAGL'],
										fakeDataset['altMSL'],
										fakeDataset['lat'],
										fakeDataset['lon'],
										fakeDataset['hdg'],
										fakeDataset['grll'],
										fakeDataset['gpch'],
										fakeDataset['gyaw'],
										fakeDataset['imgw'],
										fakeDataset['ts'])

									os.rename(picPath, path+'X-'+namelist[i]+'.jpg')
							else:
								print "NO PICTURES IN DICK  PIC : len(picTime) = 0"
				time.sleep(0.5)
			except:
				pass

	except (KeyboardInterrupt, SystemExit):
		raise

if __name__ == "__main__":
	main()



