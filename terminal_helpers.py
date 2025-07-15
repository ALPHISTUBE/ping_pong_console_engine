import os
import sys

ESC = "\x1b["
# ---------------- ANSI helpers ----------------
def _write(seq: str) -> None:
    """Low‑level write + flush"""
    sys.stdout.write(seq)
    sys.stdout.flush()
def clear():
    _write(ESC + "2J")

def hide():
    _write(ESC + "?25l")

def show():
    _write(ESC + "?25h")

def home():
    _write(ESC + "H")

def flush():
    sys.stdout.flush()


# ---------------- Cross‑platform key poller ----------------

class KeyPoller:
    """
    KeyPoller is a cross-platform, non-blocking single-key reader for console applications.
    Features:
    - Works on both Windows and Unix-like systems.
    - Normalizes arrow key inputs to 'UP' and 'DOWN' strings.
    - Designed for use as a context manager to safely manage terminal state.
    - Returns '' (empty string) when no key is pressed, allowing polling without blocking.
    Usage Example:
                key = keys.poll()
                if key:
                    print(f"Key pressed: {key}")
    Methods:
    - __init__(): Detects platform and sets up required modules.
    - __enter__(): On Unix, switches terminal to cbreak mode for immediate key reads.
    - __exit__(): Restores original terminal settings on Unix.
    - __del__(): Ensures terminal restoration if context manager is not used.
    - poll(): Returns a normalized key string or '' if no key is pressed.
        - On Windows, uses msvcrt to check and read key presses.
        - On Unix, uses select to poll stdin and reads escape sequences for arrow keys.
    Arrow Key Handling:
    - Windows: Arrow keys are detected by a prefix byte followed by a code byte.
    - Unix: Arrow keys are detected by escape sequences (e.g., '\x1b[A' for 'UP').
    Notes:
    - Always use KeyPoller as a context manager to avoid leaving the terminal in an inconsistent state.
    - Only 'UP' and 'DOWN' arrow keys are normalized; other special keys return ''.
    - Regular keys are returned as lowercase strings.
    Non‑blocking single‑key reader that normalises arrow keys to 'UP' / 'DOWN'.

    Usage:
        with KeyPoller() as keys:
            while True:
                k = keys.poll()
    """

    def __init__(self):
        self.is_windows = os.name == "nt"
        if self.is_windows:
            import msvcrt  # Windows std‑lib
            self.msvcrt = msvcrt
        else:
            import tty, termios, select  # Unix std‑lib
            self.tty, self.termios, self.select = tty, termios, select
            self.fd = self.old = None

    # ----- context‑manager boilerplate -----
    def __enter__(self):
        if not self.is_windows:
            self.fd = sys.stdin.fileno()
            self.old = self.termios.tcgetattr(self.fd)
            self.tty.setcbreak(self.fd)
        return self

    def __exit__(self, *_):
        if not self.is_windows and self.old is not None:
            self.termios.tcsetattr(self.fd, self.termios.TCSADRAIN, self.old)

    def __del__(self):
        """Insurance: restore terminal even if user forgets to use *with*."""
        self.__exit__()

    # ----- poll -----
    def poll(self) -> str:
        """Return one normalised key or ''. Arrow‑up/down → 'UP'/'DOWN'."""
        if self.is_windows:
            if not self.msvcrt.kbhit():
                return ''
            ch = self.msvcrt.getch()
            # Arrow keys: prefix 0x00 or 0xE0, then real code
            if ch in (b'\x00', b'\xe0'):
                code = self.msvcrt.getch()
                if code == b'H':
                    return 'UP'
                if code == b'P':
                    return 'DOWN'
                return ''
            return ch.decode(errors='ignore').lower()

        # ------- Unix path -------
        dr, *_ = self.select.select([sys.stdin], [], [], 0)
        if not dr:
            return ''
        c = sys.stdin.read(1)
        if c == '\x1b':  # potential escape sequence
            # Peek for '[A' or '[B'
            if self.select.select([sys.stdin], [], [], 0)[0]:
                nxt = sys.stdin.read(1)
                if nxt == '[' and self.select.select([sys.stdin], [], [], 0)[0]:
                    nxt2 = sys.stdin.read(1)
                    if nxt2 == 'A':
                        return 'UP'
                    if nxt2 == 'B':
                        return 'DOWN'
            return ''  # Unknown escape sequence
        return c.lower()