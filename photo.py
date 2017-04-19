import sys
import time
import imp
import subprocess
from multiprocessing import Queue, Process
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

a_w = imp.find_module('worker', ['./modules/'])
worker = imp.load_module('worker', *a_w)

env = sys.argv[1] if len(sys.argv) == 2 else 'default'
a_conf = imp.find_module('default', ['./config/'])
conf = imp.load_module('default', *a_conf)

from worker import Worker
from default import config

services = ['photo@root.service',
            'mongodb.service',
            'syncthing@dronolab.service',
            'mavproxy@root.service']

picPathList = []


class FolderCheck(FileSystemEventHandler):
    def __init__(self, q):
        self.q = q

    def on_created(self, event):
        n = event.src_path.split('/')[-1]
        if n[0] == '1' and n.split('.')[-1] == 'jpg':
            picPathList.append(event.src_path)
            self.q.put(('tag',  event.src_path))


def everythings_gonna_be_alright():
    everythings_gonna_be_alright = False

    while everythings_gonna_be_alright != True:
        services_out = []
        for s in services:
            time.sleep(0.1)
            cmd = 'systemctl is-active {0} >/dev/null 2>&1 && echo True ' \
                  '|| echo False'.format(s)

            out = subprocess.Popen(cmd, shell=True,
                                   stdout=subprocess.PIPE).stdout.read()
            services_out.append(out)

            if out != "True\n":
                time.sleep(0.1)
                kill_pic = 'systemctl stop {0} >/dev/null 2>&1 && echo True ' \
                           '|| echo False'.format(services[0])
                subprocess.Popen(kill_pic, shell=True,
                                 stdout=subprocess.PIPE).stdout.read()
                print "A6000 LOOP AS BEEN KILL"

        if all(s == 'True\n' for s in services_out):
            time.sleep(0.1)
            go_pic = 'systemctl start {0} >/dev/null 2>&1 && echo True ' \
                     '|| echo False'.format(services[0])
            subprocess.Popen(go_pic, shell=True,
                             stdout=subprocess.PIPE).stdout.read()
            print "GO"
            everythings_gonna_be_alright = True

    return True


def start_master_photo(q, config):
    photo = Worker(q, config)
    photo.run()


if __name__ == '__main__':
    # everythings_gonna_be_alright()

    q = Queue()

    event = FolderCheck(q)
    observer = Observer()
    observer.schedule(event, path=config['PICTURE_PATH'], recursive=False)
    observer.start()

    p_photo = Process(target=start_master_photo, args=(q, config))
    p_photo.start()

    observer.join()
    p_photo.join()

    try:
        while True:
            print "GOOD"

    except KeyboardInterrupt:
        observer.stop()

    finally:
        print "DEAD"
