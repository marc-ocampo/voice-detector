#! /usr/bin/env python

import warnings
import json
warnings.filterwarnings("ignore")

from dejavu import Dejavu
from dejavu.recognize import FileRecognizer

# load config from a JSON file
with open("config.SAMPLE") as f:
  config = json.load(f)

djv = Dejavu(config)

def train():
  print "====================== Training ======================"
  print "Only supports WAV and MP3 sample files"
  path = raw_input("Path of samples (e.g. test_audio\\): ")
  djv.fingerprint_directory(path, [".mp3", ".wav"])
  #djv.fingerprint_file(single_audio_file)  
  print "======================================================"

def recognize():
  print "==================== Recognition ====================="
  file = raw_input("File to recognize: ")
  song = djv.recognize(FileRecognizer, file)
  if song is None:
    print "Can't find in the database :(\n"
  else:
    print "We recognized %s\n" % (song)
  print "======================================================"

def process_user_choice(user_choice):
  if 'a' == user_choice:
    train()
  elif 'b' == user_choice:
    recognize()
  elif 'c' == user_choice:
    print "Please consider donating to continue this application"
  else:
    print "Unexpected user input"

def main_function():
  user_input = None
  while 'c' != user_input :
    print "====================== Voice Detector ======================"
    print "[a] Train"
    print "[b] Recognize"
    print "[c] Quit"
    print "============================================================"
    choice = raw_input("Select your option: ")
    user_input = choice.lower()
    process_user_choice(user_input)
    print "============================================================"

if __name__ == '__main__':
  main_function()