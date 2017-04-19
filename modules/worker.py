import traceback
import imp
import sys
import os
import subprocess
from multiprocessing import Process

env = sys.argv[1] if len(sys.argv) == 2 else 'default'

metadata = imp.find_module('metadata', ['./modules/'])
metadata = imp.load_module('metadata', *metadata)

a_db = imp.find_module('db', ['./modules/'])
db = imp.load_module('db', *a_db)

import metadata as meta
from db import Database


class Worker:

    def __init__(self, q, config):

        self.q = q
        self.worker_process = None
        self.config = config
        self.action_resolver = {
            'stop': self.__stop_current_task,
            'tag': self.__send_task_to_worker,
        }

    def run(self):
        while True:
            task = self.q.get(True)
            action_type = task[0]
            self.action_resolver[action_type](task)

    def __start_worker(self, task):
        w = WorkerProcess(task[0], self.config, task[1])
        w.run()

    def __stop_current_task(self):
        if self.worker_process and self.worker_process.is_alive():
            self.worker_process.terminate()
            self.worker_process = None
        else:
            return False
        return True

    def __send_task_to_worker(self, task):
        #if self.worker_process and self.worker_process.is_alive():
        #    self.worker_process.terminate()
        #    self.worker_process = None

        self.worker_process = Process(target=self.__start_worker, args=(task,))
        self.worker_process.start()


class WorkerProcess:

    def __init__(self, task, conf, _path):
        self.task = task
        self.db = Database(conf)
        self.conf = conf
        self.current_path = _path
        self.action_resolver = {
            'tag': self.__tag,
        }

    def run(self):
        try:
            self.action_resolver[self.task]()
        except Exception as e:
            trace = traceback.format_exc()
            print trace

    def __tag(self):
        name = self.get_name(self.current_path)
        time = self.get_time(name)
        data = self.db.data_from_timestamp(time, self.conf)
        print name, time
        if data is not None:
            meta.exif_write(self.current_path,
                            data['lat'],
                            data['lon'],
                            data['hdg'],
                            data['altAGL'],
                            data['drll'],
                            data['dpch'])

            meta.xmp_write(self.current_path,
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

            mv = 'mv {0} {1}X-{2}'.format(self.current_path,
                                          self.conf['PICTURE_PATH'],
                                          name)
            subprocess.Popen(mv, shell=True,
                             stdout=subprocess.PIPE).stdout.read()
        if data is None:
            try:
                mv = 'mv {0} {1}U-{2}'.format(self.current_path,
                                              self.conf['PICTURE_PATH'],
                                              name)
                subprocess.Popen(mv, shell=True,
                                 stdout=subprocess.PIPE).stdout.read()
                print "NO DATA"
            except:
                print "BUG"

        self.db.kill()

    @staticmethod
    def get_time(_name):
        timestamp = _name.split('.')[0]
        return timestamp[:10] + '.' + timestamp[10:]

    @staticmethod
    def get_name(_path):
        if os.path.exists(_path):
            return _path.split('/')[-1]
