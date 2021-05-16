from tkinter import *
import threading
import numpy as np
from assets.UI import Button
import simpleaudio as sa

screen_width = 800
screen_height = 600
button_fraction = 1/3

#color = ['#613659','#211522','#C197D2','#D3B1C2'] # Color Pallette
color = ['#EBE8E0','#A8BBB0','#0A0A00','#A2252A'] # Color Pallette

class Main():

    def __init__(self):

        # Screen Settings
        self.root = Tk()
        self.root.title('Poker TD - The Play')
        self.cwd = 'C:\\Users\\Thomas Ortenberg\\Desktop\\Poker-TD'
        self.canvas = Canvas(self.root, width = screen_width, height = screen_height, bg=color[0])
        self.canvas.pack()

        self.game_state = -1 # -1 pre, 0 start screen, 1 in-game

        # sound
        self.wave_obj = sa.WaveObject.from_wave_file(self.cwd + '\\sound\\test.wav')

        self.root.bind('<Motion>', self.moved_mouse)
        # self.window.bind('<Button-1>', self.leftClick)
        # self.window.bind('<Button-2>', self.middleClick)
        # self.window.bind('<Button-3>', self.rightClick)
        # self.window.bind('<space>', self.middleClick)

        #self.startTimer()

        ## Startup Screen
        self.create_startup()

        self.mainloop()

    def startTimer(self):
        threading.Timer(1.0, self.startTimer).start()
        if self.booleanGameActive == True:
            self.currentTime += 1
            #self.canvas.itemconfig(self.timeMarker, text=str(self.currentTime))

    def resetTimer(self):
        self.currentTime = 0

    def moved_mouse(self, event):
        if (self.game_state == 0):

            if (event.x > screen_width*button_fraction):
                for i in self.startup_screen:
                    state = i.check_pos(event.x, event.y)
                    if state:
                        play_obj = self.wave_obj.play()

    def create_startup(self):

        self.startup_screen = []

        b_names = ['play', 'about', 'quit']
        b_num = len(b_names)

        b_height = int(screen_height / b_num)
        b_width = int(screen_width*button_fraction)

        ## Imagery
        image_filename = self.cwd + "\\art\\startup\\main_img_border.png"
        self.startup_img = PhotoImage(file=image_filename)

        for i, name in enumerate(b_names):
            self.startup_screen.append(Button(self.canvas, x=screen_width-b_width, y=i*b_height, w=b_width, h=b_height, col=color, image=name))

        self.canvas.create_image(10, 50, anchor=NW, image = self.startup_img)
        self.game_state = 0

    def mainloop(self):
        self.root.mainloop()

program_instance = Main()
program_instance.mainloop()
