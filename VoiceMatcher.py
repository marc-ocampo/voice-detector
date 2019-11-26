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
    self.training_path = 'files/training'
    self.options = {'a': self.train_model,
                    'b': self.recognize,
                    'c': self.delete_model,
                    'd':self.quit}

    self.read_config_file()
    if self.read_config_file_successful:
      self.djv = Dejavu(self.config)

    print "Voice Matching Application -- make a better name?"
    print "Hello %s!" % name

  def read_config_file(self):
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
      while self.wants_to_continue():
        self.ask_from_user()
        self.assess_choice()
    else:
      pass

  def train_model(self):
    print "Training voice models stored in /files/training/"
    start_time = time.time()
    self.djv.fingerprint_directory(self.training_path, [".wav", ".mp3"])
    end_time = time.time()
    #t = timeit.Timer('self.djv.fingerprint_directory(self.training_path, [".wav", ".mp3"])')
    print "Training took %f seconds" % (end_time - start_time)

  def recognize(self):
    print "Recognize from file"
    self.get_file_to_recognize_from_user()

    if self.file_to_recognize_is_valid :
      self.recognize_voice()

  def get_file_to_recognize_from_user(self):
    self.file = raw_input("File to recognize: ")

    if os.path.isfile(self.file):
      self.file_to_recognize_is_valid = True
    else:
      self.file_to_recognize_is_valid = False
      print "Unable to find the file."

  def recognize_voice(self):
    search = self.djv.recognize(FileRecognizer, self.file)

    if search is None:
      print "Unable to find in the database"
    else:
      print "The application recognized you, %s!" % self.name

  def delete_model(self):
    print "Delete all fingerprints"
    try:
      dbconfig = self.config['database']
      db = MySQLdb.connect(dbconfig['host'], dbconfig['user'], dbconfig['passwd'], dbconfig['db'])
      cur = db.cursor()
      cur.execute("delete from songs where song_id>0")
      db.commit()
      db.close()
    except Exception:
      print "Cannot connect to the MySQL DB."

  def quit(self):
    print "Please consider donating to continue this application."

  def ask_from_user(self):
    print ""
    print "[a] Train a voice model"
    print "[b] Recognize voice"
    print "[c] Delete voice model"
    print "[d] Quit"
    self.choice = raw_input("Select your option: ")
    self.choice = self.choice.lower()
    print ""

  def assess_choice(self):
    try:
      self.options[self.choice]()
    except Exception:
      pass
#      print "Unexpected input \"%s\"from the user." % (self.choice)

  def wants_to_continue(self):
    return 'd' != self.choice