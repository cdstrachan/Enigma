"""
Enigma Machine Simulation
"""
import logging
from rotor import Rotor
from reflector import Reflector
from plugboard import PatchBoard

logger = logging.getLogger(__name__)


class EnigmaMachine:
    """ 
    Enigma machine simulation
    """

    def __init__(self, num_rotors=3):
        # create the rotors
        self.num_rotors = num_rotors
        self.rotors = [Rotor() for _ in range(self.num_rotors)]
        self.reflector = Reflector()
        self.patchboard = PatchBoard()
        for rotor in self.rotors:
            logger.debug(f"Rotor {self.rotors.index(rotor)} mappings:")
            logger.debug(rotor.rotor_mappings)

    def encrypt_letter(self, letter):
        original_letter = letter

        # Show header with rotor positions
        logger.info(f"{'=' * 10}")
        logger.info(f"Encrypting: '{original_letter}'")
        logger.info(f"Rotor positions: {[r.current_position for r in reversed(self.rotors)]}")
        logger.info(f"{'=' * 10}")

        # Patchboard forward
        letter = self.patchboard.get_mapping(letter)
        logger.info(f"{original_letter} → [Patchboard] → {letter}")

        # Rotate rotors
        self.rotors[0].rotate()  # rotate the first rotor before encryption
        # implement rotor stepping mechanism
        for i in range(1, self.num_rotors):
            if self.rotors[i - 1].current_position == 0:
                self.rotors[i].rotate()
            else:
                break

        logger.info(f"After rotation: {[r.current_position for r in reversed(self.rotors)]}")

        # Forward through rotors
        path = letter
        for rotor in self.rotors:
            prev_letter = letter
            letter = rotor.get_mapping(letter)
            path += f" → [R{self.rotors.index(rotor)}] → {letter}"
            logger.info(f"{prev_letter} → [Rotor {self.rotors.index(rotor)}] → {letter}")

        # Reflector
        prev_letter = letter
        letter = self.reflector.reflect(letter)
        logger.info(f"{prev_letter} → [Reflector] → {letter}")

        # Backward through rotors
        for rotor in reversed(self.rotors):
            prev_letter = letter
            letter = rotor.get_reverse_mapping(letter)
            logger.info(f"{prev_letter} → [Rotor {self.rotors.index(rotor)} ←] → {letter}")

        # Patchboard backward
        prev_letter = letter
        letter = self.patchboard.get_reverse_mapping(letter)
        logger.info(f"{prev_letter} → [Patchboard ←] → {letter}")

        logger.info(f"{'=' * 10}")
        logger.info(f"Final: '{original_letter}' → '{letter}'")
        logger.info(f"{'=' * 10}")

        return letter

    def encrypt_message(self, message):
        encrypted_message = ""
        for letter in message:
            if letter == " " or not letter.isalpha():
                encrypted_message += letter
                continue
            encrypted_letter = self.encrypt_letter(letter)
            encrypted_message += encrypted_letter
        # reset all rotors to initial position
        for rotor in self.rotors:
            rotor.reset_position()
        return encrypted_message
