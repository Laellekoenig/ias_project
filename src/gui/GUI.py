import tkinter as tk
import math

class GUI:

    def __init__(self):
        self.window = tk.Tk()

    def resize(self, ratio):
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()

        w = math.floor(screen_width * ratio)
        h = math.floor(screen_height * ratio)

        dim = str(w) + "x" + str(h)
        self.window.geometry(dim)


    def show(self):
        self.resize(0.5)
        self.window.mainloop()

    '''
    test = tk.Label(text="Hello World!")
    test.pack()
    '''