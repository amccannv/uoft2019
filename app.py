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

q = Queue()

frame_processed = 0
score_thresh = 0.2

app = Flask(__name__)

# Create a worker thread that loads graph and
# does detection on images in an input queue and puts it on an output queue

@app.route("/")
def hello():
    return 'hi'

@app.route("/movement", methods=['GET'])
def movement_score():
    score = q.get()
    print("SCORE", score)

    return jsonify(score=score)

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

def launch_webserver(que):
    global q
    q = que
    app.run(host='0.0.0.0', port=4018)

if __name__ == '__main__':

    input_q = Queue(maxsize=5)
    output_q = Queue(maxsize=5)

    video_capture = WebcamVideoStream(src=0, width=750, height=500).start()

    cap_params = {}
    frame_processed = 1
    cap_params['im_width'], cap_params['im_height'] = video_capture.size()
    cap_params['score_thresh'] = score_thresh

    # max number of hands we want to detect/track
    cap_params['num_hands_detect'] = 2

    # spin up workers to paralleize detection.
    pool = Pool(4, worker, (input_q, output_q, cap_params, frame_processed, q))

    start_time = datetime.datetime.now()
    num_frames = 0
    fps = 0
    index = 0

    cv2.namedWindow('Multi-Threaded Detection', cv2.WINDOW_NORMAL)

    # run web application
    Thread(target=launch_webserver, args=(q,)).start()

    while True:
        frame = video_capture.read()
        frame = cv2.flip(frame, 1)
        index += 1

        input_q.put(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        output_frame = output_q.get()

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
    pool.terminate()
    video_capture.stop()
    cv2.destroyAllWindows()
