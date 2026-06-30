from __future__ import annotations


class ButtonInput:
    def read_event(self) -> str:
        raise NotImplementedError("GPIO button support should be added on Raspberry Pi.")
