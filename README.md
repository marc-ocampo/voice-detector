# Voice Matcher

This is a repository for a voice detector script.
The idea is to use a fixed phrase to detect the voice similar to Apple's "Hey Siri".

The idea requires:
- recording of the fixed phrase
- usage of an acoustic fingerprinting algorithm
- some database or at least memory to store metadata.

The project will use [`Dejavu`](https://github.com/worldveil/dejavu) for the acoustic fingerprinting application.

Refer to the [installation manual](https://github.com/worldveil/dejavu/blob/master/INSTALLATION.md) first to install the prerequisites manually.

## Installation Notes
- MySQLdb required MySQL first
 `apt-get install python-dev libmysqlclient-dev`
 `pip install MySQL-python`

- After cloning the repository, pull the submodule
 `git submodule update --init --recursive`

## Usage Notes
1. Configuration file `config.DEFAULT` has the correct information.
2. MySQL DB is running with the DB that matches the configuration file.
3. Call the `run` script.

See the `files/CONTENTS.md` for the description of the default files used for training and recognition
