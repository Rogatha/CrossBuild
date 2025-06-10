import re


class WordList():
    def __init__(self):
        """Reads in words from WordList.txt and stores them in a list. Assumes that all 
        words in the file are alphabetized, separated by newlines, and are all capitalized
        and that all words are unique."""

        words = []

        with open ("wordlist.txt", "r") as file:
            words = file.read().splitlines()

        self.words = words

    def get_words_of_length(self, length):
        """Returns a list of words of a given length."""
        return [word for word in self.words if len(word) == length]
    
    def get_words_starting_with(self, prefix):
        """Returns a list of words starting with a given prefix."""
        prefix_length = len(prefix)
        return [word for word in self.words if word[:prefix_length] == prefix]
    
    def get_words_ending_with(self, suffix):
        """Returns a list of words ending with a given suffix."""
        suffix_length = len(suffix)
        return [word for word in self.words if word[-suffix_length:] == suffix]
    
    def get_words_containing(self, substring):
        """Returns a list of words containing a given substring."""
        return [word for word in self.words if substring in word]
    
    def get_words_matching_pattern(self, pattern):
        """Returns a list of words matching a given pattern.
        The pattern can contain '?' for any character and '*' for zero or more characters."""
        # Convert the pattern to a regex pattern
        regex_pattern = pattern.replace('?', '.').replace('*', '.*')
        return [word for word in self.words if re.fullmatch(regex_pattern, word)]
    
    def get_all_words(self):
        """Returns all words in the word list."""
        return self.words
    
    def __len__(self):
        """Returns the number of words in the word list."""
        return len(self.words)
    
    def __repr__(self):
        """Returns a string representation of the word list."""
        return f"WordList with {len(self.words)} words."
    

    

