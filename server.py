from flask import Flask, render_template, request, jsonify

app = Flask(__name__, template_folder='./templates')


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/stop_pic')
def stop():
    print("b")
    #app.q.put(('stop',))
    return jsonify({})


@app.route('/start_pic')
def open():
    print("a")
    #app.q.put(('pwm', 100, int(duration_minutes)))
    return jsonify({})

def setup(q):
    app.q = q
    return app