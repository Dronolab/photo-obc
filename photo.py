import sys
import time
from importlib import import_module
from modules.files import Files
from modules.time import FunctionTimer
from modules.db import Database

if __name__ == '__main__':
    env = sys.argv[1] if len(sys.argv) == 2 else 'default'
    config = import_module('conf.%s' % env).config

    db = Database(config)

    process_pictures = FunctionTimer(config['RATE'], Files, db, config)

try:
    while True:
        time.sleep(1000)

finally:
    process_pictures.stop()
