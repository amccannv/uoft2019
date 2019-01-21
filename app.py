from threading import Thread, Event
from multiprocessing import Pool
import os
from time import time, sleep
from datetime import datetime, timedelta
import json

from flask import Flask, render_template, redirect, url_for, jsonify

from speech import SpeechHandler
from vision import VisionHandler

app = Flask(__name__)
app.config['DEBUG'] = True
credential_path = "./UofT2019-37c5ae888676.json"
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credential_path

speech_thread = Thread()
speech_thread_stop_event = Event()

vision_thread = Thread()
vision_thread_stop_event = Event()

start_time = time()

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

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/start', methods=['POST'])
def start():
    global speech_thread
    global vision_thread
    global start_time

    if not speech_thread.isAlive():
        print("Starting Speech Thread")
        speech_thread = SpeechThread()
        speech_thread.start()

    if not vision_thread.isAlive():
        print("Starting Vision Thread")
        vision_thread = VisionThread()
        vision_thread.start()

    return "Started Threads"

@app.route('/summary/', methods=['GET'])
def summary():
    with open('audio_summary.json') as f:
        data = json.load(f)
    scores = []
    with open('scores.txt') as f:
        for score in f:
            if int(float(score.strip())) != 0:
                scores.append(score)
    data['scores'] = scores
    return render_template('summary.html', data=data)

@app.route('/current', methods=['GET'])
def current():
    global start_time

    with open('audio_summary.json') as f:
        data = json.load(f)
    scores = []
    with open('scores.txt') as f:
        for score in f:
            if int(float(score.strip())) != 0:
                scores.append(score)
    data['scores'] = scores
    data['wpm_by_line'].append(len(data['transcript'][-1].split()) / (time() - start_time))
    start_time = time()
    return jsonify(data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
