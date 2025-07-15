import sys
from terminal_helpers import home, flush

class TerminalRenderer:
    """
    TerminalRenderer provides a simple in-memory frame buffer for rendering graphics in a terminal.
    Attributes:
        w (int): Width of the frame buffer (number of columns).
        h (int): Height of the frame buffer (number of rows).
        bg (str): Background character used to fill the buffer.
        buf (list[list[str]]): 2D list representing the frame buffer.
    Methods:
        clear():
            Resets the entire buffer to the background character.
        pix(x: int, y: int, ch: str = '█'):
            Sets a single pixel at (x, y) to the specified character.
            Ignores coordinates outside the buffer.
        vline(x: int, y0: int, y1: int, ch: str = '█'):
            Draws a vertical line at column x from row y0 to y1 (inclusive) using the specified character.
        hline(y: int, x0: int, x1: int, ch: str = '█'):
            Draws a horizontal line at row y from column x0 to x1 (inclusive) using the specified character.
        draw():
            Flushes the current buffer to the terminal.
            Moves the cursor to the home position, prints each row, and flushes the output.
    """

    def __init__(self, w: int, h: int, bg: str = ' '):
        self.w, self.h, self.bg = w, h, bg
        self.buf = [[bg] * w for _ in range(h)]

    # ------------- drawing primitives -------------
    def clear(self):
        for y in range(self.h):
            self.buf[y] = [self.bg] * self.w

    def pix(self, x: int, y: int, ch: str = '█'):
        if 0 <= x < self.w and 0 <= y < self.h:
            self.buf[y][x] = ch

    def vline(self, x: int, y0: int, y1: int, ch: str = '█'):
        for y in range(y0, y1 + 1):
            self.pix(x, y, ch)

    def hline(self, y: int, x0: int, x1: int, ch: str = '█'):
        for x in range(x0, x1 + 1):
            self.pix(x, y, ch)

    # ------------- flush to terminal -------------
    def draw(self):
        home()
        for row in self.buf:
            sys.stdout.write(''.join(row) + '\n')
        flush()