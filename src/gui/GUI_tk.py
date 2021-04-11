import tkinter as tk
import math

class GUI:

    def __init__(self):
        self.RATIO = 0.6
        self.window = tk.Tk()
        self.menu = tk.Frame(self.window)
        self.article = tk.Frame(self.window)

    def get_std_size(self):
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()

        w = math.floor(screen_width * self.RATIO)
        h = math.floor(screen_height * self.RATIO)

        return (w, h)

    def start_resize(self):
        w, h = self.get_std_size()
        dim = str(w) + "x" + str(h)
        self.window.geometry(dim)

    def set_basic_layout(self):
        MENU_RATIO = 0.25

        w, h = self.get_std_size()

        menu_width = math.floor(MENU_RATIO * w)
        article_width = math.floor((1 - MENU_RATIO) * w)

        self.menu = tk.Frame(self.window, width=menu_width, borderwidth=1)
        self.article = tk.Frame(self.window, width=article_width)

        self.menu.pack(side="left", fill="both", expand=True)
        self.article.pack(side="right", fill="both", expand=True)


    def show(self):
        # constants for easy access
        WINDOW_TITLE = "IAS Project"
        window = self.window
        window.minsize(600, 300)

        window.title(WINDOW_TITLE)
        self.start_resize()

        self.set_basic_layout()

        # start window
        window.mainloop()
