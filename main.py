from terminal_helpers import clear, hide, show, KeyPoller
from renderer import TerminalRenderer
from gameobjects import Paddle, Ball
import time, random

WIN_SCORE = 4  # Number of points needed to win the game

def choose_mode() -> int:
    show(); clear()
    print("==== Terminal Pong ====".center(60))
    print("1) Player vs Player")
    print("2) Player vs Computer")
    while True:
        choice = input("Select mode (1/2): ").strip()
        if choice in {'1', '2'}:
            return int(choice)
        print("Invalid choice. Try again.")

def main():
    W, H = 60, 22              # Terminal width and height (extra rows for borders)
    mode = choose_mode()        # Game mode selection
    clear(); hide()             # Prepare terminal for game

    R = TerminalRenderer(W, H, ' ')  # Renderer for drawing game objects

    # Initialize paddles: left (Player 1) and right (Player 2 or Computer)
    p1 = Paddle(1, H // 2 - 2, 4, 30, 'w', 's')          # Player 1: W/S keys
    p2 = Paddle(W - 2, H // 2 - 2, 4, 30, 'UP', 'DOWN')  # Player 2: Arrow keys

    ball = Ball(W / 2, H / 2, 25, 12)  # Ball starts in center with initial velocity
    score = [0, 0]                     # [Player 1 score, Player 2/Computer score]

    fps = 30
    dt = 1 / fps                       # Fixed time step for physics
    speed_factor = 1.003               # Ball speed increases slightly over time

    rng = random.Random()              # Random generator for ball direction and AI

    with KeyPoller() as keys:          # Start polling keyboard input
        last_time = time.time()
        while True:
            key = keys.poll()          # Get latest key press
            if key == 'q':             # Quit game if 'q' is pressed
                break

            # ---------- Player and AI Input ----------
            # Player 1 always uses W/S keys
            p1.update(dt, key, H - 1)

            if mode == 1:  # Player vs Player: Player 2 uses arrow keys
                p2.update(dt, key, H - 1)
            else:  # Player vs Computer: Simple AI for paddle movement
                center = p2.y + p2.h / 2
                if rng.random() < 0.7:  # 70% chance to track ball perfectly
                    if ball.y < center - 1:
                        p2.y -= p2.speed * dt
                    elif ball.y > center + 1:
                        p2.y += p2.speed * dt
                else:  # 30% chance to move sluggishly (40% speed)
                    if ball.y < center - 1:
                        p2.y -= p2.speed * 0.4 * dt
                    elif ball.y > center + 1:
                        p2.y += p2.speed * 0.4 * dt
                # Clamp paddle position within arena bounds
                p2.y = max(1, min(p2.y, H - 2 - p2.h))

            # ---------- Physics Tick (Fixed Time Step) ----------
            now = time.time()
            elapsed = now - last_time
            while elapsed > dt:
                ball.update(dt)            # Update ball position
                ball.vx *= speed_factor    # Gradually increase ball speed
                ball.vy *= speed_factor
                elapsed -= dt
            last_time = now

            # ---------- Wall and Paddle Collisions ----------
            # Bounce off top and bottom walls
            if ball.y <= 1:
                ball.y = 1; ball.bounce_vert()
            if ball.y >= H - 2:
                ball.y = H - 2; ball.bounce_vert()

            # Bounce off paddles if ball is at correct x and within paddle y range
            if int(ball.x) == p1.x + 1 and p1.y <= ball.y <= p1.y + p1.h:
                ball.bounce_horiz()
            if int(ball.x) == p2.x - 1 and p2.y <= ball.y <= p2.y + p2.h:
                ball.bounce_horiz()

            # ---------- Scoring ----------
            # Ball exits left: Player 2/Computer scores
            if ball.x < 0:
                score[1] += 1
                ball = Ball(W / 2, H / 2, 25, rng.choice([-12, 12]))
            # Ball exits right: Player 1 scores
            elif ball.x > W - 1:
                score[0] += 1
                ball = Ball(W / 2, H / 2, -25, rng.choice([-12, 12]))

            # ---------- Win Check ----------
            if score[0] >= WIN_SCORE or score[1] >= WIN_SCORE:
                winner = (
                    "Player 1" if score[0] >= WIN_SCORE else
                    ("Computer" if mode == 2 else "Player 2")
                )
                R.clear()
                msg = f"{winner} wins!"
                sx = (W - len(msg)) // 2
                sy = H // 2
                for i, ch in enumerate(msg):
                    R.pix(sx + i, sy, ch)
                R.draw()
                show()
                print("\nPress any key to exit…", end='')
                while keys.poll() == '':
                    time.sleep(0.05)
                clear(); show()
                return

            # ---------- Render Frame ----------
            R.clear()
            R.hline(0, 0, W - 1, '=')          # Top border
            R.hline(H - 1, 0, W - 1, '=')      # Bottom border
            R.vline(W // 2, 1, H - 2, '.')     # Center dotted line

            p1.draw(R); p2.draw(R); ball.draw(R)  # Draw paddles and ball

            # Draw score at top center
            score_txt = f"{score[0]} : {score[1]}"
            ix = (W - len(score_txt)) // 2
            for i, ch in enumerate(score_txt):
                R.pix(ix + i, 0, ch)

            R.draw()
            time.sleep(max(0.0, dt - (time.time() - now)))  # Maintain frame rate

    clear(); show()  # Restore terminal on exit

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        clear(); show()