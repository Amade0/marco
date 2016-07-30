# Markov.py
# Heavily modified version of a Markov chain module written by Shabda Raaj
# http://agiliq.com/blog/2009/06/generating-pseudo-random-text-with-markov-
#   chains-u/

import random

class Markov(object):

    def __init__(self):
        """Initialize the database and punctuation list."""
        self.database = {}
        self.punctuation = ('.', '!', '?', ',', ';', ':')

    def parse(self, text):
        """Parse input text by first processing it and then inserting it into
        the database.

        Keyword arguments:
        text -- The raw text to be parsed, as a string.
        """
        words = text.split()
        words = self.__process_input_text(words)
        words = ['$psom', '$som'] + words + ['$eom']
        for w1, w2, w3 in self.__triples(words):
            # no control signals in keys
            w1 = self.__strip_control_signals(w1)
            w2 = self.__strip_control_signals(w2)
            key = (w1, w2)
            if key in self.database:
                self.database[key].append(w3)
            else:
                self.database[key] = [w3]

    def unparse(self, text):
        """Undoes the parsing of the supplied text (if possible), removing all
        associations it would form if parsed.

        Keyword arguments:
        text -- The raw text to be unparsed, as a string.
        """
        words = text.split()
        words = self.__process_input_text(words)
        words = ['$psom', '$som'] + words + ['$eom']
        for w1, w2, w3 in self.__triples(words):
            # no control signals in keys
            w1 = self.__strip_control_signals(w1)
            w2 = self.__strip_control_signals(w2)
            key = (w1, w2)
            if key in self.database:
                self.database[key].remove(w3)
                if not self.database[key]:
                    del self.database[key]

    def __triples(self, words):
        """ Create a list of 3-tuples of every sequence of 3 consecutive words
        in a given list.

        Keyword arguments:
        words -- A list.
        """
        if len(words) < 3:
            return
        for i in range(len(words) - 2):
            yield (words[i], words[i+1], words[i+2])

    def __strip_control_signals(self, word):
        """ Remove the control signals (eg for capitalization) from a word and
        return the modified word.

        Keyword arguments:
        word -- A word, which may or may not contain control signals.
        """
        signals = ['$shft', '$caps', '$cape']
        for signal in signals:
            signal_pos = word.find(signal)
            if signal_pos > -1:
                pre = word[0:signal_pos]
                pst = word[signal_pos + 5:]
                word = pre + pst
        return word

    def __process_input_text(self, words):
        """ Refine input text by converting capitalization to control
        signals and making the entire input lowercase.

        Keyword arguments:
        words -- A list of strings.
        """
        output = []
        cap_state = False
        for word in words:
            result = self.__process_input_word(word, cap_state)
            cap_state = result[0]
            if result[1]:
                output.append(result[1])
            if result[2]:
                output.extend(result[2])
        return output

    def __process_input_word(self, word, cap_state = False):
        """ Process a word by converting capitalization to control signals and
        making the word lowercase. Helper method of __process_input_text.

        Keyword arugments:
        word -- A string.
        caps_state -- Whether caps state ("caps lock") is currently active.
            (default False)
        """
        extra = []
        if len(word) > 1:
            # detect change of caps state
            if cap_state and not word.isupper():
                if word.islower():
                    cap_state = False
                    word = '$cape' + word
                else:
                    for index, letter in enumerate(word):
                        if letter.islower():
                            word = word[:index] + '$cape' + word[index:]
                            cap_state = False
                            break
            elif not cap_state and not word.islower():
                # check for shift
                if word[0].isupper() and word[1:].islower():
                    word = '$shft' + word
                elif word.isupper():
                    word = '$caps' + word
                    cap_state = True
                else:
                    for index, letter in enumerate(word):
                        if letter.isupper():
                            word = word[:index] + '$caps' + word[index:]
                            cap_state = True
                            break
            # make punctuation its own words
            if word.endswith(self.punctuation):
                punct = ''
                while word.endswith(self.punctuation):
                    punct = word[-1:] + punct
                    word = word[:-1]
                extra.append(punct)
        else:
            if cap_state and word.islower():
                word = '$cape' + word
                cap_state = False
            elif not cap_state and word.isupper():
                word = '$shft' + word
        if not word.islower():
            word = word.lower()
        return (cap_state, word, extra)

    def output(self):
        """Generate an output string from the database."""
        w1, w2 = ['$psom', '$som']
        gen_words = []
        while w2 != '$eom':
            # w1, w2 = w2, random.choice(self.database[(w1, w2)])
            key = (
                self.__strip_control_signals(w1),
                self.__strip_control_signals(w2)
                )
            w1 = w2
            w2 = random.choice(self.database[key])
            if w1 in self.punctuation:
                # append punctuation to most recent word
                prevword = gen_words[-1]
                prevword = prevword + w1
                gen_words[-1] = prevword
            else:
                gen_words.append(w1)
        output = gen_words[1:]
        output = self.__process_output_text(output)
        output = ' '.join(output)
        return output

    def __process_output_text(self, words):
        """Process output text, applying and removing control signals to
        restore the original formatting of the text. Helper method of output.

        Keyword arguments:
        words -- A list of strings.
        """
        output = []
        cap_state = False
        for word in words:
            next_cap_state = cap_state
            shft_pos = word.find('$shft')
            if shft_pos == 0:
                word = word[5:]
                if len(word) > 1:
                    word = word[0].upper() + word[1:].lower()
                else:
                    word = word.upper()
            caps_pos = word.find('$caps')
            if caps_pos > -1:
                pre = word[0:caps_pos]
                pst = word[caps_pos + 5:]
                if cap_state:
                    word = pre + pst
                    word = word.upper()
                else:
                    next_cap_state = True
                    word = pre + pst.upper()
            cape_pos = word.find('$cape')
            if cape_pos > -1:
                pre = word[0:cape_pos]
                pst = word[cape_pos + 5:]
                if not cap_state:
                    word = pre + pst
                else:
                    next_cap_state = False
                    word = pre.upper() + pst
            if cap_state and next_cap_state:
                word = word.upper()
            cap_state = next_cap_state
            output.append(word)
        return output

