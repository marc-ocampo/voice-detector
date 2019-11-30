import json
import warnings
import os.path
import MySQLdb
import time
import pyaudio
import wave

from dejavu import Dejavu
from dejavu.recognize import FileRecognizer

warnings.filterwarnings("ignore") # warnings if DB is already populated

# train from mic not yet supported
# recognize from mic not yet supported
class VoiceMatcher(object):

  def __init__(self, name):
    self.name = name
    self.choice = None
    self.config = None
    self.recog_mic_count = 0
    self.training_path = 'files/train/'
    self.options = {'a': self.__train_model,
                    'b': self.__recognize_from_file,
                    'c': self.__recognize_from_mic,
                    'd': self.__delete_model,
                    'e':self.__quit}

    self.__read_config_file()
    self.__word_art()
    print "Hello %s!" % name

  def __ask_from_user(self):
    print ""
    print "[a] Train a voice model"
    print "[b] Recognize voice from file"
    print "[c] Recognize voice from mic"
    print "[d] Delete stored voice model"
    print "[e] Quit"
    self.choice = raw_input("Select your option: ")
    self.choice = self.choice.lower()
    print ""

  def __wants_to_continue(self):
    return 'e' != self.choice

  def __assess_choice(self):
    try:
      self.options[self.choice]()
    except Exception:
      pass # no need to show warnings

  def run(self):
    if self.read_config_file_successful:
      self.__run_the_loop()
    else:
      pass

  def __run_the_loop(self):
    while self.__wants_to_continue():
      self.__ask_from_user()
      self.__assess_choice()

  def __read_config_file(self):
    try:
      f = open("config.DEFAULT")
      self.config = json.load(f)
      self.read_config_file_successful = True

    except Exception:
      print "Unable to find the configuration file."
      print "Please ensure config.DEFAULT file in the same directory."
      print "Check the sample file in ext/dejavu/dejavu.cnf.SAMPLE."
      self.read_config_file_successful = False

    if self.read_config_file_successful:
      self.djv = Dejavu(self.config)

  def __train_model(self):
    print "Training voice models stored in /files/training/"
    start_time = time.time()
    self.djv.fingerprint_directory(self.training_path, [".wav", ".mp3"])
    end_time = time.time()
    print "Training took %f seconds" % (end_time - start_time)

  def __recognize_from_file(self):
    print "Recognize from file"
    self.file = raw_input("File to recognize: ")

    #self.__get_file_to_recognize_from_user()

    if self.__check_recognition_file_validity() :
      self.__recognize_voice()

  def __check_recognition_file_validity(self):
    if os.path.isfile(self.file):
      return True
    else:
      print "Unable to find the file."
      # known issue where '/' must be used in directories, unable to use '\'
      print "[known issue] Please use '/' as directory delimiter."
      return False

  def __recognize_voice(self):
    search = self.djv.recognize(FileRecognizer, self.file)

    if search is None:
      print "Unable to recognize the voice"
    else:
      print "The application recognized you, %s!" % self.name

  def __recognize_from_mic(self):

    FORMAT = pyaudio.paInt16
    CHANNELS = 2
    RATE = 44100
    CHUNK = 1024
    RECORD_SECONDS = 5
    WAVE_OUTPUT_FILENAME = "file.wav"

    print "instance created"
    audio = pyaudio.PyAudio()

    # start Recording
    stream = audio.open(format=FORMAT, channels=CHANNELS,
                    rate=RATE, input=True,
                    frames_per_buffer=CHUNK)
    print "recording..."
    frames = []

    for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)
    print "finished recording"

    # stop Recording
    stream.stop_stream()
    stream.close()
    audio.terminate()

    print "saving file"
    waveFile = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
    waveFile.setnchannels(CHANNELS)
    waveFile.setsampwidth(audio.get_sample_size(FORMAT))
    waveFile.setframerate(RATE)
    waveFile.writeframes(b''.join(frames))
    waveFile.close()

    # find the file
    self.file = WAVE_OUTPUT_FILENAME;
    if self.__check_recognition_file_validity() :
      print 'checking validity'
      self.__recognize_voice()
    else:
      print 'issue'
    # delete the file

    self.recog_mic_count += 1;

  def __delete_model(self):
    dbconfig = self.config['database']
    try:
      db = MySQLdb.connect(dbconfig['host'], dbconfig['user'], dbconfig['passwd'], dbconfig['db'])
      cur = db.cursor()
      cur.execute("delete from songs where song_id>0")
      db.commit()
      db.close()
      print "Deleted all fingerprints."
      print "[known issue] Please close the application to reflect the deletion in the storage."
      # known issue where the application must be closed before the elements in the DB are actually deleted
    except Exception:
      print "Unable to delete all fingerprints"

  def __quit(self):
    print "Please consider donating to continue this application."

  def __word_art(self):
    """
    Word art obtained from http://www.patorjk.com/software/taag/
    """
    print """
     __      __   _            __  __       _       _
     \ \    / /  (_)          |  \/  |     | |     | |
      \ \  / /__  _  ___ ___  | \  / | __ _| |_ ___| |__   ___ _ __
       \ \/ / _ \| |/ __/ _ \ | |\/| |/ _` | __/ __| '_ \ / _ \ '__|
        \  / (_) | | (_|  __/ | |  | | (_| | || (__| | | |  __/ |
         \/ \___/|_|\___\___| |_|  |_|\__,_|\__\___|_| |_|\___|_|
    """