from tkinter import *
import threading
import numpy as np
from numpy import random
from assets.UI import *
from assets.Tiles import *
import simpleaudio as sa
import csv
import numpy as np
import os

# Game Design Dimensions

dimension_screen_attempt = 1000 # Dimension game will try to achieve
dimension_screen_border = 20 # Width around playing field
dimension_info_width = 296 # Width of information bar 256px + 2pcs dimension_screen_border


# Hard coded game parameters
game_tile_number = 15 
game_tile_width = int((dimension_screen_attempt - 2*dimension_screen_border)
                       /game_tile_number)


dimension_screen = game_tile_number * game_tile_width
dimension_window_width = (dimension_screen + 2*dimension_screen_border 
                          + dimension_info_width)
dimension_window_height = dimension_screen + 2*dimension_screen_border

button_fraction = 1/3


# Eventually move over to file that is read ?
color = ['#EBE8E0','#A8BBB0','#0A0A00','#A2252A'] # Color Pallette
suite = ['heart', 'spade', 'diamond', 'club']

class Main():

    def __init__(self):

        # Screen Settings
        self.root = Tk()
        self.root.winfo_toplevel().geometry("{}x{}".format(dimension_screen 
                                + dimension_screen_border, dimension_screen 
                                + 2*dimension_screen_border))
        self.root.configure(bg=color[3])
        self.root.title('Poker TD - The Play')
        self.cwd = os.getcwd()

        self.canvas_info = Canvas(self.root, width = dimension_info_width, 
                                  height = dimension_screen, bg=color[0], 
                                  bd=0, highlightthickness=0)
        self.canvas_game = Canvas(self.root, width = dimension_screen, 
                                  height = dimension_screen, bg=color[0], 
                                  bd=0, highlightthickness=0)

        self.canvas_game.place(x=dimension_screen_border, 
                               y=dimension_screen_border, anchor=NW)
        self.canvas_info.place(x=dimension_screen + dimension_screen_border, 
                               y=dimension_screen_border, anchor=NW)
        
        # -1 pre, 0 start screen, 1 in-game
        self.state_game = -1 

        self.tile_previous = [0, 0]
        self.tile_current = [-2,-2]
        self.tile_counter = 5

        # Sound
        self.sound_home_button = self.load_sound('test')
        self.sound_place_tile = self.load_sound('place')
        self.sound_place_fail = self.load_sound('place_fail')

        # Event Binders canvas_game
        self.canvas_game.bind('<Motion>', self.moved_mouse)
        self.canvas_game.bind('<Double-Button-1>', self.build_tile)
        self.canvas_game.bind('<Button-1>', self.left_click)
        # self.canvas_game.bind('<Button-2>', self.middle_click)
        self.canvas_game.bind('<Button-3>', self.right_click)

        # Event Binders canvas_info
        self.canvas_info.bind('<Motion>', self.deselect_tiles)


        #self.startTimer()

        ## Startup Screen
        self.create_startup()

        self.mainloop()

    def load_image(self, file_name, tile=True):
        if tile:
            f = self.cwd + '\\art\\tower\\tile\\' + file_name + '.png'
        else:
            f = self.cwd + '\\art\\tower\\thumbnail\\' + file_name + '.png'
        return PhotoImage(file=f)    

    def load_sound(self, file_name):
        """ loads specified sound file as wave object """
        return sa.WaveObject.from_wave_file(self.cwd 
                        + '\\sound\\' + file_name + '.wav')

    def play_sound(self, file_name):
        """ Plays specified sound file """ 
        if file_name == 'home_button':
            self.sound_home_button.play()
        elif file_name == 'place_tower':
            self.sound_place_tile.play()
        elif file_name == 'place_fail':
            self.sound_place_fail.play()

    def start_timer(self):
        threading.Timer(1.0, self.startTimer).start()
        if self.booleanGameActive == True:
            self.currentTime += 1
            #self.canvas_game.itemconfig(self.timeMarker, text=str(self.currentTime))

    def reset_timer(self):
        self.currentTime = 0

    def home_button_sound(self, event):
        if (event.x > dimension_screen*button_fraction):
            for i in self.startup_screen:
                if i.check_pos(event.x, event.y):
                    self.play_sound('home_button')

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
        if (self.state_game == 0): self.home_button_sound(event)
        elif self.state_game == 1: self.select_tile(event)

    def select_tile(self, event):
        """ Checks if current position is ok and sets its state accordingly"""
        x, y = self.find_tile(event)
        if not self.check_tile(x, y): return

        self.tile_current = [x, y]
        if self.tile_current != self.tile_previous:
            self.get_tile(x,y).highlight_tile(True)
            self.current_board[self.tile_previous[0]][self.tile_previous[1]].highlight_tile(False)
            self.update_tile_information(x,y)
            self.tile_previous = [x, y]

    def deselect_tiles(self, event):
        """ Deselects current tile """
        # Break out if not in game
        if self.state_game != 1: return
        self.current_board[self.tile_current[0]][self.tile_current[1]].highlight_tile(False)
        self.tile_previous = [-1, -1]

    def left_click(self, event):
        if self.state_game == 0: self.home_button_functions()
        elif self.state_game == 1:
            x, y = self.find_tile(event)
            if self.check_tile(x, y):
                1
                    
    def right_click(self, event):
        # Break out if not in game
        if self.state_game != 1: return
    
        x, y = self.find_tile(event)
        if self.check_tile(x, y):
            print(x,y)
            self.get_tile(x,y).set_border()

    def build_tile(self, event):
        if self.state_game == 1 and self.tile_counter > 0:
            x, y = self.find_tile(event)
            if self.check_tile(x, y):
                tile = self.get_tile(x,y)
                if tile.get_buildable():

                    col, value = self.gen_card()
                    img_name = col + '_' + str(value)

                    tile.set_tower(image=img_name, name=col + ' ' + str(value), 
                                   suite=col, value=value, attack=3, range=2, 
                                   speed=1, ability=None)
                    self.tile_counter -= 1
                    self.play_sound('place_tower')
                    self.update_tile_information(x, y)
                else:
                    self.play_sound('place_fail')
        elif self.tile_counter == 0: self.play_sound('place_fail')

    def create_startup(self):

        self.startup_screen = []

        b_names = ['play', 'about', 'quit']
        b_num = len(b_names)

        b_height = int(dimension_screen / b_num)
        b_width = int(dimension_screen*button_fraction)

        ## Imagery
        image_filename = self.cwd + "\\art\\startup\\main_img_border.png"
        self.startup_img = PhotoImage(file=image_filename)

        for i, name in enumerate(b_names):
            self.startup_screen.append(Home_Button(self.canvas_game, x=dimension_screen-b_width, y=i*b_height, w=b_width, h=b_height, col=color, image=name))

        self.canvas_game.create_image(5, 50, anchor=NW, image = self.startup_img)
        self.state_game = 0

    def gen_board(self):
        
        self.canvas_game.delete('all')
        self.root.winfo_toplevel().geometry("{}x{}".format(
                                dimension_screen + dimension_info_width 
                                + 2*dimension_screen_border, dimension_screen 
                                + 2*dimension_screen_border))

        self.current_board = [[Tile(self.canvas_game, x=i, y=j, 
                                    w=game_tile_width) 
                                    for j in range(game_tile_number)] 
                                    for i in range(game_tile_number)]
            
        self.load_map(1)

        self.state_game = 1
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
            x = tile%game_tile_number - 1
            y = int(tile/game_tile_number)
            self.get_tile(x,y).set_path()

    def find_tile(self, event):
        """ Finds x,y position of currently hoovered over tile """
        x = int(event.x/game_tile_width)
        y = int(event.y/game_tile_width)
        return x, y

    def get_tile(self, x, y):
        """ Returns reference to requested tile """
        return self.current_board[x][y]

    def check_tile(self, x, y):
        """ Returns true if marked area is a viable tile """
        if (x < 0 or x > game_tile_number - 1): return False
        if (y < 0 or y > game_tile_number - 1): return False
        return True

    def update_tile_information(self, x, y):
        tile = self.get_tile(x,y)

        img = tile.get_image()
        self.tile_image_image = self.load_image(img, tile=False)
        self.canvas_info.itemconfig(self.tile_image, image=self.tile_image_image)
        self.canvas_info.itemconfig(self.tile_image_name, text=tile.get_name())

        stats = tile.get_stats()
        for i, stat in enumerate(stats):
            self.canvas_info.itemconfig(int(self.tile_image_stat_values[i]), text=stat)

    def __create_tile_information(self):

        self.tile_image_image = self.load_image('blank')
        self.tile_image = self.canvas_info.create_image(
                            dimension_screen_border, dimension_screen_border, 
                            anchor=NW, image=self.tile_image_image)

        self.tile_image_name = self.canvas_info.create_text(
                            dimension_screen_border, 300, anchor=NW, 
                            text='', font=('Arial', 25))

        stats = ['Attack', 'Speed', 'Range', 'Ability']
        self.tile_image_stats = []

        for i, stat in enumerate(stats):
            self.tile_image_stats.append(self.canvas_info.create_text(dimension_screen_border, 320 + 40*(i+1), anchor=NW, text=stat+': ', font=('Arial', 15)))
        stats = ['', '', '', 'TBA']
        self.tile_image_stat_values = []
        for i, stat in enumerate(stats):
            self.tile_image_stat_values.append(self.canvas_info.create_text(dimension_screen_border + 80, 320 + 40*(i+1), anchor=NW, text=stat, font=('Arial', 15)))

    def gen_card(self, odds=None):

        # Add odds eventually
        color_num = np.random.randint(4)
        value_num = np.random.randint(13)

        return suite[color_num], value_num


    def mainloop(self):
        self.root.mainloop()

program_instance = Main()
program_instance.mainloop()
