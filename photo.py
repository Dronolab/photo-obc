import sys
import time
import imp
import subprocess

f_files = imp.find_module('files', ['./modules/'])
files = imp.load_module('files', *f_files)

a_db = imp.find_module('db', ['./modules/'])
db = imp.load_module('db', *a_db)

env = sys.argv[1] if len(sys.argv) == 2 else 'default'
a_conf = imp.find_module('default', ['./config/'])
conf = imp.load_module('default', *a_conf)

from files import Files
from db import Database
from default import config

services = ['photo@root.service',
           'mongodb.service',
           'syncthing@dronolab.service',
           'mavproxy@root.service']

def everythings_gonna_be_alright():
    everythings_gonna_be_alright = False

    while everythings_gonna_be_alright != True:
        print everythings_gonna_be_alright
        services_out = []
        for s in services:
            time.sleep(0.1)
            cmd = 'systemctl is-active {0} >/dev/null 2>&1 && echo True || echo False'.format(s)

            out = subprocess.Popen(cmd, shell=True,
                                   stdout=subprocess.PIPE).stdout.read()
            services_out.append(out)

            if out != "True\n":
                 time.sleep(0.1)
                 kill_pic = 'systemctl stop {0} >/dev/null 2>&1 && echo True || echo False'.format(services[0])
                 subprocess.Popen(kill_pic, shell=True,
                                  stdout=subprocess.PIPE).stdout.read()
                 print "A6000 LOOP AS BEEN KILL"


        if all(s=='True\n' for s in services_out):
            time.sleep(0.1)
            go_pic = 'systemctl start {0} >/dev/null 2>&1 && echo True || echo False'.format(services[0])
            subprocess.Popen(go_pic, shell=True,
                                   stdout=subprocess.PIPE).stdout.read()
            print "GO"
            everythings_gonna_be_alright = True

    return True


if __name__ == '__main__':
    everythings_gonna_be_alright()

    db = Database(config)

    process_pictures = Files(db, config)

try:
    while True:
        time.sleep(1000)

finally:
    process_pictures.stop()
