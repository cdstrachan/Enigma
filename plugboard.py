import random
import logging

logger = logging.getLogger(__name__)


class PatchBoard:
    """
    Enigma patch simulation.
    Patchboard wiring is represented as 13 symmetric letter pairs.
    """

    def __init__(self):
        self.rotor_mappings = {}
        self._randomize_rotor()
        logger.debug("Patchboard mappings:")
        logger.debug(self.rotor_mappings)

    # setup random symmetric patchboard pairs
    def _randomize_rotor(self):
        available_letters = [chr(i) for i in range(ord('A'), ord('Z') + 1)]
        random.shuffle(available_letters)

        for i in range(0, 26, 2):
            letter1 = available_letters[i]
            letter2 = available_letters[i + 1]
            self.rotor_mappings[letter1] = letter2
            self.rotor_mappings[letter2] = letter1

    def get_mapping(self, letter):
        letter = letter.upper()
        mapped_letter = self.rotor_mappings[letter]
        logger.debug(f"Patchboard: Letter {letter} mapped to {mapped_letter}")
        return mapped_letter

    def get_reverse_mapping(self, letter):
        letter = letter.upper()
        for key, value in self.rotor_mappings.items():
            if value == letter:
                logger.debug(f"Patchboard: Letter {letter} reverse mapped to {key}")
                return key
        raise ValueError("Letter must be between A-Z")
