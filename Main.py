from tkinter import *
import threading
import numpy as np

screen_width = 800

class Main():

    def __init__(self):

        # Screen Settings
        self.root = Tk()
        self.root.title('Poker TD - The Play')
        self.canvas = Canvas(self.root, width = screen_width/2, height = screen_width/3, bg='gray')
        self.canvas.pack()

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
            self.canvas.itemconfig(self.timeMarker, text=str(self.currentTime))

    def resetTimer(self):
        self.currentTime = 0

    def create_startup(self):

        self.startup_screen = []
        button_names = ['Easy', 'Intermediate', 'Hard', 'Quit']
        num_buttons = len(button_names)
        for i, name in enumerate(button_names):
            self.startup_screen.append(Button(screen_width/3, (2+2*i), screen_width/6, 1.5, button_names[i], 'red', self.canvas))
        #self.canvas.create_image(gameOffset,2*tileWidth, anchor=NW, image = self.startUpSplash)


    def mainloop(self):
        self.root.mainloop()

program_instance = Main()
program_instance.mainloop()
