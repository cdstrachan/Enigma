"""
Main entry point for Enigma Machine simulation
"""
import logging
from enigmamachine import EnigmaMachine


def get_sample_text(file, length):
    """
    Helper function to open a sample text file that contains the text to encrypt/decrypt
    """
    with open(file, "r") as file:
        text = file.read().upper()
    text = text.replace('\n', ' ')  # make it one long string
    if length > len(text):
        length = len(text)
    logger.info(f"Loaded text of length {len(text)} from long_text.txt")
    return text[:length]


# Configure logging to both console and file
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('enigma.log', mode='w'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def main():
    """
    Main entry point
    """
    enigma_machine = EnigmaMachine(5)

    logger.info("Encrypting message")
    message = get_sample_text("long_text.txt", 100)

    # if you prefer to input your own message, uncomment below
    # message = input("Enter the message to encrypt: ").upper()
    cypher_text = enigma_machine.encrypt_message(message)
    decrypted_text = enigma_machine.encrypt_message(cypher_text)  # remember Enigma is symmetric
    logger.info(f"Original Message: {message}")
    logger.info(f"Encrypted Message: {cypher_text}")
    logger.info(f"Decrypting message: {decrypted_text}")
    # Cater for dropping spaces and non-alpha characters in comparison or not
    if ''.join(filter(str.isalpha, message)) == decrypted_text or message == decrypted_text:
        logger.info("Success: Decrypted text matches the original message.")
    else:
        logger.error("Failure: Decrypted text does NOT match the original message.")


if __name__ == "__main__":
    main()
