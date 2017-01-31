#!/usr/bin/env python
import json
import pyexiv2
import logging
import sys
import time
import os
import struct
import datetime
from pymongo import MongoClient

TZ = -5.0

client = MongoClient('localhost', 27017)
db = client['fly-database']
collection = db['fly-collection']

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

def dataFromTimestamp(timestamp):
	dataset = json.loads('{"dpch": -1, "drll": -1, "dyaw": -1, "lat": -1, "lon": -1, "hdg": -1, "altMSL": -1, "altAGL": -1, "unix30": -1, "unix33": -1, "unixPicName": -1, "grll": -1, "gpch": -1, "gyaw": -1, "imgw": -1}')

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

	dataset['dyaw']=float(bestRes30['yaw'])
	dataset['dpch']=float(bestRes30['pitch'])
	dataset['drll']=float(bestRes30['roll'])
	dataset['lat']=float(bestRes33['lat'])
	dataset['lon']=float(bestRes33['lon'])
	dataset['altMSL']=float(bestRes33['alt'])
	dataset['hdg']=float(bestRes33['hdg'])
	dataset['altAGL']=float(bestRes33['relative_alt'])
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

def picExifInception(file_path, lat, lng, hdg, alt, drll, dpch):

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

def picXMPInception(file_path, altAGL, altMSL, lat, lng, hdg, drll, dpch, dyaw, imgw, ts):
	lat_deg = to_dddmm_mmmmk(lat, ["S", "N"])
	lng_deg = to_dddmm_mmmmk(lng, ["W", "E"])

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

def main():
	path=''
	#fakeDataset = json.loads('{"gpch": 6.124, "grll": -5.124, "gyaw": 7.98, "lat": 50.89, "lon": 69.69, "hdg": 169.2, "altMSL": 123.12, "altAGL": 127.45, "imgw": 10, "ts": "2016-10-11 21-22-22"}')
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

									picExifInception(picPath, \
										rawDatasets['lat'], \
										rawDatasets['lon'], \
										rawDatasets['hdg'], \
										rawDatasets['altAGL'], \
										rawDatasets['drll'], \
										rawDatasets['dpch'])

									picXMPInception(picPath, \
										rawDatasets['altAGL'], \
										rawDatasets['altMSL'], \
										rawDatasets['lat'], \
										rawDatasets['lon'], \
										rawDatasets['hdg'], \
										rawDatasets['drll'], \
										rawDatasets['dpch'], \
										rawDatasets['dyaw'], \
										rawDatasets['imgw'], \
										rawDatasets['unixPicName'][:10])

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



