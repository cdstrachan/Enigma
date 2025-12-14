import random
import logging

logger = logging.getLogger(__name__)

class Rotor:
    """ 
    Enigmа rotor simulation
    """

    def __init__(self):
        self.current_position = 0
        self.rotor_mappings = {}
        self._randomize_rotor()

    def reset_position(self):
        self.current_position = 0

    # setup a random rotor mapping
    def _randomize_rotor(self):
        positions = [chr(i) for i in range(ord('A'), ord('Z') + 1)]
        for i in range(ord('A'), ord('Z') + 1):
            random_position = random.choice(positions)
            self.rotor_mappings[chr(i)] = random_position
            positions.remove(random_position)

    def rotate(self):
        self.current_position = (self.current_position + 1) % 26
        logger.debug(f"Rotor rotated to position {self.current_position}")
        return self.current_position

    def get_mapping(self, letter):
        letter = letter.upper()
        rotated_letter = chr((ord(letter) - ord('A') + self.current_position) % 26 + ord('A'))
        mapped_letter = self.rotor_mappings[rotated_letter]
        return mapped_letter

    def get_reverse_mapping(self, letter):
        letter = letter.upper()
        for key, value in self.rotor_mappings.items():
            if value == letter:
                # Un-rotate the key by current_position
                unrotated_letter = chr((ord(key) - ord('A') - self.current_position) % 26 + ord('A'))
                return unrotated_letter
        raise ValueError("Letter must be between A-Z")
