import sys
import time
import imp

f_files = imp.find_module('files', ['./modules/'])
files = imp.load_module('files', *f_files)

f_timer = imp.find_module('timer', ['./modules/'])
timer = imp.load_module('timer', *f_timer)

a_db = imp.find_module('db', ['./modules/'])
db = imp.load_module('db', *a_db)

env = sys.argv[1] if len(sys.argv) == 2 else 'default'
a_conf = imp.find_module('default', ['./config/'])
conf = imp.load_module('default', *a_conf)

from files import Files
from timer import FunctionTimer
from db import Database
from default import config


if __name__ == '__main__':

    db = Database(config)

    process_pictures = FunctionTimer(config['RATE'], Files, db, config)

try:
    while True:
        time.sleep(1000)

finally:
    process_pictures.stop()
