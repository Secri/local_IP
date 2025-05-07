import ctypes
import os
import sys
import threading
import time
import socket
from tkinter import *
from PIL import Image, ImageTk
import pystray
from pystray import Icon as Icon, MenuItem as MenuItem
import darkdetect

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath('.'), relative_path)

IMG_DIR = resource_path("assets/images")
OCTOPUS = f"{IMG_DIR}/octopus.png"
OCTOPUS_THUMB = f"{IMG_DIR}/octopus_thumb.png"
CLOSE = f"{IMG_DIR}/close.png"

class Application:
    def __init__(self):
        self.stop_program = False
        self.state = 0
        self.last_ip = None

        self.root = Tk()
        self.root.overrideredirect(True)

        self.root.title("MyIP Widget")
        self.root.iconbitmap(f"{IMG_DIR}\\icon.ico")

        self.detect_theme()

        # Définir une police personnalisée avec Tahoma
        self.custom_font = ("Tahoma", 14, "bold")

        self.lab1 = Label(self.root, bg=self.bg_color, padx=5)
        self.lab2 = Label(self.root, bd=0, bg=self.bg_color, fg=self.fg_color, highlightthickness=0, borderwidth=0, font=self.custom_font)
        self.lab3 = Label(self.root, bd=0, bg=self.bg_color, fg=self.fg_color, highlightthickness=0, borderwidth=0, font=self.custom_font)

        self.lab1.grid(row=1, column=1, padx=5)
        self.lab2.grid(row=2, column=1, padx=5)
        self.lab3.grid(row=3, column=1, padx=5, pady=(0, 5))

        # Créer un bouton en forme de "X" pour masquer la fenêtre
        self.close_image = ImageTk.PhotoImage(file=CLOSE)
        self.close_button = Button(self.root, image=self.close_image, cursor="hand1", bg=self.bg_color, fg=self.fg_color, bd=0, highlightthickness=0)
        self.close_button.bind("<Button-1>", lambda event: self.quit_window())
        self.close_button.grid(row=0, column=1, padx=(0, 5), pady=(5, 0), sticky="ne")

        self.icon = pystray.Icon("ping")
        self.icon.icon = Image.open(OCTOPUS_THUMB)
        self.icon.run_detached()
        self.icon.menu = (
            MenuItem('Quit', lambda: self.quit_window()),
            MenuItem('Show', self.show_window)
        )
        self.root.attributes("-alpha", 0.85)
        self.root.attributes('-topmost', True)
        self.root.configure(bg=self.bg_color)
        self.root.bind("<B1-Motion>", self.move_window)

        self.thread2 = threading.Thread(target=self.update_data)
        self.thread2.start()

    def detect_theme(self):
        theme = darkdetect.theme()

        if theme == "Dark":
            self.bg_color = "black"
            self.fg_color = "white"
        else:
            self.bg_color = "white"
            self.fg_color = "black"

    def move_window(self, event):
        self.root.geometry(f'+{event.x_root}+{event.y_root}')

    def quit_window(self):
        self.stop_program = True
        self.icon.icon = None
        self.icon.title = None
        self.icon.stop()
        self.root.destroy()

    def show_window(self):
        self.root.after(0, self.root.deiconify())

    def hide_window(self, event):
        self.root.withdraw()

    def find_ip(self):
        try:
            hostname = socket.gethostname()
            local_ip = socket.gethostbyname(hostname)
            return {"query": local_ip, "country": "IP LOCALE"}
        except Exception as e:
            print(e)
            return False

    def update_data(self):
        while not self.stop_program:
            ip = self.find_ip()
            if ip:
                ip_address = ip["query"]
                if ip_address != self.last_ip:
                    self.last_ip = ip_address
                    self.lab1.image = ImageTk.PhotoImage(image=Image.open(OCTOPUS))
                    self.lab1.config(image=self.lab1.image)
                    self.lab2.config(text=ip["country"])
                    self.lab3.config(text=ip_address)
                    self.icon.icon = Image.open(OCTOPUS_THUMB)
                    self.icon.title = ip_address
            else:
                self.last_ip = None
                self.lab1.image = ImageTk.PhotoImage(file=OCTOPUS)
                self.lab1.config(image=self.lab1.image)
                self.lab2.config(text="No Internet")
                self.lab3.config(text="")
                self.icon.icon = Image.open(OCTOPUS_THUMB)
            time.sleep(60)

    def run(self):
        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
        except:
            ctypes.windll.user32.SetProcessDPIAware()

        self.root.mainloop()
        os._exit(1)

if __name__ == '__main__':
    app = Application()
    app.run()