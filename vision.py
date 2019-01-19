from utils import detector_utils as detector_utils
import cv2
import tensorflow as tf
import multiprocessing
from multiprocessing import Queue, Pool
import time
from utils.detector_utils import WebcamVideoStream
import datetime
import argparse
from threading import Thread

from flask import Flask, request, jsonify

# app = Flask(__name__)

# # Create a worker thread that loads graph and
# # does detection on images in an input queue and puts it on an output queue

# @app.route("/")
# def hello():
#     return 'hi'

# @app.route("/movement", methods=['GET'])
# def movement_score():
#     score = q.get()
#     print("SCORE", score)

#     return jsonify(score=score)

def worker(input_q, output_q, cap_params, frame_processed, q):
    print(">> loading frozen model for worker")
    detection_graph, sess = detector_utils.load_inference_graph()
    sess = tf.Session(graph=detection_graph)
    ret1 = 0
    ret2 = 0
    while True:
        #print("> ===== in worker loop, frame ", frame_processed)
        frame = input_q.get()
        if (frame is not None):
            # Actual detection. Variable boxes contains the bounding box cordinates for hands detected,
            # while scores contains the confidence for each of these boxes.
            # Hint: If len(boxes) > 1 , you may assume you have found atleast one hand (within your score threshold)

            boxes, scores = detector_utils.detect_objects(
                frame, detection_graph, sess)
            # draw bounding boxes

            ret = detector_utils.draw_box_on_image(
                0, cap_params["score_thresh"],
                scores, boxes, cap_params['im_width'], cap_params['im_height'], frame, frame_processed)


            if ret is not None:
                ret1 = ret

            ret = detector_utils.draw_box_on_image(
                1, cap_params["score_thresh"],
                scores, boxes, cap_params['im_width'], cap_params['im_height'],
                frame, frame_processed)

            if ret is not None:
                ret2 = ret

            score = (ret1 + ret2)/2
            if ret is not None:
                print(score, q.get())
            q.put(score)
            # print(q.get())
            # add frame annotated with bounding box to queue
            output_q.put(frame)
            frame_processed += 1
        else:
            output_q.put(frame)
    sess.close()

# def launch_webserver(que):
#     global q
#     q = que
#     app.run(host='0.0.0.0', port=4018)

class VisionHandler(object):
    def __init__(self):
        q = Queue()

        frame_processed = 0
        score_thresh = 0.2
        
        self._input_q = Queue(maxsize=5)
        self._output_q = Queue(maxsize=5)

        video_capture = WebcamVideoStream(src=0, width=750, height=500).start()

        cap_params = {}
        frame_processed = 1
        cap_params['im_width'], cap_params['im_height'] = video_capture.size()
        cap_params['score_thresh'] = score_thresh

        # max number of hands we want to detect/track
        cap_params['num_hands_detect'] = 2

        # spin up workers to paralleize detection.
        self._pool = Pool(4, worker, (self._input_q, self._output_q, cap_params, frame_processed, q))

        


        cv2.namedWindow('Multi-Threaded Detection', cv2.WINDOW_NORMAL)

        self.detection_loop(video_capture)

    def detection_loop(self, video_capture):
        num_frames = 0
        fps = 0
        index = 0
        start_time = datetime.datetime.now()

        while True:
            frame = video_capture.read()
            frame = cv2.flip(frame, 1)
            index += 1

            self._input_q.put(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            output_frame = self._output_q.get()
            output_frame = cv2.cvtColor(output_frame, cv2.COLOR_RGB2BGR)

            elapsed_time = (datetime.datetime.now() - start_time).total_seconds()
            num_frames += 1
            fps = num_frames / elapsed_time

            if output_frame is not None:
                detector_utils.draw_fps_on_image("FPS : " + str(int(fps)), output_frame)
                cv2.imshow('Multi-Threaded Detection', output_frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            else:
                break
        elapsed_time = (datetime.datetime.now() - start_time).total_seconds()
        fps = num_frames / elapsed_time
        self._pool.terminate()
        video_capture.stop()
        cv2.destroyAllWindows()