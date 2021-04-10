import tkinter as tk
import math

window = tk.Tk()

screen_width = window.winfo_screenwidth()
screen_height = window.winfo_screenheight()

# perecentage of screen covered
ratio = 0.5

w = math.floor(screen_width * ratio)
h = math.floor(screen_height * ratio)
dim = str(w) + "x" + str(h)

print(str(dim))

window.geometry(dim)

test = tk.Label(text="Hello World!")
test.pack()

window.mainloop()