from __future__ import annotations


class KeyboardInput:
    def read_message(self) -> str:
        return input("> ").strip()
