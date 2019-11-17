#! /usr/bin/env python

import warnings
import json
warnings.filterwarnings("ignore")

from dejavu import Dejavu
from dejavu.recognize import FileRecognizer#, MicrophoneRecognizer

# before starting, ensure that:
#   MySQL server is up
#   database in config.SAMPLE is present

# load config from a JSON file
with open("config.SAMPLE") as f:
  config = json.load(f)

djv = Dejavu(config)

# Dejavu.fingerprint_directory for audio in a specified path
# Dejavu.fingerprint_file for audio files


djv.fingerprint_file("test_audio/jok.wav")
djv.fingerprint_file("test_audio/mac.wav")

song = djv.recognize(FileRecognizer, "test_audio/jok.wav")
if song is None:
  print "Nothing recognized :(\n"
else:
  print "We recognized %s\n" % (song)
# Useful MySQL commands which could be used a lot soon
# show databases;
# use <db_name>;
# drop database <db_name>;
# create database if not exists <db_name>;
# show tables;
# select <table_entry> from <table>
# delete from <table> where <condition>