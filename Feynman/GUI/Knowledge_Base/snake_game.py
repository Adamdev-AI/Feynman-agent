import turtle
import time
import random


def game():
    delay = 0.1

    score = 0
    high_score = 0
    running = True

    try:
        # ---------------- Screen ----------------
        wn = turtle.Screen()
        wn.title("Snake Game")
        wn.bgcolor("green")
        wn.setup(width=600, height=600)
        wn.tracer(0)

        # ---------------- Snake ----------------
        head = turtle.Turtle()
        head.speed(0)
        head.shape("square")
        head.color("black")
        head.penup()
        head.goto(0, 0)
        head.direction = "stop"

        # ---------------- Food ----------------
        food = turtle.Turtle()
        food.speed(0)
        food.shape("circle")
        food.color("red")
        food.penup()
        food.goto(0, 100)

        segments = []

        # ---------------- Score ----------------
        pen = turtle.Turtle()
        pen.speed(0)
        pen.hideturtle()
        pen.penup()
        pen.color("white")
        pen.goto(0, 260)
        pen.write(
            "Score: 0  High Score: 0",
            align="center",
            font=("Courier", 24, "normal")
        )

        # ---------- Functions ----------
        def reset():
            nonlocal score, delay

            head.goto(0, 0)
            head.direction = "stop"

            for segment in segments:
                segment.goto(1000, 1000)

            segments.clear()

            score = 0
            delay = 0.1

            pen.clear()
            pen.write(
                f"Score: {score}  High Score: {high_score}",
                align="center",
                font=("Courier", 24, "normal")
            )

        def go_up():
            if head.direction != "down":
                head.direction = "up"

        def go_down():
            if head.direction != "up":
                head.direction = "down"

        def go_left():
            if head.direction != "right":
                head.direction = "left"

        def go_right():
            if head.direction != "left":
                head.direction = "right"

        def move():
            if head.direction == "up":
                head.sety(head.ycor() + 20)
            elif head.direction == "down":
                head.sety(head.ycor() - 20)
            elif head.direction == "left":
                head.setx(head.xcor() - 20)
            elif head.direction == "right":
                head.setx(head.xcor() + 20)

        # ---------- Keyboard ----------
        wn.listen()
        wn.onkeypress(go_up, "w")
        wn.onkeypress(go_down, "s")
        wn.onkeypress(go_left, "a")
        wn.onkeypress(go_right, "d")

        # ---------- Main Loop ----------
        while running:
            wn.update()

            # Border collision
            if (
                head.xcor() > 290
                or head.xcor() < -290
                or head.ycor() > 290
                or head.ycor() < -290
            ):
                time.sleep(1)
                reset()

            # Food collision
            if head.distance(food) < 20:
                food.goto(
                    random.randint(-290, 290),
                    random.randint(-290, 290)
                )

                segment = turtle.Turtle()
                segment.speed(0)
                segment.shape("square")
                segment.color("grey")
                segment.penup()
                segments.append(segment)

                delay = max(0.03, delay - 0.001)

                score += 10
                if score > high_score:
                    high_score = score

                pen.clear()
                pen.write(
                    f"Score: {score}  High Score: {high_score}",
                    align="center",
                    font=("Courier", 24, "normal")
                )

            # Move body
            for i in range(len(segments) - 1, 0, -1):
                segments[i].goto(
                    segments[i - 1].xcor(),
                    segments[i - 1].ycor()
                )

            if segments:
                segments[0].goto(head.xcor(), head.ycor())

            move()

            # Self collision
            for segment in segments:
                if segment.distance(head) < 20:
                    time.sleep(1)
                    reset()
                    break

            time.sleep(delay)

    except turtle.Terminator:
        print("Game window closed.")

    except KeyboardInterrupt:
        print("Game interrupted.")

    except Exception as e:
        print(f"Unexpected error: {e}")

    finally:
        try:
            turtle.bye()
        except Exception:
            pass