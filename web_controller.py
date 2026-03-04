"""
Backend controller for web UI interaction with EnigmaMachine.
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass
from typing import Any

from enigmamachine import EnigmaMachine


def _normalize_letter(value: str) -> str:
    if not value:
        return ""
    return value[0].upper()


@dataclass
class EnigmaSession:
    machine: EnigmaMachine
    session_id: str
    seed: int | None

    @classmethod
    def create(
        cls,
        num_rotors: int,
        seed: int | None = None,
        randomize_positions: bool = False,
    ) -> "EnigmaSession":
        machine = EnigmaMachine(
            num_rotors=num_rotors,
            seed=seed,
            randomize_positions=randomize_positions,
        )
        return cls(machine=machine, session_id=str(uuid.uuid4()), seed=seed)

    def snapshot(self) -> dict[str, Any]:
        return {
            "sessionId": self.session_id,
            "seed": self.seed,
            "numRotors": self.machine.num_rotors,
            "rotorPositions": [rotor.current_position for rotor in self.machine.rotors],
            "rotors": [
                {
                    "index": index,
                    "position": rotor.current_position,
                    "mappings": rotor.rotor_mappings,
                }
                for index, rotor in enumerate(self.machine.rotors)
            ],
            "plugboard": {
                "mappings": self.machine.patchboard.rotor_mappings,
            },
            "reflector": {
                "mappings": self.machine.reflector.reflector_mappings,
            },
        }

    def encrypt_keypress(self, letter: str) -> dict[str, Any]:
        normalized = _normalize_letter(letter)
        pre_positions = [rotor.current_position for rotor in self.machine.rotors]

        if not normalized.isalpha():
            return {
                "input": letter,
                "output": letter,
                "timeline": {
                    "prePositions": pre_positions,
                    "postPositions": pre_positions,
                    "rotorStepped": False,
                },
                "trace": [],
                "state": self.snapshot(),
            }

        encryption = self.machine.encrypt_letter_with_trace(normalized)
        output = encryption["output"]
        post_positions = [rotor.current_position for rotor in self.machine.rotors]
        stepped_indices = [
            index for index, (before, after) in enumerate(zip(pre_positions, post_positions)) if before != after
        ]

        return {
            "input": normalized,
            "output": output,
            "timeline": {
                "prePositions": pre_positions,
                "postPositions": post_positions,
                "rotorStepped": bool(stepped_indices),
                "steppedRotorIndices": stepped_indices,
            },
            "trace": encryption["trace"],
            "state": self.snapshot(),
        }

    def encrypt_message(self, message: str) -> dict[str, Any]:
        input_message = message.upper()
        pre_positions = [rotor.current_position for rotor in self.machine.rotors]
        encrypted = self.machine.encrypt_message(input_message)
        post_positions = [rotor.current_position for rotor in self.machine.rotors]
        return {
            "input": input_message,
            "output": encrypted,
            "timeline": {
                "prePositions": pre_positions,
                "postPositions": post_positions,
                "resetApplied": True,
            },
            "state": self.snapshot(),
        }

    def reset_rotors(self) -> dict[str, Any]:
        pre_positions = [rotor.current_position for rotor in self.machine.rotors]
        for rotor in self.machine.rotors:
            rotor.reset_position()
        post_positions = [rotor.current_position for rotor in self.machine.rotors]
        return {
            "timeline": {
                "prePositions": pre_positions,
                "postPositions": post_positions,
                "resetApplied": True,
            },
            "state": self.snapshot(),
        }


class EnigmaSessionStore:
    def __init__(self) -> None:
        self._sessions: dict[str, EnigmaSession] = {}

    def create(
        self,
        num_rotors: int,
        seed: int | None = None,
        randomize_positions: bool = False,
    ) -> EnigmaSession:
        session = EnigmaSession.create(
            num_rotors=num_rotors,
            seed=seed,
            randomize_positions=randomize_positions,
        )
        self._sessions[session.session_id] = session
        return session

    def get(self, session_id: str) -> EnigmaSession | None:
        return self._sessions.get(session_id)
