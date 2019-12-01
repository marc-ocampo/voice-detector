import json
import warnings
import os.path
import MySQLdb
import time
import shutil
import pyaudio
import wave

from dejavu import Dejavu
from dejavu.recognize import FileRecognizer

warnings.filterwarnings("ignore") # warnings if DB is already populated

class VoiceMatcher(object):

  def __init__(self, name):
    # UI Parameters
    self.name = name
    self.choice = None
    self.config = None
    self.training_path_file = 'files/train/'
    self.training_path_mic = '/tmp/train/'
    self.options = {'a': self.__train_model_from_file,
                    'b': self.__train_model_from_mic,
                    'c': self.__recognize_from_file,
                    'd': self.__recognize_from_mic,
                    'e': self.__delete_model,
                    'f':self.__quit}
    # PyAudio parameters
    self.format = pyaudio.paInt16
    self.channels = 2
    self.rate = 44100 # Mhz
    self.chunk = 1024
    self.record_length_s = 5

    self.__read_config_file()
    self.__create_folder_for_models_from_mic()
    self.__word_art()
    print "Hello %s!" % name

  def __ask_from_user(self):
    print ""
    print "[a] Train voice models from file."
    print "[b] Train voice model from mic. [NOT YET SUPPORTED]"
    print "[c] Recognize voice from file."
    print "[d] Recognize voice from mic. [NOT YET SUPPORTED]"
    print "[e] Delete stored voice model."
    print "[f] Quit."
    self.choice = raw_input("Select your option: ")
    self.choice = self.choice.lower()
    print ""

  def __wants_to_continue(self):
    return 'f' != self.choice

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

  def __create_folder_for_models_from_mic(self):
    if not os.path.exists(self.training_path_mic):
      os.makedirs(self.training_path_mic)

  def __remove_folder_for_models_from_mic(self):
    if os.path.exists(self.training_path_mic):
      shutil.rmtree(self.training_path_mic)

  def __train_model_from_file(self):
    print "Train Voice Models from Files"
    print "Training voice models stored in /files/training/."
    start_time = time.time()
    self.djv.fingerprint_directory(self.training_path_file, [".wav", ".mp3"])
    end_time = time.time()
    print "Training took %f seconds" % (end_time - start_time)

  def __train_model_from_mic(self):
    print "Train Voice Model from Mic"


  def __recognize_from_file(self):
    print "Recognize from File"
    self.file = raw_input("File to recognize: ")
    self.__recognize()

  def __recognize(self):
    if self.__check_recognition_file_validity() :
      self.__recognize_voice()
    else:
      print "Recognition file %s is invalid" % (self.file)

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
    print "Recognize from Mic"
    self.file = "/tmp/temp.wav"
    self.__record_using_mic()
    self.__recognize()

    # delete the temporary file
    if os.path.isfile(self.file):
      os.remove(self.file)
    else:
      pass

  def __record_using_mic(self):
    audio = pyaudio.PyAudio()

    # start Recording
    stream = audio.open(format=self.format, channels=self.channels,
                    rate=self.rate, input=True,
                    frames_per_buffer=self.chunk)
    print "Say your key phrase using the microphone."
    frames = []

    for i in range(0, int(self.rate / self.chunk * self.record_length_s)):
        data = stream.read(self.chunk)
        frames.append(data)
    #print "finished recording"

    # stop Recording
    stream.stop_stream()
    stream.close()
    audio.terminate()
    print "Voice model to recognize obtained from the user."

    # Saving the file
    temp_file = wave.open(self.file, 'wb')
    temp_file.setnchannels(self.channels)
    temp_file.setsampwidth(audio.get_sample_size(self.format))
    temp_file.setframerate(self.rate)
    temp_file.writeframes(b''.join(frames))
    temp_file.close()

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
    self.__remove_folder_for_models_from_mic() # for cleanup

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