from __future__ import print_function

import time, os

with open('/var/tmp/mavproxy-run.log', 'a') as fp:
    print(time.time(), 'SERVICE[START]: mavproxy.py', file=fp)
    os.system("nohup mavproxy.py &")
