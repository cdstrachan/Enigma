"""
Unit tests for Enigma Machine Simulator
"""
import unittest
import logging
from enigmamachine import EnigmaMachine
from rotor import Rotor
from reflector import Reflector
from plugboard import PatchBoard

# Disable logging during tests
logging.disable(logging.CRITICAL)


class TestRotor(unittest.TestCase):
    """Test cases for Rotor class"""

    def setUp(self):
        """Create a fresh rotor for each test"""
        self.rotor = Rotor()

    def test_rotor_initialization(self):
        """Test rotor initializes with position 0"""
        self.assertEqual(self.rotor.current_position, 0)

    def test_rotor_has_all_mappings(self):
        """Test rotor has mappings for all 26 letters"""
        self.assertEqual(len(self.rotor.rotor_mappings), 26)

    def test_rotor_mappings_unique(self):
        """Test each letter maps to a unique letter"""
        values = list(self.rotor.rotor_mappings.values())
        self.assertEqual(len(values), len(set(values)))

    def test_rotor_rotation(self):
        """Test rotor advances position correctly"""
        initial_position = self.rotor.current_position
        self.rotor.rotate()
        self.assertEqual(self.rotor.current_position, initial_position + 1)

    def test_rotor_rotation_wraparound(self):
        """Test rotor wraps around after position 25"""
        self.rotor.current_position = 25
        self.rotor.rotate()
        self.assertEqual(self.rotor.current_position, 0)

    def test_rotor_reset(self):
        """Test rotor can be reset to position 0"""
        self.rotor.current_position = 15
        self.rotor.reset_position()
        self.assertEqual(self.rotor.current_position, 0)

    def test_get_mapping_returns_letter(self):
        """Test get_mapping returns a valid letter"""
        result = self.rotor.get_mapping('A')
        self.assertTrue(result.isalpha())
        self.assertTrue(result.isupper())

    def test_reverse_mapping_consistency(self):
        """Test forward and reverse mapping are consistent"""
        # Set rotor to a known position
        self.rotor.current_position = 5

        # Get forward mapping
        letter = 'A'
        mapped = self.rotor.get_mapping(letter)

        # Reset to same position
        self.rotor.current_position = 5

        # Get reverse mapping - should return original letter
        reversed_letter = self.rotor.get_reverse_mapping(mapped)
        self.assertEqual(letter, reversed_letter)


class TestReflector(unittest.TestCase):
    """Test cases for Reflector class"""

    def setUp(self):
        """Create a fresh reflector for each test"""
        self.reflector = Reflector()

    def test_reflector_has_all_mappings(self):
        """Test reflector has mappings for all 26 letters"""
        self.assertEqual(len(self.reflector.reflector_mappings), 26)

    def test_reflector_symmetry(self):
        """Test reflector is symmetric: if A→B then B→A"""
        for letter, reflected in self.reflector.reflector_mappings.items():
            # Reflecting the reflected letter should give original
            self.assertEqual(
                self.reflector.reflector_mappings[reflected],
                letter,
                f"Reflector not symmetric: {letter}→{reflected} but {reflected}→{self.reflector.reflector_mappings[reflected]}"
            )

    def test_reflector_no_self_mapping(self):
        """Test no letter reflects to itself"""
        for letter, reflected in self.reflector.reflector_mappings.items():
            self.assertNotEqual(
                letter,
                reflected,
                f"Letter {letter} reflects to itself"
            )

    def test_reflect_returns_letter(self):
        """Test reflect returns a valid letter"""
        result = self.reflector.reflect('A')
        self.assertTrue(result.isalpha())
        self.assertTrue(result.isupper())

    def test_double_reflection_returns_original(self):
        """Test reflecting twice returns original letter"""
        letter = 'M'
        reflected_once = self.reflector.reflect(letter)
        reflected_twice = self.reflector.reflect(reflected_once)
        self.assertEqual(letter, reflected_twice)


class TestPatchBoard(unittest.TestCase):
    """Test cases for PatchBoard class"""

    def setUp(self):
        """Create a fresh patchboard for each test"""
        self.patchboard = PatchBoard()

    def test_patchboard_has_all_mappings(self):
        """Test patchboard has mappings for all 26 letters"""
        self.assertEqual(len(self.patchboard.rotor_mappings), 26)

    def test_patchboard_mappings_unique(self):
        """Test each letter maps to a unique letter"""
        values = list(self.patchboard.rotor_mappings.values())
        self.assertEqual(len(values), len(set(values)))

    def test_get_mapping_returns_letter(self):
        """Test get_mapping returns a valid letter"""
        result = self.patchboard.get_mapping('A')
        self.assertTrue(result.isalpha())
        self.assertTrue(result.isupper())

    def test_reverse_mapping_consistency(self):
        """Test forward and reverse mapping are consistent"""
        letter = 'K'
        mapped = self.patchboard.get_mapping(letter)
        reversed_letter = self.patchboard.get_reverse_mapping(mapped)
        self.assertEqual(letter, reversed_letter)


class TestEnigmaMachine(unittest.TestCase):
    """Test cases for EnigmaMachine class"""

    def setUp(self):
        """Create a fresh enigma machine for each test"""
        self.enigma = EnigmaMachine(num_rotors=3)

    def test_machine_has_correct_rotor_count(self):
        """Test machine is created with correct number of rotors"""
        enigma_5 = EnigmaMachine(num_rotors=5)
        self.assertEqual(len(enigma_5.rotors), 5)

    def test_encryption_symmetry_single_letter(self):
        """Test encrypting twice returns original (single letter)"""
        letter = 'A'
        encrypted = self.enigma.encrypt_letter(letter)

        # Reset rotors to initial position
        for rotor in self.enigma.rotors:
            rotor.reset_position()

        decrypted = self.enigma.encrypt_letter(encrypted)
        self.assertEqual(letter, decrypted)

    def test_encryption_symmetry_message(self):
        """Test encrypting twice returns original (full message)"""
        message = "HELLO WORLD"
        encrypted = self.enigma.encrypt_message(message)
        decrypted = self.enigma.encrypt_message(encrypted)
        self.assertEqual(message, decrypted)

    def test_no_letter_encrypts_to_itself(self):
        """Test no letter encrypts to itself (reflector property)"""
        for letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
            # Create fresh machine for each letter
            enigma = EnigmaMachine(num_rotors=3)
            encrypted = enigma.encrypt_letter(letter)
            self.assertNotEqual(
                letter,
                encrypted,
                f"Letter {letter} encrypted to itself"
            )

    def test_rotor_rotation_on_encryption(self):
        """Test first rotor rotates with each letter"""
        initial_pos = self.enigma.rotors[0].current_position
        self.enigma.encrypt_letter('A')
        self.assertEqual(self.enigma.rotors[0].current_position, initial_pos + 1)

    def test_rotor_stepping_mechanism(self):
        """Test rotors step like odometer"""
        enigma = EnigmaMachine(num_rotors=3)

        # Encrypt 26 letters - rotor 0 should complete rotation, rotor 1 should advance
        for _ in range(26):
            enigma.encrypt_letter('A')

        self.assertEqual(enigma.rotors[0].current_position, 0, "Rotor 0 should be at position 0")
        self.assertEqual(enigma.rotors[1].current_position, 1, "Rotor 1 should have advanced once")

    def test_different_positions_different_encryption(self):
        """Test same letter encrypts differently at different rotor positions"""
        enigma = EnigmaMachine(num_rotors=3)

        encrypted_1 = enigma.encrypt_letter('A')
        encrypted_2 = enigma.encrypt_letter('A')

        self.assertNotEqual(
            encrypted_1,
            encrypted_2,
            "Same letter should encrypt differently at different positions"
        )

    def test_spaces_preserved(self):
        """Test spaces are preserved in message"""
        message = "HELLO WORLD"
        encrypted = self.enigma.encrypt_message(message)
        # Count spaces
        self.assertEqual(message.count(' '), encrypted.count(' '))

    def test_non_alpha_preserved(self):
        """Test non-alphabetic characters are preserved"""
        message = "HELLO, WORLD!"
        encrypted = self.enigma.encrypt_message(message)
        self.assertIn(',', encrypted)
        self.assertIn('!', encrypted)

    def test_long_message_encryption(self):
        """Test encryption of longer message"""
        message = "THE QUICK BROWN FOX JUMPS OVER THE LAZY DOG"
        encrypted = self.enigma.encrypt_message(message)
        decrypted = self.enigma.encrypt_message(encrypted)
        self.assertEqual(message, decrypted)

    def test_empty_message(self):
        """Test encryption of empty message"""
        message = ""
        encrypted = self.enigma.encrypt_message(message)
        self.assertEqual(message, encrypted)

    def test_multiple_rotor_configurations(self):
        """Test different rotor counts work correctly"""
        for num_rotors in [1, 3, 5, 7]:
            enigma = EnigmaMachine(num_rotors=num_rotors)
            message = "TEST"
            encrypted = enigma.encrypt_message(message)
            decrypted = enigma.encrypt_message(encrypted)
            self.assertEqual(
                message,
                decrypted,
                f"Failed with {num_rotors} rotors"
            )


class TestEnigmaIntegration(unittest.TestCase):
    """Integration tests for full encryption/decryption workflow"""

    def test_full_alphabet_round_trip(self):
        """Test all letters can be encrypted and decrypted"""
        enigma = EnigmaMachine(num_rotors=3)
        alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

        encrypted = enigma.encrypt_message(alphabet)
        decrypted = enigma.encrypt_message(encrypted)

        self.assertEqual(alphabet, decrypted)

    def test_repeated_letter_encryption(self):
        """Test repeated letters encrypt to different values"""
        enigma = EnigmaMachine(num_rotors=3)
        message = "AAAAAAA"

        encrypted = enigma.encrypt_message(message)

        # All encrypted letters should be different (except possibly by chance)
        # At minimum, first and second should differ
        self.assertNotEqual(encrypted[0], encrypted[1])

    def test_very_long_message(self):
        """Test encryption of very long message (tests rotor stepping)"""
        enigma = EnigmaMachine(num_rotors=3)

        # Create a message longer than 26*26 to test multi-rotor stepping
        message = "A" * 1000

        encrypted = enigma.encrypt_message(message)
        decrypted = enigma.encrypt_message(encrypted)

        self.assertEqual(message, decrypted)


def run_tests():
    """Run all tests"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestRotor))
    suite.addTests(loader.loadTestsFromTestCase(TestReflector))
    suite.addTests(loader.loadTestsFromTestCase(TestPatchBoard))
    suite.addTests(loader.loadTestsFromTestCase(TestEnigmaMachine))
    suite.addTests(loader.loadTestsFromTestCase(TestEnigmaIntegration))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Return success status
    return result.wasSuccessful()


if __name__ == '__main__':
    # Run tests when script is executed directly
    success = run_tests()
    exit(0 if success else 1)
