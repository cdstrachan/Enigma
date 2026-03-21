"""
Enigma Machine Simulation
"""
import random
import logging
from rotor import Rotor
from reflector import Reflector
from plugboard import PatchBoard

logger = logging.getLogger(__name__)


class EnigmaMachine:
    """ 
    Enigma machine simulation
    """

    def __init__(self, num_rotors=3, seed=None, randomize_positions=False):
        if seed is not None:
            random.seed(seed)

        # create the rotors
        if num_rotors > 100:
            num_rotors = 100  # cap to prevent excessive resource usage
        self.num_rotors = num_rotors
        self.rotors = [Rotor() for _ in range(self.num_rotors)]
        self.reflector = Reflector()
        self.patchboard = PatchBoard()
        if randomize_positions:
            for rotor in self.rotors:
                rotor.set_initial_position(random.randint(0, 25))
        for rotor in self.rotors:
            logger.debug(f"Rotor {self.rotors.index(rotor)} mappings:")
            logger.debug(rotor.rotor_mappings)

    def _rotate_rotors(self):
        self.rotors[0].rotate()
        for i in range(1, self.num_rotors):
            if self.rotors[i - 1].current_position == 0:
                self.rotors[i].rotate()
            else:
                break

    def encrypt_letter_with_trace(self, letter):
        original_letter = letter.upper()
        trace = []

        letter = self.patchboard.get_mapping(original_letter)
        trace.append({
            "component": "plugboard",
            "direction": "forward",
            "from": original_letter,
            "to": letter,
        })

        self._rotate_rotors()

        for index, rotor in enumerate(self.rotors):
            prev_letter = letter
            letter = rotor.get_mapping(letter)
            trace.append({
                "component": "rotor",
                "index": index,
                "direction": "forward",
                "from": prev_letter,
                "to": letter,
            })

        prev_letter = letter
        letter = self.reflector.reflect(letter)
        trace.append({
            "component": "reflector",
            "from": prev_letter,
            "to": letter,
        })

        for index in range(self.num_rotors - 1, -1, -1):
            rotor = self.rotors[index]
            prev_letter = letter
            letter = rotor.get_reverse_mapping(letter)
            trace.append({
                "component": "rotor",
                "index": index,
                "direction": "reverse",
                "from": prev_letter,
                "to": letter,
            })

        prev_letter = letter
        letter = self.patchboard.get_reverse_mapping(letter)
        trace.append({
            "component": "plugboard",
            "direction": "reverse",
            "from": prev_letter,
            "to": letter,
        })

        return {
            "input": original_letter,
            "output": letter,
            "trace": trace,
        }

    def encrypt_letter(self, letter):
        result = self.encrypt_letter_with_trace(letter)
        original_letter = result["input"]
        encrypted_letter = result["output"]

        # Show header with rotor positions
        logger.info(f"{'=' * 10}")
        logger.info(f"Encrypting: '{original_letter}'")
        logger.info(f"Rotor positions: {[r.current_position for r in reversed(self.rotors)]}")
        logger.info(f"{'=' * 10}")

        for step in result["trace"]:
            if step["component"] == "plugboard":
                direction = "←" if step["direction"] == "reverse" else ""
                logger.info(f"{step['from']} → [Patchboard {direction}] → {step['to']}")
            elif step["component"] == "reflector":
                logger.info(f"{step['from']} → [Reflector] → {step['to']}")
            elif step["component"] == "rotor":
                direction = " ←" if step["direction"] == "reverse" else ""
                logger.info(f"{step['from']} → [Rotor {step['index']}{direction}] → {step['to']}")

        logger.info(f"{'=' * 10}")
        logger.info(f"Final: '{original_letter}' → '{encrypted_letter}'")
        logger.info(f"{'=' * 10}")

        return encrypted_letter

    def encrypt_message(self, message):
        encrypted_message = ""
        for letter in message:
            if letter == " " or not letter.isalpha():
                encrypted_message += letter  # Comment out to drop spaces and non-alpha characters
                continue
            encrypted_letter = self.encrypt_letter(letter)
            encrypted_message += encrypted_letter
        # reset all rotors to initial position
        for rotor in self.rotors:
            rotor.reset_position()
        return encrypted_message
