from tkinter import *
import threading
import numpy as np
from assets.UI import *
from assets.Tiles import *
import simpleaudio as sa
import csv

screen_width = 800
screen_height = 600
screen_tiles = 15

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

        self.canvas.bind('<Motion>', self.moved_mouse)
        self.canvas.bind('<Button-1>', self.left_click)
        self.canvas.bind('<Button-3>', self.right_click)
        # self.window.bind('<Button-3>', self.rightClick)

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
        elif self.game_state == 1:
            x, y = self.find_tile(event)
            if self.check_tile(x, y):
                self.current_board[x][y].highlight_tile(True)
                # print(x,y)
                if x != self.highlighted_tile[0] or y != self.highlighted_tile[1]:
                    self.current_board[self.highlighted_tile[0]][self.highlighted_tile[1]].highlight_tile(False)
                    self.highlighted_tile = [x,y]

    def left_click(self, event):
        if self.game_state == 0:
            for i in self.startup_screen:
                if i.get_state():
                    if (i.get_y() == 0):
                        print('Starting!')
                        self.gen_board()
                    elif (i.get_y() == 200):
                        print('About')
                    else:
                        print('Quit')
        elif self.game_state == 1:
            x, y = self.find_tile(event)
            if self.check_tile(x, y):
                self.current_board[x][y].set_path(not self.current_board[x][y].get_path())

    def right_click(self, event):
        1
                    
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
            self.startup_screen.append(Home_Button(self.canvas, x=screen_width-b_width, y=i*b_height, w=b_width, h=b_height, col=color, image=name))

        self.canvas.create_image(10, 50, anchor=NW, image = self.startup_img)
        self.game_state = 0

    def gen_board(self):

        width = int(screen_width/screen_tiles)
        
        self.canvas.delete('all')
        self.canvas.configure(width=screen_width, height=screen_width+3*width)
        self.root.winfo_toplevel().geometry("1280x940")
        self.root.configure(bg=color[1])

        self.current_board = [[Tile(self.canvas, x=i, y=j+1, w=width, col=color[1:2]) for j in range(screen_tiles)] for i in range(screen_tiles)]
            
        self.load_map(1)

        self.game_state = 1
        self.highlighted_tile = [-1, -1]

    def load_map(self, map_num):
        """ Map to load - Begin with 1 and call at beginning of every game """

        counter = 0
        with open(self.cwd + '\\assets\\maps.csv') as csvfile:
            csv_reader = csv.reader(csvfile, delimiter=',')
            for row in csv_reader:
                if counter == map_num: 
                    break
                else: counter += 1

        for tile in row:
            tile = int(tile)
            x = tile%screen_tiles - 1
            y = int(tile/screen_tiles)
            self.current_board[x][y].set_path(color=color[0])

    def find_tile(self, event):
        """ Finds x,y position of currently hoovered over tile """
        width = int(screen_width/screen_tiles)
        x = int(event.x/width)
        y = int(event.y/width) - 1
        return x, y
    
    def check_tile(self, x, y):
        """ Returns true if marked area is a viable tile """
        if (x < 0 or x > screen_tiles - 1): return False
        if (y < 0 or y > screen_tiles - 1): return False
        return True
        


    def mainloop(self):
        self.root.mainloop()

program_instance = Main()
program_instance.mainloop()
