from dataclasses import dataclass

"""
Paddle dataclass representing a player's paddle in a console-based ping pong game.

Attributes:
    x (int): The horizontal position of the paddle.
    y (int): The vertical position (top) of the paddle.
    h (int): The height of the paddle (number of cells).
    speed (int): The speed at which the paddle moves vertically.
    key_up (str): The key assigned to move the paddle up.
    key_down (str): The key assigned to move the paddle down.

Methods:
    update(dt, key, max_y):
        Updates the paddle's vertical position based on user input.
        Moves the paddle up if the 'key_up' is pressed and the paddle is not at the top boundary.
        Moves the paddle down if the 'key_down' is pressed and the paddle is not at the bottom boundary.
        The movement is scaled by 'speed' and 'dt' (delta time).

    draw(R):
        Draws the paddle on the provided rendering context 'R'.
        Iterates over the height of the paddle and sets pixels at the paddle's current position.
"""
@dataclass
class Paddle:
    x:int; y:int; h:int; speed:int; key_up:str; key_down:str
    def update(self, dt, key, max_y):
        if key==self.key_up and self.y>1:          self.y -= self.speed*dt
        elif key==self.key_down and self.y+self.h<max_y-1: self.y += self.speed*dt
    def draw(self,R):
        for i in range(self.h): R.pix(self.x, int(self.y)+i)

@dataclass
class Ball:
    x:float; y:float; vx:float; vy:float
    def update(self, dt): self.x += self.vx*dt; self.y += self.vy*dt
    def bounce_vert(self): self.vy = -self.vy
    def bounce_horiz(self): self.vx = -self.vx
    def draw(self,R): R.pix(int(self.x), int(self.y))