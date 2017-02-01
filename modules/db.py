import json
from pymongo import MongoClient


class Database(object):
    def __init__(self, c):
        self.client = MongoClient(c['DB_HOST'], c['DB_PORT'])
        self.db = self.client[c['DB_CLIENT']]
        self.collection = self.db[c['DB_COLL']]

    def data_from_timestamp(self, timestamp, c):
        dataset = json.loads('{"dpch": -1, '
                             '"drll": -1, '
                             '"dyaw": -1, '
                             '"lat": -1, '
                             '"lon": -1, '
                             '"hdg": -1, '
                             '"altMSL": -1, '
                             '"altAGL": -1, '
                             '"unix30": -1,'
                             ' "unix33": -1, '
                             '"unixPicName": -1, '
                             '"grll": -1, '
                             '"gpch": -1, '
                             '"gyaw": -1, '
                             '"imgw": -1} ')

        res_30 = list(self.collection.find({
            "packet_id": 30,
            "$and": [dict(unix={"$gte": float(float(timestamp) - c['DELTA']),
                                "$lte": float(float(timestamp) + c['DELTA'])})]
            }))

        res_33 = list(self.collection.find({
            "packet_id": 33,
            "$and": [dict(unix={"$gte": float(float(timestamp) - c['DELTA']),
                                "$lte": float(float(timestamp) + c['DELTA'])})]
            }))

        best_res_30 = self.find_best_match(res_30, timestamp)
        best_res_33 = self.find_best_match(res_33, timestamp)

        dataset['dyaw'] = float(best_res_30['yaw'])
        dataset['dpch'] = float(best_res_30['pitch'])
        dataset['drll'] = float(best_res_30['roll'])
        dataset['lat'] = float(best_res_33['lat'])
        dataset['lon'] = float(best_res_33['lon'])
        dataset['altMSL'] = float(best_res_33['alt'])
        dataset['hdg'] = float(best_res_33['hdg'])
        dataset['altAGL'] = float(best_res_33['relative_alt'])
        dataset['unix30'] = best_res_33['unix']
        dataset['unix33'] = best_res_33['unix']
        dataset['unixPicName'] = timestamp

        return dataset

    @staticmethod
    def find_best_match(dataset, timestamp):
        index = min(range(len(dataset)),
                    key=lambda i: abs(dataset[i]['unix'] - float(timestamp)))
        return dataset[index]