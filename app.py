from flask_socketio import SocketIO, emit
from flask import Flask, render_template, url_for, copy_current_request_context
from random import random
from time import sleep
from threading import Thread, Event
import subprocess

from speech import SpeechHandler
from vision import VisionHandler

app = Flask(__name__)
app.config['DEBUG'] = True

# turn the flask app into a socketio app
socketio = SocketIO(app)

# audio thread
speech_thread = Thread()
speech_thread_stop_event = Event()

class SpeechThread(Thread):
    def __init__(self):
        self.delay = 1
        super(SpeechThread, self).__init__()

    # def speechStreaming(self):

    #     while not speech_thread_stop_event.isSet():
    #         number = round(random()*10, 3)
    #         print(number)
    #         socketio.emit('newnumber', {'number': number}, namespace='/test')
    #         sleep(self.delay)

    def run(self):
        SpeechHandler(socketio)

vision_thread = Thread()
vision_thread_stop_event = Event()

class VisionThread(Thread):
    def __init__(self):
        self.delay = 1
        super(VisionThread, self).__init__()

    # def speechStreaming(self):

    #     while not speech_thread_stop_event.isSet():
    #         number = round(random()*10, 3)
    #         print(number)
    #         socketio.emit('newnumber', {'number': number}, namespace='/test')
    #         sleep(self.delay)

    def run(self):
        VisionHandler()


@app.route('/')
def index():
    #only by sending this page first will the client be connected to the socketio instance
    return render_template('index.html')

@socketio.on('connect', namespace='/test')
def test_connect():
    # need visibility of the global thread object
    global speech_thread
    global vision_thread
    print('Client connected')

    #Start the random number generator thread only if the thread has not been started before.
    # if not speech_thread.isAlive():
    #     print("Starting Thread")
    #     speech_thread = SpeechThread()
    #     speech_thread.start()
    if not vision_thread.isAlive():
        print("Starting Thread")
        vision_thread = VisionThread()
        vision_thread.start()

@socketio.on('disconnect', namespace='/test')
def test_disconnect():
    print('Client disconnected')


if __name__ == '__main__':
    socketio.run(app)