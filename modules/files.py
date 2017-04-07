import os
import time
from os import listdir
from os.path import isfile, join
import imp
import subprocess
from collections import deque

f_timer = imp.find_module('timer', ['./modules/'])
timer = imp.load_module('timer', *f_timer)

from timer import FunctionTimer

metadata = imp.find_module('metadata', ['./modules/'])
metadata = imp.load_module('metadata', *metadata)

import metadata as meta


class Files:
    def __init__(self, database, c):
        self.files = None
        self.names = None
        self.times = None
        self.paths = None
        self.ctl = FunctionTimer(c['RATE'], self.ctl, c)
        self.process_pictures = self.process_pictures(database, c)

    def ctl(self, c):
        self.files = self.get_file_list(c['PICTURE_PATH'])
        self.names = self.get_name_list()
        self.times = self.get_time_list()
        self.paths = self.get_path_list(c)

    def get_name_list(self):
        names = deque([])
        if self.files is not None:
            for a in self.files:
                names.appendleft(a.split(".")[0])
            return names

    def get_time_list(self):
        times = deque([])
        if self.files is not None:
            for key, value in self.files.items():
                times.appendleft(self.match_time_format(value))
            return times

    def get_path_list(self, c):
        paths = deque([])
        if self.files is not None:
            for i in range(0, len(self.names)):
                paths.appendleft(c['PICTURE_PATH'] + self.names[i] + '.jpg')
            return paths

    def process_pictures(self, db, c):
        while True:
            l_path = self.paths
            l_names = self.names
            l_times = self.times
            if l_path is not None:
                for i in range(0, len(l_path)):
                    data = db.data_from_timestamp(l_times[i], c)
                    if data is not None:
                        meta.exif_write(l_path[i],
                                        data['lat'],
                                        data['lon'],
                                        data['hdg'],
                                        data['altAGL'],
                                        data['drll'],
                                        data['dpch'])

                        meta.xmp_write(l_path[i],
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

                        mv = 'mv {0} {1}X-{2}.jpg '.format(l_path[i], c['PICTURE_PATH'], l_names[i])
                        subprocess.Popen(mv, shell=True,
                                               stdout=subprocess.PIPE).stdout.read()
                    if data is None:
                        if l_path[i]:
                            try:
                                mv = 'mv {0} {1}U-{2}.jpg '.format(l_path[i], c['PICTURE_PATH'], l_names[i])
                                subprocess.Popen(mv, shell=True,
                                                       stdout=subprocess.PIPE).stdout.read()
                                print "NO DATA"
                            except:
                                print "BUG"

            # else:
                # print "NO PICTURES"

    def get_file_list(self, path):
        ofiles = [f for f in listdir(path) if isfile(join(path, f))]
        a = dict()
        for f in ofiles:
            if f.split('.')[1] == "jpg":
                if f[0] == '1':
                    a.update([(f, f.split('.')[0])])
        return a

    def match_time_format(self, timestamp):
        return timestamp[:10] + '.' + timestamp[10:]

    def stop():
        self.ctl.stop()
