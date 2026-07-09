from __future__ import annotations

"""Keyboard input adapters.

`KeyboardInput` uses Python's built-in `input()` and is only for console
development, where a real terminal is attached to stdin. `USBEvdevKeyboardInput`
reads raw key events directly from a USB keyboard device node and is what the
finished hardware build must use: a systemd service has no controlling
terminal, so `input()` raises `EOFError` the instant it's called, because
stdin is connected to `/dev/null` rather than a keyboard.
"""


class KeyboardInput:
    """Read messages from standard input. Console/development use only."""

    def read_message(self) -> str:
        """Prompt for and return one user message."""

        return input("chatbot> ").strip()


# US QWERTY layout, unshifted characters. Only the keys a short chat message
# realistically needs; anything not listed here is silently ignored rather
# than raising, since unmapped keys (media keys, function keys) are common on
# consumer USB keyboards.
_KEY_CHARACTERS = {
    "KEY_A": "a", "KEY_B": "b", "KEY_C": "c", "KEY_D": "d", "KEY_E": "e",
    "KEY_F": "f", "KEY_G": "g", "KEY_H": "h", "KEY_I": "i", "KEY_J": "j",
    "KEY_K": "k", "KEY_L": "l", "KEY_M": "m", "KEY_N": "n", "KEY_O": "o",
    "KEY_P": "p", "KEY_Q": "q", "KEY_R": "r", "KEY_S": "s", "KEY_T": "t",
    "KEY_U": "u", "KEY_V": "v", "KEY_W": "w", "KEY_X": "x", "KEY_Y": "y",
    "KEY_Z": "z",
    "KEY_0": "0", "KEY_1": "1", "KEY_2": "2", "KEY_3": "3", "KEY_4": "4",
    "KEY_5": "5", "KEY_6": "6", "KEY_7": "7", "KEY_8": "8", "KEY_9": "9",
    "KEY_MINUS": "-", "KEY_EQUAL": "=", "KEY_COMMA": ",", "KEY_DOT": ".",
    "KEY_SLASH": "/", "KEY_SEMICOLON": ";", "KEY_APOSTROPHE": "'",
    "KEY_LEFTBRACE": "[", "KEY_RIGHTBRACE": "]", "KEY_BACKSLASH": "\\",
    "KEY_GRAVE": "`",
}

_SHIFTED_KEY_CHARACTERS = {
    "KEY_1": "!", "KEY_2": "@", "KEY_3": "#", "KEY_4": "$", "KEY_5": "%",
    "KEY_6": "^", "KEY_7": "&", "KEY_8": "*", "KEY_9": "(", "KEY_0": ")",
    "KEY_MINUS": "_", "KEY_EQUAL": "+", "KEY_COMMA": "<", "KEY_DOT": ">",
    "KEY_SLASH": "?", "KEY_SEMICOLON": ":", "KEY_APOSTROPHE": '"',
    "KEY_LEFTBRACE": "{", "KEY_RIGHTBRACE": "}", "KEY_BACKSLASH": "|",
    "KEY_GRAVE": "~",
}

_SHIFT_KEYS = {"KEY_LEFTSHIFT", "KEY_RIGHTSHIFT"}


class USBEvdevKeyboardInput:
    """Read one line at a time directly from a USB keyboard device node.

    Requires the `evdev` package and read access to `/dev/input/eventN`
    (add the systemd service's user to the `input` group). Backspace edits
    the current line, Enter submits it, Shift produces uppercase letters and
    the shifted symbol row.
    """

    def __init__(self, device_path: str | None = None) -> None:
        import evdev  # Linux-only; imported lazily so console mode never needs it installed.

        self._evdev = evdev
        self._device = self._open_device(device_path)
        try:
            self._device.grab()
        except OSError:
            # Another process already holds it, or the kernel refused
            # exclusive access. Reading still works without grab(); it just
            # means the same keystrokes could also reach an active console.
            pass

    def _open_device(self, device_path: str | None):
        evdev = self._evdev
        if device_path:
            return evdev.InputDevice(device_path)
        candidates = []
        for path in evdev.list_devices():
            device = evdev.InputDevice(path)
            capabilities = device.capabilities().get(evdev.ecodes.EV_KEY, [])
            if evdev.ecodes.KEY_A in capabilities and evdev.ecodes.KEY_ENTER in capabilities:
                candidates.append(device)
            else:
                device.close()
        if candidates:
            return candidates[0]
        raise RuntimeError(
            "No USB keyboard found under /dev/input. Set CHATBOT_KEYBOARD_DEVICE to a "
            "specific /dev/input/eventN path (check with 'evtest' or 'ls -la /dev/input/by-id'), "
            "and confirm the service user is a member of the 'input' group."
        )

    def read_message(self) -> str:
        """Block until Enter is pressed, returning the typed line."""

        evdev = self._evdev
        buffer: list[str] = []
        shift_held = False
        for event in self._device.read_loop():
            if event.type != evdev.ecodes.EV_KEY:
                continue
            key_event = evdev.categorize(event)
            keycode = key_event.keycode
            keycode = keycode[0] if isinstance(keycode, list) else keycode

            if key_event.keystate == evdev.KeyEvent.key_up and keycode in _SHIFT_KEYS:
                shift_held = False
                continue
            if key_event.keystate != evdev.KeyEvent.key_down:
                continue

            if keycode in _SHIFT_KEYS:
                shift_held = True
            elif keycode == "KEY_ENTER":
                return "".join(buffer).strip()
            elif keycode == "KEY_BACKSPACE":
                if buffer:
                    buffer.pop()
            elif keycode == "KEY_SPACE":
                buffer.append(" ")
            elif shift_held and keycode in _SHIFTED_KEY_CHARACTERS:
                buffer.append(_SHIFTED_KEY_CHARACTERS[keycode])
            elif shift_held and keycode in _KEY_CHARACTERS:
                buffer.append(_KEY_CHARACTERS[keycode].upper())
            elif keycode in _KEY_CHARACTERS:
                buffer.append(_KEY_CHARACTERS[keycode])
        return "".join(buffer).strip()
