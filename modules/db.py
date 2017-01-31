
class Database(object):
    def __init__(self):
        super(Database, self).__init__()
        self.client = MongoClient('localhost', 27017)
        self.db = client['fly-database']
        self.collection = db['fly-collection']
        self.arg = arg

    def find_best_match(datasets, timestamp):
    	index = min(range(len(datasets)), key=lambda i: abs(datasets[i]['unix']-float(timestamp)))
    	return datasets[index]

    def data_from_timestamp(timestamp):
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

    	bestRes30 = self.find_best_match(res30, timestamp)
    	bestRes33 = self.find_best_match(res33, timestamp)

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
