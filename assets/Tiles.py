from tkinter import *
import os

class Tile:
    """ x_pos, y_pos, width, height, text, color, canvas
    """

    def __init__(self, canvas, x=0, y=0, w=10):
        self.canvas = canvas

        self.x = x
        self.y = y
        self.w = w
        self.path = False

        self.tile_color = 'red'
        
        # Tower Variables
        self.remove_tower(update=False)

        self.img_selected = self.load_image('selector')
        self.img_tile = self.load_image('tile_felt_' + self.tile_color)
        self.img_suite_marker = self.load_image('blank')

        self.tile = self.canvas.create_image(self.x*self.w, self.y*self.w, image=self.img_tile, anchor=NW)
        self.tower = self.canvas.create_image(self.x*self.w, self.y*self.w, image=self.img_tower, anchor=NW)
        self.suite_marker = self.canvas.create_image(self.x*self.w, self.y*self.w, image=self.img_suite_marker, anchor=NW)
        self.select = self.canvas.create_image(self.x*self.w, self.y*self.w, image=self.img_selected, anchor=NW, state='hidden')
    
    def load_image(self, name):
        image_file = os.getcwd() + '\\art\\tower\\tile\\' + name + '.png' 
        return PhotoImage(file=image_file)

    def set_path(self):
        self.image_name = 'tile_felt_white'
        self.name = 'Felt Path'
        self.attack = ''
        self.range = ''
        self.speed = ''
        self.ability = ''
        self.path = True
        self.buildable = False
        self.img_tile = self.load_image(self.image_name)
        self.canvas.itemconfig(self.tile, image=self.img_tile)

    def set_tower(self, image=None, suite=None, name=None, attack=None, range=None, speed=None, ability=None, number=None):
        self.image_name = 'temporary' # Switch to tower images eventually when they are created
        self.img_tower = self.load_image(self.image_name)
        self.canvas.itemconfig(self.tower, image=self.img_tower)
        
        if suite != False:
            self.suite = suite
            self.img_suite_marker = self.load_image(self.suite + '_marker')
            self.canvas.itemconfig(self.suite_marker, image=self.img_suite_marker)

        self.name = name # Card name, "Ace of Spades"
        self.number = number # Ace = 0, King = 12
        self.attack = attack
        self.range = range
        self.speed = speed
        self.ability = ability
        self.buildable = False

    def remove_tower(self, update=True):
        self.image_name = 'tile_felt_' + self.tile_color
        self.img_tower = self.load_image('blank')
        if update: 
            self.canvas.itemconfig(self.tower, image=self.img_tower)
            self.canvas.itemconfig(self.suite_marker, image=self.img_tower)
        self.name = 'Felt Carpet'
        self.suite = ''
        self.attack = 0
        self.range = 0
        self.speed = 0
        self.ability = ''
        self.buildable = True
        self.selected = False

    def get_selected(self):
        return self.selected

    def deselect(self):
        self.selected = False
        self.highlight_tile(self.selected)
    
    def switch_selected(self):
        self.selected = not self.selected
        self.highlight_tile(self.selected)

    def get_buildable(self):
        return self.buildable

    def get_path(self):
        return self.path

    def get_x(self):
        return self.x

    def get_y(self):
        return self.y
    
    def get_w(self):
        return self.w
    
    def get_range(self):
        return self.range

    def get_image(self):
        return self.image_name

    def get_suite(self):
        return self.suite

    def get_name(self):
        return self.name
    
    def get_number(self):
        return self.number

    def get_stats(self):
        return [self.attack, self.speed, self.range, self.ability]

    def highlight_tile(self, state):
        if self.selected: return
        if state: 
            self.canvas.itemconfig(self.select, state='normal')
        else:
            self.canvas.itemconfig(self.select, state='hidden')