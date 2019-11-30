import json
import warnings
import os.path
import MySQLdb
import time

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
    self.training_path = 'files/train'
    self.options = {'a': self.__train_model,
                    'b': self.__recognize,
                    'c': self.__delete_model,
                    'd':self.__quit}

    self.__read_config_file()
    if self.read_config_file_successful:
      self.djv = Dejavu(self.config)

    print "Voice Matching Application -- make a better name?"
    print "Hello %s!" % name

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

  def run(self):
    if self.read_config_file_successful:
      self.__run_the_loop()
    else:
      pass

  def __run_the_loop(self):
    while self.__wants_to_continue():
      self.__ask_from_user()
      self.__assess_choice()

  def __train_model(self):
    print "Training voice models stored in /files/training/"
    start_time = time.time()
    self.djv.fingerprint_directory(self.training_path, [".wav", ".mp3"])
    end_time = time.time()
    print "Training took %f seconds" % (end_time - start_time)

  def __recognize(self):
    print "Recognize from file"
    self.__get_file_to_recognize_from_user()

    if self.file_to_recognize_is_valid :
      self.__recognize_voice()

  def __get_file_to_recognize_from_user(self):
    self.file = raw_input("File to recognize: ")

    if os.path.isfile(self.file):
      self.file_to_recognize_is_valid = True
    else:
      self.file_to_recognize_is_valid = False
      print "Unable to find the file."
      # known issue where '/' must be used in directories, unable to use '\'
      print "[known issue] Please use '/' as directory delimiter."

  def __recognize_voice(self):
    search = self.djv.recognize(FileRecognizer, self.file)

    if search is None:
      print "Unable to recognize the voice"
    else:
      print "The application recognized you, %s!" % self.name

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

  def __ask_from_user(self):
    print ""
    print "[a] Train a voice model"
    print "[b] Recognize voice"
    print "[c] Delete stored voice model"
    print "[d] Quit"
    self.choice = raw_input("Select your option: ")
    self.choice = self.choice.lower()
    print ""

  def __assess_choice(self):
    try:
      self.options[self.choice]()
    except Exception:
      pass # no need to show warnings

  def __wants_to_continue(self):
    return 'd' != self.choice