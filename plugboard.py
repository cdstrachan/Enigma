import random
import logging

logger = logging.getLogger(__name__)


class PatchBoard:
    """
    Enigmа patch simulation. Note that the patchboard is basically a static rotor.
    But the advantage is you can wire it yourself.
    """
    total_positions = 26

    def __init__(self):
        self.rotor_mappings = {}
        self._randomize_rotor()
        logger.debug("Patchboard mappings:")
        logger.debug(self.rotor_mappings)

    # setup a random rotor mapping
    def _randomize_rotor(self):
        positions = [chr(i) for i in range(ord('A'), ord('Z') + 1)]
        for i in range(ord('A'), ord('Z') + 1):
            random_position = random.choice(positions)
            self.rotor_mappings[chr(i)] = random_position
            positions.remove(random_position)

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


# test code
a = PatchBoard()
map = a.get_mapping('A')
logger.debug(a.get_reverse_mapping(map))
