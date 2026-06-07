import tkinter as tk
import math

root = tk.Tk()
root.title("Вертикальное футбольное поле")

############################
width = 500
height = 735
margin = 50

canvas = tk.Canvas(root, width=width, height=height, bg="green")
canvas.pack()

###################################
canvas.create_rectangle(margin, margin, width - margin, height - margin, outline="white", width=3)
canvas.create_line(margin, height // 2, width - margin, height // 2, fill="white", width=3)
# центр
canvas.create_oval(width // 2 - 60, height // 2 - 60, width // 2 + 60, height // 2 + 60, outline="white", width=3)
canvas.create_oval(width // 2 - 4, height // 2 - 4, width // 2 + 4, height // 2 + 4, fill="white", outline="white")
# штрафные
canvas.create_rectangle(width // 2 - 90, margin, width // 2 + 90, margin + 120, outline="white", width=3)
canvas.create_rectangle(width // 2 - 90, height - margin - 120, width // 2 + 90, height - margin, outline="white", width=3)
# вратарские
canvas.create_rectangle(width // 2 - 45, margin, width // 2 + 45, margin + 50, outline="white", width=3)
canvas.create_rectangle(width // 2 - 45, height - margin - 50, width // 2 + 45, height - margin, outline="white", width=3)
# ворота
canvas.create_rectangle(width // 2 - 30, margin - 15, width // 2 + 30, margin, outline="white", width=3)
canvas.create_rectangle(width // 2 - 30, height - margin, width // 2 + 30, height - margin + 15, outline="white", width=3)

#######################
# параметры игрока
player_radius = 14
player_speed = 3
turn_senor = 4

player_x = width / 2
player_y = height / 2
player_angle = 0.0

keys_pressed = set()

##############################################
player_circle = canvas.create_oval(player_x - player_radius, player_y - player_radius, player_x + player_radius, player_y + player_radius, fill="red", outline="darkred", width=2)
player_line = canvas.create_line(player_x, player_y, player_x, player_y - player_radius, fill="white", width=2)

######################
def update_visuals():
    canvas.coords(player_circle, player_x - player_radius, player_y - player_radius, player_x + player_radius, player_y + player_radius)
    rad = math.radians(player_angle)
    canvas.coords(player_line, player_x, player_y, player_x + math.sin(rad) * player_radius, player_y - math.cos(rad) * player_radius)

def game_loop():
    global player_x, player_y, player_angle
    # поворот
    if "a" in keys_pressed: player_angle -= turn_senor
    if "d" in keys_pressed: player_angle += turn_senor
    # движение
    if "w" in keys_pressed:
        rad = math.radians(player_angle)
        new_x = max(margin + player_radius, min(width - margin - player_radius, player_x + math.sin(rad) * player_speed))
        new_y = max(margin + player_radius, min(height - margin - player_radius, player_y - math.cos(rad) * player_speed))
        player_x, player_y = new_x, new_y
    update_visuals()
    root.after(16, game_loop)

###############################
def on_press(event): keys_pressed.add(event.keysym.lower())
def on_release(event): keys_pressed.discard(event.keysym.lower())

root.bind("<KeyPress>", on_press)
root.bind("<KeyRelease>", on_release)

game_loop()
root.mainloop()