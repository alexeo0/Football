import tkinter as tk

root = tk.Tk()
root.title("Вертикальное футбольное поле")

WIDTH = 500
HEIGHT = 800

canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT, bg="green")
canvas.pack()

margin = 50

# Границы поля
canvas.create_rectangle(
    margin, margin,
    WIDTH - margin, HEIGHT - margin,
    outline="white", width=3
)

# Центральная линия
canvas.create_line(
    margin, HEIGHT // 2,
    WIDTH - margin, HEIGHT // 2,
    fill="white", width=3
)

# Центральный круг
radius = 60
canvas.create_oval(
    WIDTH // 2 - radius, HEIGHT // 2 - radius,
    WIDTH // 2 + radius, HEIGHT // 2 + radius,
    outline="white", width=3
)

# Центральная точка
canvas.create_oval(
    WIDTH // 2 - 4, HEIGHT // 2 - 4,
    WIDTH // 2 + 4, HEIGHT // 2 + 4,
    fill="white", outline="white"
)

# Верхняя штрафная площадь
canvas.create_rectangle(
    WIDTH // 2 - 90, margin,
    WIDTH // 2 + 90, margin + 120,
    outline="white", width=3
)

# Нижняя штрафная площадь
canvas.create_rectangle(
    WIDTH // 2 - 90, HEIGHT - margin - 120,
    WIDTH // 2 + 90, HEIGHT - margin,
    outline="white", width=3
)

# Верхняя вратарская
canvas.create_rectangle(
    WIDTH // 2 - 45, margin,
    WIDTH // 2 + 45, margin + 50,
    outline="white", width=3
)

# Нижняя вратарская
canvas.create_rectangle(
    WIDTH // 2 - 45, HEIGHT - margin - 50,
    WIDTH // 2 + 45, HEIGHT - margin,
    outline="white", width=3
)

# Верхние ворота
canvas.create_rectangle(
    WIDTH // 2 - 30, margin - 15,
    WIDTH // 2 + 30, margin,
    outline="white", width=3
)

# Нижние ворота
canvas.create_rectangle(
    WIDTH // 2 - 30, HEIGHT - margin,
    WIDTH // 2 + 30, HEIGHT - margin + 15,
    outline="white", width=3
)

root.mainloop()