# from flask_socketio import SocketIO, emit
from flask import Flask, render_template, url_for, copy_current_request_context
from random import random
from time import sleep
from threading import Thread, Event
import subprocess
import multiprocessing
from multiprocessing import Queue, Pool

from speech import SpeechHandler
from vision import VisionHandler

app = Flask(__name__)
app.config['DEBUG'] = True

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
    
    if not speech_thread.isAlive():
        print("Starting Thread")
        speech_thread = SpeechThread()
        speech_thread.start()
    if not vision_thread.isAlive():
        print("Starting Thread")
        vision_thread = VisionThread()
        vision_thread.start()

@app.route('/stop')
def stop():
    print('hold')
    # stop logic
    # render summary

if __name__ == '__main__':
    app.run(host='0.0.0.0')
