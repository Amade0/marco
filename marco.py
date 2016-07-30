# marco.py
# An object extending the functionality of a Markov object by saving and
# loading its database to and from the hard drive and adding commands.

import os.path
import pickle
import datetime, threading
import random
from Markov import Markov

class marco:

    def __init__(self, file_name='./marco_db.pickle', chat_freq=0.15):
        """Load a Markov from file or create a new Markov as necessary.
        Initialize the response frequency and begin the autosave schedule.

        Keyword arguments:
        file_name -- The location at which to load/store the database.
        chat_freq -- The chance of spontaneously generating an output message
            upon receiving an input message.
        """
        self.file_name = file_name
        if os.path.isfile(self.file_name):
            db_file = open(self.file_name, 'rb')
            self.markov = pickle.load(db_file)
            db_file.close()
        else:
            self.markov = Markov()
        self.chat_freq = chat_freq
        self.on()
        self.autosave(True)

    def autosave(self, skip = False):
        """Save the database to a file and schedule the next autosave.

        Keyword arguments:
        skip -- If True, do not save the database to file. (default False)
        """
        threading.Timer(5 * 60, self.autosave).start()
        if not skip:
            db_file = open(self.file_name, 'wb')
            pickle.dump(self.markov, db_file)
            db_file.close()

    def command(self, command, args = ''):
        """Execute the provided command and return the chat output of the
        command.

        Keyword arguments:
        command -- The name of the command to run as a string.
        args -- Any arguments to the command as a string.
        """
        command = command.lower()
        if command == 'ping':
            return 'pong!'
        if command == 'output':
            return self.output()
        if command == 'help':
            if args:
                args = args.lower()
                if args[0] == '!':
                    args = args[1:]
                elif args == 'ping':
                    return '!ping responds "pong!"'
                elif args == 'help':
                    return (
                        '!help provides help messages. use !help commandname '
                        'for more information about a command.'
                        )
                elif args == 'off':
                    return (
                        '!off silences the bot indefinitely. provide a number '
                        'to silence the bot for that many minutes instead.'
                        )
                elif args == 'on':
                    return '!on unsilences the bot immediately.'
                elif args == 'output':
                    return (
                        '!output immediately produces a line of output from '
                        'the bot.'
                        )
            return (
                'I am a markov chain bot created by lemon. I understand the '
                'following commands: !ping !help !off !on !output. Use !help '
                'commandname for more information about a command.'
                )
        if command == 'off':
            if args:
                args = self.__strToNum(args)
                if args == False:
                    return (
                        '!off only takes a positive integer as an argument. '
                        '(no action taken)'
                        )
                else:
                    self.off(args)
                    return (
                        'deactivating for ' + str(args) + ' minutes (use !on '
                        'to reactivate immediately)'
                        )
            else:
                self.off()
                return 'deactivating indefinitely (use !on to reactivate)'
        if command == 'on':
            self.on()
            return 'reactivating.';
        if command == 'unlearn':
            self.markov.unparse(args)
            return 'Unlearned provided message.'

    def __strToNum(self, string):
        """Convert a string to a number. Return False if the conversion fails.

        Keyword arguments:
        string -- A string.
        """
        try:
            return int(string)
        except ValueError:
            return False

    def off(self, time = 0):
        """Deactivate, temporarily disabling the simultaneous response feature.

        Keyword arguments:
        time -- The number of minutes to deactivate for (0 for until
        reactivated). (default 0)
        """
        self.silent = True
        if time > 0:
            threading.Timer(time * 60, self.on).start()

    def on(self):
        """Immediately reactivate."""
        self.silent = False

    def input(self, message):
        """Passes input to the Markov chain. May generate a simultaneous
        response.
        """
        self.markov.parse(message)
        if random.random() <= self.chat_freq and not self.silent:
            return self.output()

    def output(self):
        """Generates an output message from the Markov chain."""
        return self.markov.output()
