import tkinter as tk
import math
import random

############################
width = 500
height = 735
margin = 50

GOAL_HALF_WIDTH = 60
PENALTY_HALF_WIDTH = 180
SMALL_BOX_HALF_WIDTH = 90

root = tk.Tk()
root.title("Вертикальное футбольное поле")
canvas = tk.Canvas(root, width=width, height=height, bg="green")
canvas.pack()

player_radius = 14
player_speed = 3
turn_senor = 4
kick_power = 10
kick_accuracy = 0
player_x = width / 2
player_y = height / 2 + 100
player_angle = 0.0
keys_pressed = set()

# --- ВРАТАРЬ ИГРОКА ---
my_keeper_x = width / 2
my_keeper_y = height - margin - 10
my_keeper_radius = 10
my_keeper_speed = 4.0
my_keeper_ball_attached = False
my_keeper_kick_cooldown = 0
# Угол вратаря всегда смотрит вверх (в поле), не меняется от управления
MY_KEEPER_ANGLE = 0.0   # смотрит вверх (0 = вверх)

bot_char = None
bot_radius = 14
bot_speed = 2.5
bot_turn = 3
bot_kick_power = 8
bot_kick_accuracy = 15
bot_x = width / 2
bot_y = height / 2 - 100
bot_angle = 180.0
bot_ball_attached = False
bot_kick_cooldown = 0
bot_delay = 45
bot_wander_timer = 0
bot_steal_delay = 0

# --- ВРАТАРЬ БОТА ---
# Ходит маятником от штанги до штанги, делает маленькие прыжки к мячу
bot_keeper_x = width / 2
bot_keeper_y = margin + 10
bot_keeper_radius = 10
bot_keeper_speed = 2.0          # скорость маятника
bot_keeper_direction = 1        # направление маятника: +1 вправо, -1 влево
bot_keeper_jump_cooldown = 0    # кулдаун прыжка
bot_keeper_ball_attached = False
bot_keeper_kick_cooldown = 0

ball_radius = 8
ball_x = width / 2
ball_y = height / 2
ball_vx = 0
ball_vy = 0
ball_attached = False
goal_checked = False
last_touch = None

pillars = []
player_circle = None
player_line = None
my_keeper_circle = None
my_keeper_line = None
bot_circle = None
bot_line = None
bot_keeper_circle = None
bot_keeper_line = None
ball = None
pillar_objects = []

in_character_select = True
game_started = False
showing_random_char = False
random_char = None

puddles = []

characters = [
    {"name": "Гаяр",     "color": "black",  "outline": "darkred",    "radius": 14, "speed": 4.25, "turn": 4.25, "kick": 7,  "accuracy": 10},
    {"name": "Лёша",     "color": "red",    "outline": "darkred",    "radius": 14, "speed": 3.75, "turn": 4,    "kick": 6,  "accuracy": 17.5},
    {"name": "Климентий","color": "blue",   "outline": "darkblue",   "radius": 14, "speed": 3,    "turn": 4,    "kick": 20, "accuracy": 25},
    {"name": "Петя",     "color": "orange", "outline": "darkorange", "radius": 12, "speed": 4,    "turn": 6,    "kick": 9,  "accuracy": 12.5},
    {"name": "Максим",   "color": "purple", "outline": "darkviolet", "radius": 14, "speed": 3.25, "turn": 4,    "kick": 8,  "accuracy": 12.5},
    {"name": "Ростислав","color": "green",  "outline": "darkviolet", "radius": 14, "speed": 2,    "turn": 3,    "kick": 4,  "accuracy": random.randint(7, 35)},
]


def select_random_bot():
    available = [c for c in characters if c != selected_char]
    return random.choice(available)


def generate_pillars():
    global pillars
    pillars = []
    quarter_width = (width - 2 * margin) / 2
    quarter_height = (height - 2 * margin) / 2
    centers = [
        (margin + quarter_width / 2,         margin + quarter_height / 2),
        (width - margin - quarter_width / 2, margin + quarter_height / 2),
        (margin + quarter_width / 2,         height - margin - quarter_height / 2),
        (width - margin - quarter_width / 2, height - margin - quarter_height / 2),
    ]
    for cx, cy in centers:
        pillar_radius = random.randint(15, 25)
        bounce_power = random.uniform(1.5, 2.5)
        pillars.append({"x": cx, "y": cy, "radius": pillar_radius, "bounce_power": bounce_power})


def draw_pillars():
    global pillar_objects
    pillar_objects = []
    for pillar in pillars:
        x1 = pillar["x"] - pillar["radius"]
        y1 = pillar["y"] - pillar["radius"]
        x2 = pillar["x"] + pillar["radius"]
        y2 = pillar["y"] + pillar["radius"]
        obj = canvas.create_oval(x1, y1, x2, y2, fill="brown", outline="saddlebrown", width=3)
        pillar_objects.append(obj)
        hr = pillar["radius"] * 0.4
        canvas.create_oval(pillar["x"]-hr, pillar["y"]-hr, pillar["x"]+hr, pillar["y"]+hr, fill="peru", outline="")


def check_pillar_collision(x, y, radius):
    for pillar in pillars:
        dx = x - pillar["x"]
        dy = y - pillar["y"]
        distance = math.hypot(dx, dy)
        if distance < radius + pillar["radius"]:
            if distance > 0:
                nx = dx / distance
                ny = dy / distance
            else:
                nx, ny = 1, 0
            overlap = radius + pillar["radius"] - distance
            x += nx * overlap
            y += ny * overlap
            return x, y, nx, ny, pillar["bounce_power"]
    return x, y, 0, 0, 0


def generate_puddles():
    global puddles
    puddles = []
    num_puddles = random.randint(3, 6)
    for _ in range(num_puddles):
        while True:
            x = random.randint(margin + 30, width - margin - 30)
            y = random.randint(margin + 30, height - margin - 30)
            on_pillar = any(math.hypot(x - p["x"], y - p["y"]) < p["radius"] + 40 for p in pillars)
            if not on_pillar:
                break
        main_radius = random.randint(20, 50)
        puddles.append({"x": x, "y": y, "radius": main_radius, "ovals": []})
        for _ in range(random.randint(2, 4)):
            puddles[-1]["ovals"].append({
                "x": x + random.randint(-15, 15),
                "y": y + random.randint(-15, 15),
                "radius_x": main_radius + random.randint(-10, 20),
                "radius_y": main_radius * (0.5 + random.random() * 0.5),
                "alpha": random.randint(20, 40),
            })


def draw_puddles():
    for puddle in puddles:
        for oval in puddle["ovals"]:
            x1, y1 = oval["x"] - oval["radius_x"], oval["y"] - oval["radius_y"]
            x2, y2 = oval["x"] + oval["radius_x"], oval["y"] + oval["radius_y"]
            stipple = "gray75" if oval["alpha"] < 25 else ("gray50" if oval["alpha"] < 35 else "gray25")
            canvas.create_oval(x1, y1, x2, y2, fill="navy", stipple=stipple, outline="")


def is_in_puddle(x, y, radius_check=ball_radius):
    for puddle in puddles:
        for oval in puddle["ovals"]:
            dx, dy = x - oval["x"], y - oval["y"]
            if math.hypot(dx / oval["radius_x"], dy / oval["radius_y"]) < 1.0:
                return True
    return False


def draw_field():
    canvas.delete("all")
    canvas.create_rectangle(margin, margin, width - margin, height - margin, outline="white", width=3)
    canvas.create_line(margin, height // 2, width - margin, height // 2, fill="white", width=3)
    canvas.create_oval(width//2-60, height//2-60, width//2+60, height//2+60, outline="white", width=3)
    canvas.create_oval(width//2-4, height//2-4, width//2+4, height//2+4, fill="white", outline="white")
    canvas.create_rectangle(width//2-PENALTY_HALF_WIDTH, margin, width//2+PENALTY_HALF_WIDTH, margin+120, outline="white", width=3)
    canvas.create_rectangle(width//2-PENALTY_HALF_WIDTH, height-margin-120, width//2+PENALTY_HALF_WIDTH, height-margin, outline="white", width=3)
    canvas.create_rectangle(width//2-SMALL_BOX_HALF_WIDTH, margin, width//2+SMALL_BOX_HALF_WIDTH, margin+50, outline="white", width=3)
    canvas.create_rectangle(width//2-SMALL_BOX_HALF_WIDTH, height-margin-50, width//2+SMALL_BOX_HALF_WIDTH, height-margin, outline="white", width=3)
    canvas.create_rectangle(width//2-GOAL_HALF_WIDTH, margin-15, width//2+GOAL_HALF_WIDTH, margin, outline="blue", width=3, fill="darkblue")
    canvas.create_text(width//2, margin-40, text=f"{bot_char['name']} (БОТ)", font=("Arial", 14, "bold"), fill="lightblue")
    canvas.create_rectangle(width//2-GOAL_HALF_WIDTH, height-margin, width//2+GOAL_HALF_WIDTH, height-margin+15, outline="red", width=3, fill="darkred")
    canvas.create_text(width//2, height-margin+40, text=f"{selected_char['name']} (ИГРОК)", font=("Arial", 14, "bold"), fill="pink")
    draw_puddles()
    draw_pillars()


def create_game_objects():
    global player_circle, player_line, my_keeper_circle, my_keeper_line
    global bot_circle, bot_line, bot_keeper_circle, bot_keeper_line, ball

    player_circle = canvas.create_oval(
        player_x-player_radius, player_y-player_radius, player_x+player_radius, player_y+player_radius,
        fill=selected_char["color"], outline=selected_char["outline"], width=2)
    player_line = canvas.create_line(player_x, player_y, player_x, player_y-player_radius, fill="white", width=2)

    # Вратарь игрока — смотрит вверх (в поле), жёлтый
    my_keeper_circle = canvas.create_oval(
        my_keeper_x-my_keeper_radius, my_keeper_y-my_keeper_radius,
        my_keeper_x+my_keeper_radius, my_keeper_y+my_keeper_radius,
        fill="yellow", outline="darkorange", width=2)
    my_keeper_line = canvas.create_line(
        my_keeper_x, my_keeper_y,
        my_keeper_x, my_keeper_y - my_keeper_radius,
        fill="white", width=2)

    bot_circle = canvas.create_oval(
        bot_x-bot_radius, bot_y-bot_radius, bot_x+bot_radius, bot_y+bot_radius,
        fill=bot_char["color"], outline=bot_char["outline"], width=2)
    bot_line = canvas.create_line(bot_x, bot_y, bot_x, bot_y-bot_radius, fill="white", width=2)

    bot_keeper_circle = canvas.create_oval(
        bot_keeper_x-bot_keeper_radius, bot_keeper_y-bot_keeper_radius,
        bot_keeper_x+bot_keeper_radius, bot_keeper_y+bot_keeper_radius,
        fill="cyan", outline="darkblue", width=2)
    bot_keeper_line = canvas.create_line(
        bot_keeper_x, bot_keeper_y,
        bot_keeper_x, bot_keeper_y - bot_keeper_radius,
        fill="white", width=2)

    ball = canvas.create_oval(
        ball_x-ball_radius, ball_y-ball_radius, ball_x+ball_radius, ball_y+ball_radius,
        fill="white", outline="black")


loop_after_id = None


def reset_positions():
    global player_x, player_y, player_angle
    global my_keeper_x, my_keeper_y, my_keeper_ball_attached, my_keeper_kick_cooldown
    global bot_x, bot_y, bot_angle, bot_ball_attached, bot_kick_cooldown, bot_delay, bot_wander_timer, bot_steal_delay
    global bot_keeper_x, bot_keeper_y, bot_keeper_direction, bot_keeper_jump_cooldown
    global bot_keeper_ball_attached, bot_keeper_kick_cooldown
    global ball_x, ball_y, ball_vx, ball_vy, ball_attached, goal_checked, game_started, loop_after_id, last_touch

    if loop_after_id is not None:
        root.after_cancel(loop_after_id)
        loop_after_id = None

    player_x, player_y, player_angle = width/2, height/2+100, 0.0

    my_keeper_x, my_keeper_y = width/2, height - margin - 10
    my_keeper_ball_attached = False
    my_keeper_kick_cooldown = 0

    bot_x, bot_y, bot_angle = width/2, height/2-100, 180.0
    bot_ball_attached = False
    bot_kick_cooldown = 0
    bot_delay = 45
    bot_wander_timer = 0
    bot_steal_delay = 0

    bot_keeper_x, bot_keeper_y = width/2, margin+10
    bot_keeper_direction = 1
    bot_keeper_jump_cooldown = 0
    bot_keeper_ball_attached = False
    bot_keeper_kick_cooldown = 0

    ball_x, ball_y = width/2, height/2
    ball_vx, ball_vy = 0, 0
    ball_attached = False
    goal_checked = False
    last_touch = None
    game_started = False


def start():
    global in_character_select, game_started, showing_random_char, bot_char
    global bot_radius, bot_speed, bot_turn, bot_kick_power, bot_kick_accuracy
    in_character_select = False
    showing_random_char = False
    game_started = False
    bot_char = select_random_bot()
    bot_radius = bot_char["radius"]
    # Полевой бот — полегче
    bot_speed = bot_char["speed"] * 0.55
    bot_turn = bot_char["turn"] * 0.55
    bot_kick_power = bot_char["kick"] * 0.65
    bot_kick_accuracy = bot_char["accuracy"] * 1.8  # больше = менее точный
    generate_pillars()
    generate_puddles()
    reset_positions()
    draw_field()
    create_game_objects()
    game_loop()


def select_character(char):
    global selected_char, player_radius, player_speed, turn_senor, kick_power, kick_accuracy
    selected_char = char
    player_radius = char["radius"]
    player_speed = char["speed"]
    turn_senor = char["turn"]
    kick_power = char["kick"]
    kick_accuracy = char["accuracy"]
    start()


def show_random_character(char):
    global showing_random_char, random_char
    showing_random_char = True
    random_char = char
    canvas.delete("all")
    canvas.create_rectangle(0, 0, width, height, fill="darkgreen")
    canvas.create_text(width//2, height//2-80, text="СЛУЧАЙНЫЙ ВЫБОР", font=("Arial", 28, "bold"), fill="white")
    canvas.create_text(width//2, height//2-30, text="Вы играете за:", font=("Arial", 18), fill="white")
    canvas.create_text(width//2, height//2+20, text=char["name"], font=("Arial", 36, "bold"), fill=char["color"])
    canvas.create_text(width//2, height//2+60,
        text=f"Скорость: {char['speed']} | Удар: {char['kick']} | Поворот: {char['turn']} | Точность: {char['accuracy']}°",
        font=("Arial", 12), fill="white")
    x1, y1, x2, y2 = width//2-80, height//2+100, width//2+80, height//2+140
    canvas.create_rectangle(x1, y1, x2, y2, fill="gray30", outline="white", width=2)
    canvas.create_text(width//2, height//2+120, text="ИГРАТЬ", font=("Arial", 18, "bold"), fill="white")
    global random_play_button_coords
    random_play_button_coords = (x1, y1, x2, y2)


def select_random_character():
    show_random_character(random.choice(characters))


def show_character_select():
    global in_character_select
    in_character_select = True
    canvas.delete("all")
    canvas.create_rectangle(0, 0, width, height, fill="darkgreen")
    canvas.create_text(width//2, 40, text="ВЫБОР ПЕРСОНАЖА", font=("Arial", 24, "bold"), fill="white")
    rand_x1, rand_y1, rand_x2, rand_y2 = width//2-100, 70, width//2+100, 105
    canvas.create_rectangle(rand_x1, rand_y1, rand_x2, rand_y2, fill="darkorange", outline="white", width=2)
    canvas.create_text(width//2, 87, text="🎲 СЛУЧАЙНЫЙ ВЫБОР", font=("Arial", 14, "bold"), fill="white")
    global random_button_coords
    random_button_coords = (rand_x1, rand_y1, rand_x2, rand_y2)
    button_width, button_height, start_y, gap = 200, 80, 120, 20
    for i, char in enumerate(characters):
        x1 = width//2 - button_width//2
        y1 = start_y + i * (button_height + gap)
        x2, y2 = x1 + button_width, y1 + button_height
        canvas.create_rectangle(x1, y1, x2, y2, fill="gray30", outline="white", width=2)
        canvas.create_text(width//2, y1+20, text=char["name"], font=("Arial", 16, "bold"), fill=char["color"])
        canvas.create_text(width//2, y1+50,
            text=f"Скорость: {char['speed']} | Удар: {char['kick']} | Поворот: {char['turn']} | Точность: {char['accuracy']}°",
            font=("Arial", 10), fill="white")
        char["button_coords"] = (x1, y1, x2, y2)


def on_click(event):
    global in_character_select, showing_random_char
    if showing_random_char:
        x1, y1, x2, y2 = random_play_button_coords
        if x1 <= event.x <= x2 and y1 <= event.y <= y2:
            select_character(random_char)
        return
    if not in_character_select:
        return
    x1, y1, x2, y2 = random_button_coords
    if x1 <= event.x <= x2 and y1 <= event.y <= y2:
        select_random_character()
        return
    for char in characters:
        if "button_coords" in char:
            x1, y1, x2, y2 = char["button_coords"]
            if x1 <= event.x <= x2 and y1 <= event.y <= y2:
                select_character(char)
                return


def update_visuals():
    canvas.coords(player_circle,
        player_x-player_radius, player_y-player_radius, player_x+player_radius, player_y+player_radius)
    rad = math.radians(player_angle)
    canvas.coords(player_line, player_x, player_y,
        player_x + math.sin(rad)*player_radius, player_y - math.cos(rad)*player_radius)

    # Вратарь игрока — стрелка всегда смотрит вверх (в поле), не вращается
    canvas.coords(my_keeper_circle,
        my_keeper_x-my_keeper_radius, my_keeper_y-my_keeper_radius,
        my_keeper_x+my_keeper_radius, my_keeper_y+my_keeper_radius)
    canvas.coords(my_keeper_line,
        my_keeper_x, my_keeper_y,
        my_keeper_x, my_keeper_y - my_keeper_radius)

    canvas.coords(bot_circle,
        bot_x-bot_radius, bot_y-bot_radius, bot_x+bot_radius, bot_y+bot_radius)
    bot_rad = math.radians(bot_angle)
    canvas.coords(bot_line, bot_x, bot_y,
        bot_x + math.sin(bot_rad)*bot_radius, bot_y - math.cos(bot_rad)*bot_radius)

    canvas.coords(bot_keeper_circle,
        bot_keeper_x-bot_keeper_radius, bot_keeper_y-bot_keeper_radius,
        bot_keeper_x+bot_keeper_radius, bot_keeper_y+bot_keeper_radius)
    # Стрелка вратаря бота всегда вниз (в поле)
    canvas.coords(bot_keeper_line,
        bot_keeper_x, bot_keeper_y,
        bot_keeper_x, bot_keeper_y + bot_keeper_radius)

    canvas.coords(ball,
        ball_x-ball_radius, ball_y-ball_radius, ball_x+ball_radius, ball_y+ball_radius)


def end_game(scorer):
    text, color = ("ГОЛ!", "gold") if scorer == "player" else ("ПРОПУЩЕН ГОЛ!", "red")
    canvas.create_text(width//2, height//2, text=text, font=("Arial", 48, "bold"), fill=color)
    root.after(3000, start)


def check_goal():
    if width//2-GOAL_HALF_WIDTH < ball_x < width//2+GOAL_HALF_WIDTH and margin-15 < ball_y < margin:
        return "player"
    if width//2-GOAL_HALF_WIDTH < ball_x < width//2+GOAL_HALF_WIDTH and height-margin < ball_y < height-margin+15:
        return "bot"
    return None


def try_pick_ball():
    """Полевой игрок подбирает мяч."""
    global ball_attached, last_touch, bot_ball_attached, bot_keeper_ball_attached, my_keeper_ball_attached

    dx = ball_x - player_x
    dy = ball_y - player_y
    distance = math.hypot(dx, dy)

    if distance < 30:
        if bot_keeper_ball_attached:
            dist_to_keeper = math.hypot(player_x - bot_keeper_x, player_y - bot_keeper_y)
            if dist_to_keeper < bot_keeper_radius + player_radius + 20:
                bot_keeper_ball_attached = False
            else:
                return
        if my_keeper_ball_attached:
            dist_to_my_keeper = math.hypot(player_x - my_keeper_x, player_y - my_keeper_y)
            if dist_to_my_keeper < my_keeper_radius + player_radius + 20:
                my_keeper_ball_attached = False
            else:
                return
        if bot_ball_attached:
            bot_ball_attached = False
        ball_attached = True
        last_touch = "player"


def kick_ball():
    global ball_attached, ball_vx, ball_vy
    if not ball_attached:
        return
    ball_attached = False
    rad = math.radians(player_angle)
    deviation = random.uniform(-kick_accuracy, kick_accuracy)
    rad += math.radians(deviation)
    ball_vx = math.sin(rad) * kick_power
    ball_vy = -math.cos(rad) * kick_power


def update_my_keeper():
    """
    Вратарь игрока: управляется стрелками влево/вправо.
    Вперёд/назад — нельзя.
    Угол (стрелка) не меняется — всегда смотрит в поле.
    При контакте с мячом подбирает его и бьёт вперёд.
    """
    global my_keeper_x, my_keeper_ball_attached, my_keeper_kick_cooldown
    global ball_attached, ball_vx, ball_vy, last_touch, ball_x, ball_y
    global bot_ball_attached, bot_keeper_ball_attached

    if my_keeper_kick_cooldown > 0:
        my_keeper_kick_cooldown -= 1

    # Зона движения — в рамках ворот
    keeper_left  = width//2 - GOAL_HALF_WIDTH + my_keeper_radius
    keeper_right = width//2 + GOAL_HALF_WIDTH - my_keeper_radius

    if "left" in keys_pressed:
        my_keeper_x = max(keeper_left, my_keeper_x - my_keeper_speed)
    if "right" in keys_pressed:
        my_keeper_x = min(keeper_right, my_keeper_x + my_keeper_speed)

    # Подбор мяча при физическом контакте
    dist_to_ball = math.hypot(ball_x - my_keeper_x, ball_y - my_keeper_y)
    if not my_keeper_ball_attached and dist_to_ball < my_keeper_radius + ball_radius + 10:
        ball_attached = False
        bot_ball_attached = False
        bot_keeper_ball_attached = False
        my_keeper_ball_attached = True
        ball_attached = True
        last_touch = "my_keeper"

    # Удар вперёд в поле при нажатии пробела или E
    if my_keeper_ball_attached and my_keeper_kick_cooldown == 0:
        if "space" in keys_pressed or "e" in keys_pressed:
            # Бьёт вверх в поле с небольшим разбросом
            deviation = random.uniform(-15, 15)
            rad = math.radians(deviation)  # 0 = вверх, добавляем отклонение
            ball_vx = math.sin(rad) * 10
            ball_vy = -math.cos(rad) * 10
            my_keeper_ball_attached = False
            ball_attached = False
            last_touch = "my_keeper"
            my_keeper_kick_cooldown = 30


def update_bot():
    """Полевой бот — полегче."""
    global bot_x, bot_y, bot_angle, bot_ball_attached, bot_kick_cooldown, bot_delay, bot_wander_timer, bot_steal_delay
    global ball_attached, ball_vx, ball_vy, last_touch, ball_x, ball_y

    if bot_delay > 0:
        bot_delay -= 1
        return

    if bot_kick_cooldown > 0:
        bot_kick_cooldown -= 1
    if bot_steal_delay > 0:
        bot_steal_delay -= 1

    bot_wander_timer -= 1
    if bot_wander_timer <= 0:
        bot_wander_timer = random.randint(30, 70)
        if random.random() < 0.25:
            bot_angle += random.uniform(-45, 45)

    target_x = ball_x
    target_y = ball_y

    if bot_ball_attached:
        target_x = width/2 + random.uniform(-30, 30)
        target_y = height - margin + 15

    dx = target_x - bot_x
    dy = target_y - bot_y
    target_angle = math.degrees(math.atan2(dx, -dy))
    angle_diff = target_angle - bot_angle
    while angle_diff > 180:  angle_diff -= 360
    while angle_diff < -180: angle_diff += 360

    if abs(angle_diff) > bot_turn:
        bot_angle += bot_turn if angle_diff > 0 else -bot_turn
    else:
        bot_angle = target_angle

    rad = math.radians(bot_angle)
    distance_to_target = math.hypot(dx, dy)

    # Бьёт с умеренного расстояния
    kick_distance = random.randint(50, 200)
    if bot_ball_attached and distance_to_target < kick_distance and bot_kick_cooldown == 0:
        target_goal_x = width//2 + random.uniform(-30, 30)
        target_goal_y = height - margin + random.uniform(-5, 10)
        goal_dx = target_goal_x - bot_x
        goal_dy = target_goal_y - bot_y
        goal_angle = math.atan2(goal_dx, -goal_dy)
        deviation = random.uniform(-bot_kick_accuracy, bot_kick_accuracy)
        kick_rad = goal_angle + math.radians(deviation)
        ball_vx = math.sin(kick_rad) * bot_kick_power
        ball_vy = -math.cos(kick_rad) * bot_kick_power
        bot_ball_attached = False
        ball_attached = False
        last_touch = "bot"
        bot_kick_cooldown = 70  # дольше кулдаун = реже бьёт
        return

    # Отбор — медленнее реагирует
    if not bot_ball_attached and ball_attached and last_touch == "player":
        dist_to_player = math.hypot(player_x - bot_x, player_y - bot_y)
        if dist_to_player < 35:
            if bot_steal_delay == 0:
                bot_steal_delay = 40           # долгая задержка перед отбором
            elif bot_steal_delay == 1 and random.random() < 0.2:  # низкий шанс
                bot_ball_attached = True
                ball_attached = True
                last_touch = "bot"
                bot_steal_delay = 0

    # Подбор свободного мяча
    if not bot_ball_attached and not ball_attached:
        dist_to_ball = math.hypot(ball_x - bot_x, ball_y - bot_y)
        if dist_to_ball < 30 and random.random() < 0.7:
            bot_ball_attached = True
            ball_attached = True
            last_touch = "bot"

    should_move = False
    if bot_ball_attached and distance_to_target > 10:
        should_move = random.random() < 0.8
    elif not bot_ball_attached and distance_to_target > 30:
        should_move = random.random() < 0.65

    if should_move:
        current_speed = bot_speed * (0.5 if is_in_puddle(bot_x, bot_y, bot_radius) else 1.0)
        new_x = max(margin+bot_radius, min(width-margin-bot_radius, bot_x + math.sin(rad)*current_speed))
        new_y = max(margin+bot_radius, min(height-margin-bot_radius, bot_y - math.cos(rad)*current_speed))
        bot_x, bot_y = new_x, new_y


def update_bot_keeper():
    """
    Вратарь бота:
    - Ходит маятником от штанги до штанги
    - Периодически делает маленький прыжок в сторону мяча
    - НЕ следует за мячом постоянно
    - Подбирает мяч только при физическом контакте
    """
    global bot_keeper_x, bot_keeper_direction, bot_keeper_jump_cooldown
    global bot_keeper_ball_attached, bot_keeper_kick_cooldown
    global ball_attached, ball_vx, ball_vy, last_touch, ball_x, ball_y

    if bot_keeper_kick_cooldown > 0:
        bot_keeper_kick_cooldown -= 1
    if bot_keeper_jump_cooldown > 0:
        bot_keeper_jump_cooldown -= 1

    keeper_left  = width//2 - GOAL_HALF_WIDTH + bot_keeper_radius
    keeper_right = width//2 + GOAL_HALF_WIDTH - bot_keeper_radius

    # --- Маятник ---
    bot_keeper_x += bot_keeper_speed * bot_keeper_direction

    if bot_keeper_x >= keeper_right:
        bot_keeper_x = keeper_right
        bot_keeper_direction = -1
    elif bot_keeper_x <= keeper_left:
        bot_keeper_x = keeper_left
        bot_keeper_direction = 1

    # --- Маленький прыжок в сторону мяча раз в ~60 тиков ---
    if bot_keeper_jump_cooldown == 0:
        jump_amount = 18  # небольшой прыжок
        if ball_x < bot_keeper_x:
            bot_keeper_x = max(keeper_left, bot_keeper_x - jump_amount)
        else:
            bot_keeper_x = min(keeper_right, bot_keeper_x + jump_amount)
        bot_keeper_jump_cooldown = random.randint(50, 80)

    # --- Подбор мяча при физическом контакте ---
    dist_to_ball = math.hypot(ball_x - bot_keeper_x, ball_y - bot_keeper_y)
    if not bot_keeper_ball_attached and dist_to_ball < bot_keeper_radius + ball_radius + 10:
        ball_attached = False
        bot_ball_attached = False
        bot_keeper_ball_attached = True
        ball_attached = True
        last_touch = "bot_keeper"

    # --- Пас к боту ---
    if bot_keeper_ball_attached and bot_keeper_kick_cooldown == 0:
        dx = bot_x - bot_keeper_x + random.uniform(-80, 80)
        dy = abs(bot_y - bot_keeper_y) + random.uniform(50, 150)
        angle = math.atan2(dx, dy)
        power = 8
        ball_vx = math.sin(angle) * power
        ball_vy = math.cos(angle) * power
        bot_keeper_ball_attached = False
        ball_attached = False
        last_touch = "bot_keeper"
        bot_keeper_kick_cooldown = 45


def on_press(event):
    global ball_attached
    key = event.keysym.lower()
    keys_pressed.add(key)
    if key == "e":
        try_pick_ball()
    if key == "space":
        if ball_attached and last_touch == "player":
            kick_ball()
        elif my_keeper_ball_attached:
            pass  # обрабатывается в update_my_keeper
        else:
            try_pick_ball()
    if key == "q":
        ball_attached = False
        bot_ball_attached = False
        bot_keeper_ball_attached = False
        my_keeper_ball_attached = False


def on_release(event):
    keys_pressed.discard(event.keysym.lower())


def game_loop():
    global player_x, player_y, player_angle
    global my_keeper_x, my_keeper_ball_attached, my_keeper_kick_cooldown
    global bot_x, bot_y, bot_angle, bot_ball_attached, bot_kick_cooldown, bot_delay, bot_wander_timer, bot_steal_delay
    global bot_keeper_x, bot_keeper_y, bot_keeper_direction, bot_keeper_jump_cooldown
    global bot_keeper_ball_attached, bot_keeper_kick_cooldown
    global ball_x, ball_y, ball_vx, ball_vy, ball_attached, goal_checked, game_started, loop_after_id, last_touch

    if game_started:
        return
    game_started = True

    def loop():
        global player_x, player_y, player_angle
        global my_keeper_x, my_keeper_ball_attached, my_keeper_kick_cooldown
        global bot_x, bot_y, bot_angle, bot_ball_attached, bot_kick_cooldown, bot_delay, bot_wander_timer, bot_steal_delay
        global bot_keeper_x, bot_keeper_y, bot_keeper_direction, bot_keeper_jump_cooldown
        global bot_keeper_ball_attached, bot_keeper_kick_cooldown
        global ball_x, ball_y, ball_vx, ball_vy, ball_attached, goal_checked, loop_after_id, last_touch

        # Полевой игрок: повороты A/D, движение W — вперёд, S — назад
        if "a" in keys_pressed:
            player_angle -= turn_senor
        if "d" in keys_pressed:
            player_angle += turn_senor

        if "w" in keys_pressed:
            rad = math.radians(player_angle)
            current_speed = player_speed * 0.5 if is_in_puddle(player_x, player_y, player_radius) else player_speed
            new_x = max(margin+player_radius, min(width-margin-player_radius, player_x + math.sin(rad)*current_speed))
            new_y = max(margin+player_radius, min(height-margin-player_radius, player_y - math.cos(rad)*current_speed))
            new_x, new_y, nx, ny, bounce = check_pillar_collision(new_x, new_y, player_radius)
            player_x, player_y = new_x, new_y

        if "s" in keys_pressed:
            rad = math.radians(player_angle)
            current_speed = player_speed * 0.5 if is_in_puddle(player_x, player_y, player_radius) else player_speed
            new_x = max(margin+player_radius, min(width-margin-player_radius, player_x - math.sin(rad)*current_speed))
            new_y = max(margin+player_radius, min(height-margin-player_radius, player_y + math.cos(rad)*current_speed))
            new_x, new_y, nx, ny, bounce = check_pillar_collision(new_x, new_y, player_radius)
            player_x, player_y = new_x, new_y

        update_my_keeper()
        update_bot()
        update_bot_keeper()

        rad = math.radians(player_angle)

        if ball_attached:
            if last_touch == "player":
                offset = player_radius + ball_radius + 4
                ball_x = player_x + math.sin(rad) * offset
                ball_y = player_y - math.cos(rad) * offset
            elif last_touch == "bot":
                bot_rad = math.radians(bot_angle)
                offset = bot_radius + ball_radius + 4
                ball_x = bot_x + math.sin(bot_rad) * offset
                ball_y = bot_y - math.cos(bot_rad) * offset
            elif last_touch == "bot_keeper":
                offset = bot_keeper_radius + ball_radius + 4
                ball_x = bot_keeper_x
                ball_y = bot_keeper_y + offset  # мяч перед вратарём (вниз = в поле)
            elif last_touch == "my_keeper":
                offset = my_keeper_radius + ball_radius + 4
                ball_x = my_keeper_x
                ball_y = my_keeper_y - offset  # мяч перед вратарём (вверх = в поле)
        else:
            ball_x += ball_vx
            ball_y += ball_vy

            new_ball_x, new_ball_y, nx, ny, bounce_power = check_pillar_collision(ball_x, ball_y, ball_radius)
            if bounce_power > 0:
                ball_x, ball_y = new_ball_x, new_ball_y
                dot_product = ball_vx * nx + ball_vy * ny
                ball_vx = (ball_vx - 2 * dot_product * nx) * bounce_power
                ball_vy = (ball_vy - 2 * dot_product * ny) * bounce_power

            if is_in_puddle(ball_x, ball_y):
                ball_vx *= 0.95
                ball_vy *= 0.95
            else:
                ball_vx *= 0.99
                ball_vy *= 0.99

            left   = margin + ball_radius
            right  = width - margin - ball_radius
            top    = (margin - 15 + ball_radius) if (width//2-GOAL_HALF_WIDTH < ball_x < width//2+GOAL_HALF_WIDTH) else (margin + ball_radius)
            bottom = (height - margin + 15 - ball_radius) if (width//2-GOAL_HALF_WIDTH < ball_x < width//2+GOAL_HALF_WIDTH) else (height - margin - ball_radius)

            if ball_x < left:   ball_x = left;   ball_vx *= -0.8
            if ball_x > right:  ball_x = right;  ball_vx *= -0.8
            if ball_y < top:    ball_y = top;     ball_vy *= -0.8
            if ball_y > bottom: ball_y = bottom;  ball_vy *= -0.8

        scorer = check_goal()
        if not goal_checked and scorer:
            goal_checked = True
            end_game(scorer)

        update_visuals()
        loop_after_id = root.after(16, loop)

    loop()


root.bind("<KeyPress>", on_press)
root.bind("<KeyRelease>", on_release)
root.bind("<Button-1>", on_click)

show_character_select()
root.mainloop()