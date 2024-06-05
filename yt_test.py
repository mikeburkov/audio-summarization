from pytube import YouTube
import ffmpy
import os
import subprocess
import json
import sys
import datetime
import time
import re
import requests
import spacy
from language_tool_python import LanguageTool



# load spaCy model
nlp = spacy.load('en_core_web_sm')

# Initialize LanguageTool with error handling
try:
    tool = LanguageTool('en-US')
except Exception as e:
    print(f"Error initializing LanguageTool: {e}")
    exit(1)

def clean_transcript(transcript):

    # basic cleaning with spaCy
    doc = nlp(transcript)
    cleaned_text = " ".join([token.text for token in doc if not token.is_space])

    # grammar and spelling correction with LanguageTool
    return tool.correct(cleaned_text)


print(sys.argv)
yt = YouTube(sys.argv[1])
print (yt.title)
print('Duration: '+ str(round(yt.length/60)) + 'min')
stream = yt.streams.filter(only_audio=True).first()
stream.download(filename='audio.mp4')
ff = ffmpy.FFmpeg(inputs={'audio.mp4': None},
                  outputs={'audio.wav': '-ar 16000 -ac 1 -c:a pcm_s16le'})
ff.run()

now = datetime.datetime.now()
date_time_str = now.strftime("%Y%m%d-%H%M%S-%f")
transcribed_json = 'youtube_transcribed_' + date_time_str + ".json"
transcribed_json_main = 'youtube_transcribed_' + date_time_str

audio_file = 'audio.wav'
audio_file_mp4 = 'audio.mp4'
# with speaker segmentation turned on https://github.com/ggerganov/whisper.cpp?tab=readme-ov-file#speaker-segmentation-via-tinydiarize-experimental
subprocess.run(["/Users/mikeburkov/whisper.cpp/main", "-d", "100000", "-oj", "--output-file", transcribed_json_main, "-m", "/Users/mikeburkov/whisper.cpp/models/ggml-small.en-tdrz.bin", "-tdrz", "--split-on-word", audio_file])

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
    scrubbed_text = clean_transcript(re.sub(pattern, '', x['text']))
    speaker = '[' + speakers[0] + ']'
    output_file.write(f'{speaker}, {scrubbed_text}\n\n')
output_file.close()

# Clean up by removing the recorded audio file
if os.path.exists(audio_file):
    os.remove(audio_file)
if os.path.exists(transcribed_json):
    os.remove(transcribed_json)
if os.path.exists(audio_file_mp4):
    os.remove(audio_file_mp4)


