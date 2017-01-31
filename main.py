#!/usr/bin/env python3
from multiprocessing import Process, Queue
from subprocess import Popen, PIPE
from photo import Photo
import server

def start_flask_app(app):
    app.run(debug=True, port=8880, host='0.0.0.0')

def start_photo(q):
    photo = Photo(q)
    photo.run()

if __name__ == '__main__':
    q = Queue()
    flask_app = server.setup(q)

    print('Starting Flask application')
    p_flask = Process(target=start_flask_app, args=(flask_app,))
    p_flask.start()

    print('Starting Photo process')
    p_photo = Process(target=start_photo, args=(q,))
    p_photo.start()
    p_photo.join()