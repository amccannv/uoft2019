#!/usr/bin/env python

# Copyright 2017 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Google Cloud Speech API sample application using the streaming API.
NOTE: This module requires the additional dependency `pyaudio`. To install
using pip:
    pip install pyaudio
Example usage:
    python transcribe_streaming_mic.py
"""

# [START speech_transcribe_streaming_mic]
from __future__ import division

import re
import sys
import json
import subprocess

from google.cloud import speech
from google.cloud.speech import enums
from google.cloud.speech import types
import pyaudio
from six.moves import queue

from microphoneStream import MicrophoneStream

# Audio recording parameters
RATE = 16000
CHUNK = int(RATE / 10)  # 100ms
CRUTCH_WORDS = ['basically', 'really', 'like', 'actually', 'very', 'literally', 'stuff', 'things', 'obviously', 'yeah']

class SpeechHandler(object):
    def listen_print_loop(self, responses):
        """Iterates through server responses and prints them.
        The responses passed is a generator that will block until a response
        is provided by the server.
        Each response may contain multiple results, and each result may contain
        multiple alternatives; for details, see https://goo.gl/tjCPAU.  Here we
        print only the transcription for the top alternative of the top result.
        In this case, responses are provided for interim results as well. If the
        response is an interim one, print a line feed at the end of it, to allow
        the next result to overwrite it, until the response is a final one. For the
        final one, print a newline to preserve the finalized transcription.
        """
        num_chars_printed = 0
        for response in responses:
            if not response.results:
                continue

            # The `results` list is consecutive. For streaming, we only care about
            # the first result being considered, since once it's `is_final`, it
            # moves on to considering the next utterance.
            result = response.results[0]
            if not result.alternatives:
                continue

            # Display the transcription of the top alternative.
            transcript = result.alternatives[0].transcript

            # Display interim results, but with a carriage return at the end of the
            # line, so subsequent lines will overwrite them.
            #
            # If the previous result was longer than this one, we need to print
            # some extra spaces to overwrite the previous result
            overwrite_chars = ' ' * (num_chars_printed - len(transcript))

            if not result.is_final:
                sys.stdout.write(transcript + overwrite_chars + '\r')
                sys.stdout.flush()

                num_chars_printed = len(transcript)

            else:
                print(transcript + overwrite_chars)

                # Exit recognition if any of the transcribed phrases could be
                # one of our keywords.
                with open('scores.txt', 'r') as f:
                    lines = f.read().splitlines()
                    line = lines[-1]
                # self._socket.emit('newnumber', {'number': line}, namespace='/test')

                if re.search(r'\b(exit|quit)\b', transcript, re.I):
                    print('Exiting..')
                    with open('audio_summary.json', 'w') as outfile:
                        json.dump(self._json_summary, outfile)
                    break

                num_chars_printed = 0

    def fillerStats(self, transcript):
        crutch_word_count = 0
        for word in CRUTCH_WORDS:
            crutch_word_count = crutch_word_count + transcript.count(word)
            self._json_summary['counts'][word] += transcript.count(word)

        self._json_summary['transcript'] = self._json_summary['transcript'] + transcript
        self._json_summary['crutch_count_by_line'].append(crutch_word_count)
        self._json_summary['wpm_by_line'].append(0)

        return crutch_word_count / len(transcript.split()) * 100

    def __init__(self):
        # See http://g.co/cloud/speech/docs/languages
        # for a list of supported languages.
        self._json_summary = {'transcript': '',
                              'crutch_count_by_line': [],
                              'wpm_by_line': [],
                              'counts': {'basically': 0, 'really': 0, 'like': 0, 'actually': 0, 'very': 0, 'literally': 0, 'stuff': 0, 'things': 0, 'obviously': 0, 'yeah': 0}
                              }
        language_code = 'en-US'  # a BCP-47 language tag

        client = speech.SpeechClient()
        config = types.RecognitionConfig(
            encoding=enums.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=RATE,
            language_code=language_code)
        streaming_config = types.StreamingRecognitionConfig(
            config=config,
            interim_results=True)

        with MicrophoneStream(RATE, CHUNK) as stream:
            audio_generator = stream.generator()
            requests = (types.StreamingRecognizeRequest(audio_content=content)
                        for content in audio_generator)

            responses = client.streaming_recognize(streaming_config, requests)

            # Now, put the transcription responses to use.
            try:
                self.listen_print_loop(responses)
            except Exception as exception:
                print(exception)