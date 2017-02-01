import os
from collections import deque
import modules.metadata as meta


class Files:
    def __init__(self, database, c):
        self.files = self.get_file_list(c['PICTURE_PATH'])
        self.names = self.get_name_list()
        self.times = self.get_time_list()
        self.paths = self.get_path_list(c)
        self.process_pictures = self.process_pictures(database)

    def get_name_list(self):
        names = deque([])
        for key, value in self.files.items():
            names.appendleft(value)
        return names

    def get_time_list(self):
        times = deque([])
        for key, value in self.files.items():
            times.appendleft(self.match_time_format(value))
        return times

    def get_path_list(self, c):
        paths = deque([])
        for i in range(0, len(self.names)):
            paths.appendleft(c['PICTURE_PATH'] + self.names[i] + '.jpg')
        return paths

    def process_pictures(self, db, c):
        if len(self.paths) != 0:
            for i in range(0, len(self.paths)):
                data = db.data_from_timestamp(self.times[i])
                print data

                meta.exif_write(self.paths[i],
                                data['lat'],
                                data['lon'],
                                data['hdg'],
                                data['altAGL'],
                                data['drll'],
                                data['dpch'])

                meta.xmp_write(self.paths[i],
                               data['altAGL'],
                               data['altMSL'],
                               data['lat'],
                               data['lon'],
                               data['hdg'],
                               data['drll'],
                               data['dpch'],
                               data['dyaw'],
                               data['imgw'],
                               data['unixPicName'][:10])

                os.rename(self.paths[i],
                          c['PICTURE_PATH'] + 'X-' + self.names[i] + '.jpg')
        else:
            print "NO PICTURES"

    @staticmethod
    def get_file_list(path)
        for f in os.listdir(path):
            if f.split('.')[1] == "jpg":
                if f[0] == '1':
                    return dict([(f, f.split('.')[0])])

    @staticmethod
    def match_time_format(timestamp):
        return timestamp[:10] + '.' + timestamp[10:]