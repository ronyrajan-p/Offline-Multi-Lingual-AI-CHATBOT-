from __future__ import annotations

"""GPIO button input adapter.

Button support requires a physical wiring plan, so this module exposes a clear
adapter boundary without being used by the default keyboard flow.
"""


class ButtonInput:
    """Read navigation events from GPIO buttons when configured."""

    def read_event(self) -> str:
        """Read one button event.

        The default program does not instantiate this class. Wire it into the
        controller only after GPIO pins are assigned for the physical model.
        """

        raise RuntimeError("Button input is not configured for this device build.")
