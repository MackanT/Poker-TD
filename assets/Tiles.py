from assets.Enemies import Projectile
from tkinter import *
from PIL import Image, ImageTk
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

        self.tile_color = 'grass'
        
        # Tower Variables
        self.remove_tower(update=False)

        self.img_selected = self.load_image('selector', tile=True)
        self.img_tile = self.load_image('tile_' + self.tile_color, tile=True)

        self.tile = self.canvas.create_image(self.x*self.w, self.y*self.w, image=self.img_tile, anchor=NW)
        self.tower = self.canvas.create_image(self.x*self.w, self.y*self.w, image=self.img_tower, anchor=NW)
        self.select = self.canvas.create_image(self.x*self.w, self.y*self.w, image=self.img_selected, anchor=NW, state='hidden')

    def load_image(self, name, tile=False):

        print(name)

        if tile:
            bg = os.getcwd() + '\\art\\tower\\tile\\' + name + '.png' 
            bg = Image.open(bg)
            bg = bg.resize((64,64), Image.NEAREST)
            return ImageTk.PhotoImage(bg)

        if name[1:4] == '_11': name = 'single'
        elif name[0:3] == '10_': name = 'pair'
        elif name[0:2] == '9_': name = 'two_pair'
        elif name[0:2] == '8_': name = 'three_kind'
        elif name[0:2] == '7_': name = 'straight'
        elif name[0:2] == '6_': name = 'flush'
        elif name[0:2] == '5_': name = 'house'
        elif name[0:2] == '4_': name = 'four_kind'
        elif name[0:2] == '3_': name = 'straight_flush'
        elif name[0:2] == '2_': name = 'royal_straight_flush'
        elif name[0:2] == '1_': name = 'god'
        elif name[0:2] == '0_': name = 'god_like'

        bg = os.getcwd() + '\\art\\tower\\tile\\' + name + '.png' 
        bg = Image.open(bg)
        
        if name == 'single':
            number = self.get_card_number()
            suite = self.get_suite_number()
        else:
            number = self.get_card_number(single=False)
            suite = 0

        # Adding value symbol
        if suite == 0 or suite == 2: name = 'red_' + str(number) 
        else: name = 'black_' + str(number)
        fg = os.getcwd() + '\\art\\tower\\indicator\\' + name + '.png' 
        fg_1 = Image.open(fg)
        bg.paste(fg_1, (22, 1), mask=fg_1)

        # Adding suite symbol
        if name == 'single':
            fg = os.getcwd() + '\\art\\tower\\indicator\\suite_' + str(suite) + '.png' 
            fg_2 = Image.open(fg) 
            bg.paste(fg_2, (22, 22), mask=fg_2)

        bg = bg.resize((64,64), Image.NEAREST)

        return ImageTk.PhotoImage(bg)

    def set_path(self):
        self.image_name = 'tile_grey'
        self.name = 'Felt Path'
        self.attack_min = ''
        self.range = ''
        self.speed = ''
        self.ability = ''
        self.path = True
        self.buildable = False
        self.img_tile = self.load_image(self.image_name, tile=True)
        self.canvas.itemconfig(self.tile, image=self.img_tile)

    def set_tower(self, name=None, attack_min=None, attack_max=None, range=None, speed=None, ability=None, number=None, projectile=None):
        self.name = name # Card name, "Ace of Spades"
        self.number = number # Ace = 0, King = 12

        self.image_name = number
        self.img_tower = self.load_image(self.image_name)
        self.canvas.itemconfig(self.tower, image=self.img_tower)
        self.attack_min = attack_min
        self.attack_max = attack_max
        self.range = range
        self.speed = speed
        self.speed_current = speed - 1
        self.ability = ability
        self.buildable = False
        self.projectile = projectile

    def remove_tower(self, update=True):
        self.image_name = 'tile_' + self.tile_color
        self.img_tower = self.load_image('blank', tile=True)
        if update: 
            self.canvas.itemconfig(self.tower, image=self.img_tower)
        self.name = 'Felt Carpet'
        self.attack_min = 0
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

    def fire_count_down(self):
        self.speed_current += 1
        if self.speed_current >= self.speed: return True
        else: return False
    
    def fire_reset(self):
        self.speed_current = 0

    def get_buildable(self):
        return self.buildable

    def get_path(self):
        return self.path

    def get_projectile(self):
        return self.projectile

    def get_x(self):
        return self.x

    def get_y(self):
        return self.y
    
    def get_w(self):
        return self.w
    
    def get_range(self):
        return self.range
    
    def get_damage(self):
        return self.attack_min

    def get_image(self):
        return self.image_name

    def get_name(self):
        return self.name
    
    def get_number(self):
        return self.number
    
    def get_card_number(self, single=True):
        if single: i = self.number.split('_')[2]
        else: i = self.number.split('_')[1]
        return int(i)
    
    def get_suite_number(self):
        i = self.number.split('_')[0]
        return int(i)

    def get_stats(self):
        return [self.attack_min, self.speed, self.range, self.ability]

    def highlight_tile(self, state):
        if self.selected: return
        if state: 
            self.canvas.itemconfig(self.select, state='normal')
        else:
            self.canvas.itemconfig(self.select, state='hidden')