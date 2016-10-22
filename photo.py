#!/usr/bin/env python
import json
import pyexiv2
import logging
import sys
import time

from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler
from bson import BSON
from bson import json_util
from pymongo import MongoClient

client = MongoClient('localhost', 27017)
db = client['fly-database']
collection = db['fly-collection']

picStack = []
count = 0

class EventHandler(FileSystemEventHandler):
	patterns = ["*.jpg"]
	def process(self, event):
		picStack[count] = event.src_path
		count++
	    print event.src_path, count

	def on_created(self, event):
	    self.process(event)

def dataFromTimestamp(timestamp):
	dataset = json.loads('{"pitch": -1, "roll": -1, "yaw": -1, "latitude": -1, "longitude": -1, "heading": -1, "altitude": -1}')
	datasets[]

	res30 = list(collection.find({
		"packet_id": 30,
		"unix": { "$gte": float(float(timestamp) - 0.1)  },
    	"unix": { "$lte": float(float(timestamp) + 0.1) }
		}))

	res33 = list(collection.find({
		"packet_id": 33,
		"unix": { "$gte": float(float(timestamp) - 0.1) },
    	"unix": { "$lte": float(float(timestamp) + 0.1) }
		}))

	ml = max(res30, res33)

	for k in xrange(0,len(ml)):
		for i in xrange(0,len(res30)):
			dataset['yaw']=res30[i]['yaw']
			dataset['pitch']=res30[i]['pitch']
			dataset['roll']=res30[i]['roll']
			datasets.insert(k, dataset)

		for i in xrange(0,len(res33)):
			dataset['latitude']=res33[i]['lat']
			dataset['longitude']=res33[i]['lon']
			dataset['altitude']=res33[i]['alt']
			dataset['heading']=res33[i]['hdg']
			datasets.insert(k, dataset)

	return datasets

def findBestMatch(datasets, timestamp):
	index = min(range(len(datasets)), key=lambda i: abs(datasets[i]['unix']-float(timestamp))
	return datasets[index]

def matchTimeFormat(timestamp):
	return timestamp[:10] + '.' + timestamp[11:]

def stackPicName(path):
	observer = Observer()
    observer.schedule(EventHandler(), path, recursive=False)
    observer.start()


def main():
    path='/home/dev/photo/captures/'

    stackPicName(path)
    tmp = 0
	try:
        while True:
			picTime = matchTimeFormat(picStack[tmp])
			d = findBestMatch(dataFromTimestamp(picTime), picTime)
        	tmp++
			print d
    except KeyboardInterrupt:
        observer.stop()

    observer.join()

if __name__ == "__main__":
    main()



