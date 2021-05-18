from tkinter import *
import threading
import numpy as np
from assets.UI import *
from assets.Tiles import *
import simpleaudio as sa
import csv

screen_width = 750
screen_height = 600
task_height = 50
screen_tiles = 15

button_fraction = 1/3

color = ['#EBE8E0','#A8BBB0','#0A0A00','#A2252A'] # Color Pallette

class Main():

    def __init__(self):

        # Screen Settings
        self.root = Tk()
        self.root.title('Poker TD - The Play')
        self.cwd = 'C:\\Users\\Thomas Ortenberg\\Desktop\\Poker-TD'

        self.top_canvas = Canvas(self.root, width = screen_width, height = 1, bg=color[0], bd=0, highlightthickness=0)
        self.bottom_canvas = Canvas(self.root, width = screen_width, height = 1, bg=color[0], bd=0, highlightthickness=0)
        self.canvas = Canvas(self.root, width = screen_width, height = screen_height, bg=color[0], bd=0, highlightthickness=0)

        self.top_canvas.pack()
        self.canvas.pack()
        self.bottom_canvas.pack()

        self.game_state = -1 # -1 pre, 0 start screen, 1 in-game

        self.tile_previous = [0, 0]
        self.tile_current = [-2,-2]
        self.tile_counter = 5

        # sound
        self.sound_home_button = sa.WaveObject.from_wave_file(self.cwd + '\\sound\\test.wav')
        self.sound_place_tile = sa.WaveObject.from_wave_file(self.cwd + '\\sound\\place.wav')
        self.sound_place_fail = sa.WaveObject.from_wave_file(self.cwd + '\\sound\\place_fail.wav')

        self.canvas.bind('<Motion>', self.moved_mouse)
        self.canvas.bind('<Double-Button-1>', self.build_tile)
        self.canvas.bind('<Button-1>', self.left_click)
        self.canvas.bind('<Button-3>', self.right_click)


        self.bottom_canvas.bind('<Motion>', self.deselect_tiles)
        self.top_canvas.bind('<Motion>', self.deselect_tiles)

        
        # self.window.bind('<Button-2>', self.middleClick)

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

    def home_button_sound(self, event):
        if (event.x > screen_width*button_fraction):
            for i in self.startup_screen:
                if i.check_pos(event.x, event.y):
                    play_obj = self.sound_home_button.play()

    def home_button_functions(self):
        for i in self.startup_screen:
            if i.get_state():
                if (i.get_y() == 0):
                    print('Starting!')
                    self.gen_board()
                elif (i.get_y() == 200):
                    print('About')
                else:
                    print('Quit')

    def moved_mouse(self, event):
        """ Fired by mouse movement, calls appropriate function depending on game state """
        if (self.game_state == 0): self.home_button_sound(event)
        elif self.game_state == 1: self.select_tile(event)

    def select_tile(self, event):
        """ Checks if current position is ok and sets its state accordingly"""
        x, y = self.find_tile(event)
        if not self.check_tile(x, y): return

        self.tile_current = [x, y]
        if self.tile_current != self.tile_previous:
            self.current_board[x][y].highlight_tile(True)
            self.current_board[self.tile_previous[0]][self.tile_previous[1]].highlight_tile(False)
            self.tile_information(x,y)
            self.tile_previous = [x, y]

    def deselect_tiles(self, event):
        """ Deselects current tile """
        # Break out if not in game
        if self.game_state != 1: return
        self.current_board[self.tile_current[0]][self.tile_current[1]].highlight_tile(False)
        self.tile_previous = [-1, -1]

    def left_click(self, event):
        if self.game_state == 0: self.home_button_functions()
        elif self.game_state == 1:
            x, y = self.find_tile(event)
            if self.check_tile(x, y):
                1
                #self.current_board[x][y].set_path(not self.current_board[x][y].get_path())
                ### Open window to "buid on tile"
                    
    def right_click(self, event):
        # Break out if not in game
        if self.game_state != 1: return
    
        x, y = self.find_tile(event)
        if self.check_tile(x, y):
            print(x,y)
            self.current_board[x][y].set_border()

    def build_tile(self, event):
        if self.game_state == 1 and self.tile_counter > 0:
            x, y = self.find_tile(event)
            if self.check_tile(x, y):
                tile = self.current_board[x][y]
                if tile.get_buildable():
                    tile.set_tower(image='temporary', name='A Long name for testing', value='Nani', attack=3, range=2, speed=1)
                    self.tile_counter -= 1
                    play_obj = self.sound_place_tile.play()
                else:
                    play_obj = self.sound_place_fail.play()
        elif self.tile_counter == 0: play_obj = self.sound_place_fail.play()

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

        self.canvas.create_image(5, 50, anchor=NW, image = self.startup_img)
        self.game_state = 0

    def gen_board(self):

        width = int(screen_width/screen_tiles)
        
        self.canvas.delete('all')
        self.canvas.configure(width=screen_width, height=screen_width)
        self.top_canvas.configure(width=screen_width, height=task_height)
        self.bottom_canvas.configure(width=screen_width, height=4*task_height)
        self.root.winfo_toplevel().geometry("1280x{}".format(screen_width + 6*task_height))
        self.root.configure(bg=color[0])

        self.current_board = [[Tile(self.canvas, x=i, y=j, w=width) for j in range(screen_tiles)] for i in range(screen_tiles)]
            
        self.load_map(1)

        self.game_state = 1
        self.__create_tile_information()

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
            self.current_board[x][y].set_path()

    def find_tile(self, event):
        """ Finds x,y position of currently hoovered over tile """
        width = int(screen_width/screen_tiles)
        x = int(event.x/width)
        y = int(event.y/width)
        return x, y
    
    def check_tile(self, x, y):
        """ Returns true if marked area is a viable tile """
        if (x < 0 or x > screen_tiles - 1): return False
        if (y < 0 or y > screen_tiles - 1): return False
        return True

    def tile_information(self, x, y):
        tile = self.current_board[x][y]
        img = tile.get_image()
        image_filename = self.cwd + '\\art\\tower\\thumbnail\\' + img + '.png'
        self.tile_image_image = PhotoImage(file=image_filename)
        self.bottom_canvas.itemconfig(self.tile_image, image=self.tile_image_image)
        self.bottom_canvas.itemconfig(self.tile_image_name, text=tile.get_name())

        stats = tile.get_stats()
        for i, stat in enumerate(stats):
            self.bottom_canvas.itemconfig(int(self.tile_image_stat_values[i]), text=stat)

    def __create_tile_information(self):

        image_filename = self.cwd + "\\art\\tower\\tile\\blank.png"
        self.tile_image_image = PhotoImage(file=image_filename)
        self.tile_image = self.bottom_canvas.create_image(20, 20, anchor=NW, image=self.tile_image_image)

        self.tile_image_name = self.bottom_canvas.create_text(200, 20, anchor=NW, text='Temporary name of tile', font=('Arial', 25))

        stats = ['Attack', 'Speed', 'Range']
        self.tile_image_stats = []
        for i, stat in enumerate(stats):
            self.tile_image_stats.append(self.bottom_canvas.create_text(200, 20 + 40*(i+1), anchor=NW, text=stat+': ', font=('Arial', 15)))
        stats = ['1', '10000', '1']
        self.tile_image_stat_values = []
        for i, stat in enumerate(stats):
            self.tile_image_stat_values.append(self.bottom_canvas.create_text(280, 20 + 40*(i+1), anchor=NW, text=stat, font=('Arial', 15)))

    def mainloop(self):
        self.root.mainloop()

program_instance = Main()
program_instance.mainloop()
