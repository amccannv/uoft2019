from threading import Thread, Event
from multiprocessing import Pool

from flask import Flask, render_template

from speech import SpeechHandler
from vision import VisionHandler

app = Flask(__name__)
app.config['DEBUG'] = True

speech_thread = Thread()
speech_thread_stop_event = Event()

vision_thread = Thread()
vision_thread_stop_event = Event()

class SpeechThread(Thread):
    def __init__(self):
        self.delay = 1
        super(SpeechThread, self).__init__()

    def run(self):
        SpeechHandler()

class VisionThread(Thread):
    def __init__(self):
        self.delay = 1
        super(VisionThread, self).__init__()

    def run(self):
        VisionHandler()

@app.route('/', methods=['POST'])
def index():
    return render_template('index.html')

@app.route('/start', methods=['POST'])
def start():
    global speech_thread
    global vision_thread

    if not speech_thread.isAlive():
        print("Starting Speech Thread")
        speech_thread = SpeechThread()
        speech_thread.start()
    if not vision_thread.isAlive():
        print("Starting Vision Thread")
        vision_thread = VisionThread()
        vision_thread.start()

    return "Started Threads"

@app.route('/stop', methods=['POST'])
def stop():
    global speech_thread
    global vision_thread

    if speech_thread.isAlive():
        print("Stopping Speech Thread")
        speech_thread.stop()
    if vision_thread.isAlive():
        print("Stopping Vision Thread")
        vision_thread.stop()

    return "Stopped Threads"

if __name__ == '__main__':
    app.run(host='0.0.0.0')
