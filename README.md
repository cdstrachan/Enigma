# Enigma Machine Simulator

A Python implementation of the famous Enigma encryption machine used during World War II.

## What is the Enigma Machine?

The Enigma machine was an electro-mechanical cipher device used primarily by Nazi Germany during World War II to encrypt military communications. It was considered unbreakable at the time, but the work of cryptanalysts at Bletchley Park, including Alan Turing, successfully broke the code, significantly contributing to the Allied victory.

The machine's security came from its complex system of rotors, a reflector, and a plugboard that created trillions of possible encryption combinations.

## How It Works

### Encryption Flow

```
                    ┌──────────────┐
    Plain Text  →   │  Plugboard   │
                    └──────┬───────┘
                           ↓
                    ┌──────────────┐
                    │   Rotor 0    │  (Rightmost - rotates every letter)
                    └──────┬───────┘
                           ↓
                    ┌──────────────┐
                    │   Rotor 1    │  (Rotates every 26 letters)
                    └──────┬───────┘
                           ↓
                    ┌──────────────┐
                    │   Rotor 2    │  (Rotates every 676 letters)
                    └──────┬───────┘
                           ↓
                    ┌──────────────┐
                    │   Rotor 3    │  (Rotates every 17,576 letters)
                    └──────┬───────┘
                           ↓
                    ┌──────────────┐
                    │   Rotor 4    │  (Rotates every 456,976 letters)
                    └──────┬───────┘
                           ↓
                    ┌──────────────┐
                    │  Reflector   │  (Symmetric pairs: A↔B means B↔A)
                    └──────┬───────┘
                           ↓
                    (Return through rotors in reverse)
                           ↓
                    ┌──────────────┐
                    │  Plugboard   │
                    └──────┬───────┘
                           ↓
                    Cipher Text
```

### Encryption Process

1. **Plugboard (Forward)**: The input letter is first substituted using the plugboard mapping
2. **Rotor Rotation**: The rightmost rotor advances by one position before encryption
3. **Rotor Stepping**: When a rotor completes a full rotation (returns to position 0), it triggers the next rotor to advance (like an odometer)
4. **Forward Pass**: The letter passes through each rotor from right to left, being substituted at each stage
5. **Reflector**: The letter is reflected back using symmetric pairs (if A maps to C, then C maps to A)
6. **Backward Pass**: The letter passes back through all rotors from left to right in reverse
7. **Plugboard (Backward)**: Final substitution through the plugboard in reverse
8. **Output**: The encrypted letter is produced

### Symmetry

The Enigma machine is **symmetric**: encrypting an encrypted message with the same settings produces the original message. This means encryption and decryption use the exact same process.

## Features

- Multiple configurable rotors (default: 5)
- Plugboard (patchboard) for additional scrambling
- Reflector with symmetric letter pairs
- Rotor stepping mechanism (odometer-style)
- Detailed logging showing encryption flow
- Position tracking for all rotors

## Deviations from Historical Enigma

This implementation differs from the actual WWII Enigma machines in several ways:

| Feature | Historical Enigma | This Implementation |
|---------|------------------|---------------------|
| **Rotor Wiring** | Fixed, pre-defined wirings (I, II, III, IV, V) | Randomly generated on initialization |
| **Number of Rotors** | Typically 3-4 rotors | Configurable (default: 5) |
| **Plugboard** | Manual wire connections, typically 10 pairs | Fully randomized substitution |
| **Reflector** | Fixed reflectors (B, C) | Randomly generated symmetric pairs |
| **Ring Settings** | Adjustable ring positions | Not implemented: this simulation uses random wirings, so the ring offset doesn't add meaningful security |
| **Notch Positions** | Fixed turnover notches (different per rotor) | Simple position-0 turnover |
| **Initial Positions** | User-configurable starting positions | Always starts at position 0 |
| **Non-Alpha Characters** | Not possible, or replaced with a fixed letter such as "X" | Spaces and non-alpha characters left unchanged (can be filtered out - see enigmamachine.py/encrypt_message)| 


### Why These Deviations?

- **Random Rotors**: Simplifies setup and demonstrates the encryption principle without historical rotor complexity
- **Flexible Rotor Count**: Allows experimentation with different security levels
- **Simplified Stepping**: Uses a straightforward odometer mechanism rather than the complex notch system
- **Readability**: Makes encrypted text easier to read by preserving spaces. Historical operators would manually group letters with a fixed letter. (e.g.,""HOW ARE YOU" ->"HOWXAREXYOU"). Comment out the filter in `enigmamachine.py/encrypt_message` to drop all spaces and non-alpha characters.

## Configuration Options

### Number of Rotors

You can configure the number of rotors when creating the machine:

```python
# Create machine with 3 rotors (like historical M3 Enigma)
enigma = EnigmaMachine(num_rotors=3)

# Create machine with 5 rotors (more secure)
enigma = EnigmaMachine(num_rotors=5)
```

### Logging Level

Adjust the logging level in `main.py`:

```python
logging.basicConfig(
    level=logging.INFO,    # Change to INFO, WARNING, or ERROR for less verbose output, or DEBUG for loads of output.
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('enigma.log', mode='w'),
        logging.StreamHandler()
    ]
)
```

## Usage

### Basic Usage

```python
from enigmamachine import EnigmaMachine

# Create an Enigma machine with 5 rotors
enigma = EnigmaMachine(num_rotors=5)

# Encrypt a message
message = "HELLO WORLD"
encrypted = enigma.encrypt_message(message)
print(f"Encrypted: {encrypted}")

# Decrypt (same operation due to symmetry)
decrypted = enigma.encrypt_message(encrypted)
print(f"Decrypted: {decrypted}")
```

### Running the Demo

```bash
python main.py
```

By default, this will:
- Load sample text from `long_text.txt`
- Encrypt the first 100 characters
- Decrypt the result
- Verify the decryption matches the original

### Using Custom Input

Edit `main.py` and uncomment the input line:

```python
# message = get_sample_text(100)
message = input("Enter the message to encrypt: ").upper()
```

## Project Structure

```
Enigma/
├── enigmamachine.py    # Main Enigma machine class
├── rotor.py            # Rotor implementation with rotation
├── reflector.py        # Reflector with symmetric pairs
├── plugboard.py        # Plugboard/patchboard substitution
├── main.py             # Demo and entry point
├── long_text.txt       # Sample text file (optional)
└── enigma.log          # Output log file (generated)
```

## Example Output

```
==========
Encrypting: 'H'
Rotor positions: [0, 0, 0, 0, 1]
==========
H → [Patchboard] → A
After rotation: [0, 0, 0, 0, 1]
A → [Rotor 0] → W
W → [Rotor 1] → E
E → [Rotor 2] → T
T → [Rotor 3] → J
J → [Rotor 4] → X
X → [Reflector] → D
D → [Rotor 4 ←] → R
R → [Rotor 3 ←] → I
I → [Rotor 2 ←] → D
D → [Rotor 1 ←] → V
V → [Rotor 0 ←] → R
R → [Patchboard ←] → M
==========
Final: 'H' → 'M'
==========
```

## Requirements

- Python 3.6+
- No external dependencies (uses only standard library)

## Historical Context

The breaking of the Enigma code was one of the greatest intellectual achievements of WWII. The Bombe machine, designed by Alan Turing and Gordon Welchman, exploited weaknesses in Enigma's design (such as the fact that no letter could encrypt to itself due to the reflector) to systematically test possible rotor settings.

This project is educational and demonstrates the core principles of the Enigma machine's operation.

## License

Please see the license file.

## Source

Original source at https://github.com/cdstrachan/Enigma

## Acknowledgments

Inspired by the historical Enigma machine and the brilliant cryptanalysts who broke it, and of course Alan Turing, the founder of modern computing.


