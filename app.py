# from flask_socketio import SocketIO, emit
from flask import Flask, render_template, url_for, copy_current_request_context
from random import random
from time import sleep
from threading import Thread, Event
import subprocess
import multiprocessing
from multiprocessing import Queue, Pool
import os

from speech import SpeechHandler
from vision import VisionHandler

app = Flask(__name__)
app.config['DEBUG'] = True
credential_path = "./UofT2019-37c5ae888676.json"
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credential_path

speech_thread = Thread()
speech_thread_stop_event = Event()

class SpeechThread(Thread):
    def __init__(self):
        self.delay = 1
        super(SpeechThread, self).__init__()

    def run(self):
        SpeechHandler()

vision_thread = Thread()
vision_thread_stop_event = Event()

class VisionThread(Thread):
    def __init__(self):
        self.delay = 1
        super(VisionThread, self).__init__()

    def run(self):
        VisionHandler()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start')
def start():
    global speech_thread
    global vision_thread
<<<<<<< HEAD
    print('Client connected')

    # #Start the random number generator thread only if the thread has not been started before.
=======
    
>>>>>>> c71ff6c4cb8f451fdda75d455ac74ed6c01048ce
    if not speech_thread.isAlive():
        print("Starting Thread")
        speech_thread = SpeechThread()
        speech_thread.start()
<<<<<<< HEAD
    # if not vision_thread.isAlive():
    #     print("Starting Thread")
    #     vision_thread = VisionThread()
    #     vision_thread.start()

@socketio.on('disconnect', namespace='/test')
def test_disconnect():
    print('Client disconnected')
=======
    if not vision_thread.isAlive():
        print("Starting Thread")
        vision_thread = VisionThread()
        vision_thread.start()

@app.route('/stop')
def stop():
    print('hold')
    # stop logic
    # render summary
>>>>>>> c71ff6c4cb8f451fdda75d455ac74ed6c01048ce

if __name__ == '__main__':
    app.run(host='0.0.0.0')
