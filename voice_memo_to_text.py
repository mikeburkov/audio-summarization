from pytube import YouTube
import ffmpy
import os
import subprocess
import sys
import json
import datetime
import time
import re


input_file = sys.argv[1]


ff = ffmpy.FFmpeg(inputs={input_file: None},
                  outputs={'voice_memo.wav': '-ar 16000 -ac 1 -c:a pcm_s16le'})
ff.run()


now = datetime.datetime.now()
date_time_str = now.strftime("%Y%m%d-%H%M%S-%f")
transcribed_json = 'voice_memo_transcribed_' + date_time_str + ".json"
transcribed_json_main = 'voice_memo_transcribed_' + date_time_str

audio_file = 'voice_memo.wav'
# with speaker segmentation turned on https://github.com/ggerganov/whisper.cpp?tab=readme-ov-file#speaker-segmentation-via-tinydiarize-experimental
subprocess.run(["/Users/mikeburkov/whisper.cpp/main","-oj", "--output-file", transcribed_json_main, "-m", "/Users/mikeburkov/whisper.cpp/models/ggml-small.en-tdrz.bin", "-tdrz", "--split-on-word", audio_file])

input_file = open(transcribed_json, 'r')
output_file = open('output_' + date_time_str + ".txt", 'w')
data = json.load(input_file)
transcript = data['transcription']
#formatted_json = json.dumps(text, indent=2)
speakers = ['Speaker 1', 'Speaker 2']
pattern = r'\b[Uu][mh]\b'
for x in transcript:
    if bool(x['speaker_turn_next']):
        speakers.reverse()
    scrubbed_text = re.sub(pattern, '', x['text'])
    speaker = '[' + speakers[0] + ']'
    print(speaker, scrubbed_text)
    output_file.write(f'{speaker}, {scrubbed_text}\n\n')
output_file.close()


# Clean up by removing the recorded audio file
if os.path.exists(audio_file):
    os.remove(audio_file)
if os.path.exists(transcribed_json):
    os.remove(transcribed_json)

