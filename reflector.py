"""
Enigma reflector simulation
"""
import random
import logging

logger = logging.getLogger(__name__)


class Reflector:
    """
    Enigma reflector simulation
    Reflector has 13 random pairs where each letter maps symmetrically
    If A->C, then C->A
    """

    def __init__(self):
        self.reflector_mappings = {}
        self._randomize_reflector()

    def _randomize_reflector(self):
        # Get all 26 letters
        available_letters = [chr(i) for i in range(ord('A'), ord('Z') + 1)]
        random.shuffle(available_letters)

        # Create 13 pairs
        for i in range(0, 26, 2):
            letter1 = available_letters[i]
            letter2 = available_letters[i + 1]

            # Create symmetrical mapping
            self.reflector_mappings[letter1] = letter2
            self.reflector_mappings[letter2] = letter1
        logger.debug("Reflector mappings:")
        logger.debug(self.reflector_mappings)

    def reflect(self, letter):
        letter = letter.upper()
        reflected_letter = self.reflector_mappings[letter]
        logger.debug(f"Letter {letter} reflected to {reflected_letter}")
        return reflected_letter
