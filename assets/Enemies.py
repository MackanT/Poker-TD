from tkinter import *
from PIL import Image, ImageTk
import numpy as np
import os

class Enemy:
    """ canvas, x_pos, y_pos, enemy hp, enemy speed, enemy movement goal
    """

    def __init__(self, canvas=None, id=None):
        self.canvas = canvas
        self.x = -10
        self.y = -10
        self.hp = 100
        self.hp_max = 100
        self.speed = 0
        self.ability = None
        self.armor = 100
        self.name = ''
        self.goal = None
        self.goal_index = 0
        self.id = id
        self.is_alive = False
        self.tick_cooldown = 0

    def reset_mob(self, x=None, y=None, hp=None, speed=None, goal=None, armor=None, ability=None, name=None, image=None):
        self.x = x
        self.y = y
        self.hp_max = hp
        self.hp = hp
        self.speed = speed
        self.armor = armor
        self.ability = ability
        self.name = name
        self.goal = goal
        self.image = image
        self.goal_index = 0
        self.is_alive = True
        self.ticks = 0
        
        self.shape = self.canvas.create_image(self.x, self.y, image=self.image)
        self.hp_bar = self.canvas.create_rectangle(self.x-15, self.y+40, self.x+15, self.y+35, fill='blue', state='hidden')

    def set_alive(self):
        self.is_alive = True

    def get_x(self):
        return self.x
    
    def get_y(self):
        return self.y

    def get_id(self):
        return self.id

    def get_alive(self):
        return self.is_alive

    def set_goal(self, goal):
        self.goal = goal
        self.goal_index += 1

    def get_goal(self):
        return self.goal_index
    
    def do_damage(self, damage):
        self.hp -= damage
        self.canvas.itemconfig(self.hp_bar, state='normal')
        self.update_hp_bar()
        self.tick_cooldown = 0
        if self.hp <= 0:
            return True
        else: return False

    def update_hp_bar(self):
        # 15 = size of "one side" of full hp bar
        size = int(self.hp / self.hp_max * 15)
        self.canvas.coords(self.hp_bar, self.x-size, self.y+40, self.x+size, self.y+35)

    def __get_dir(self):
        delta_x = self.goal[0] - self.x
        delta_y = self.goal[1] - self.y

        dir_x = 0 if delta_x == 0 else (-1 if delta_x < 0 else 1)
        dir_y = 0 if delta_y == 0 else (-1 if delta_y < 0 else 1)

        return dir_x, dir_y

    def remove(self):
        self.is_alive = False
        self.canvas.delete(self.shape)
        self.canvas.delete(self.hp_bar)
        
    def move(self):

        if self.goal == None: 
            print('da')
            return False

        self.ticks += 1

        # Hide hp_bar
        self.tick_cooldown +=1
        if self.tick_cooldown > 25:
            self.canvas.itemconfig(self.hp_bar, state = 'hidden')

        dir_x0, dir_y0 = self.__get_dir()

        move_x = dir_x0*self.speed
        move_y = dir_y0*self.speed

        sin_y = np.sin(self.ticks)*5

        self.canvas.move(self.shape, move_x, move_y+sin_y)
        self.canvas.move(self.hp_bar, move_x, move_y)

        self.x += move_x
        self.y += move_y

        dir_x1, dir_y1 = self.__get_dir()

        if dir_x0 != dir_x1 or dir_y0 != dir_y1: return True
        else: return False

class Projectile:
    """ canvas, x_pos, y_pos, amount of damage, speed of projectile [px], enemy target
    """

    def __init__(self, canvas=None, x=None, y=None, damage=None, speed=None, target=None, image=None, homing=False, age=20, size=10, scale=1):
        self.canvas = canvas
        self.x = x
        self.y = y
        self.damage = damage
        self.speed = speed
        self.target = target
        self.goal_index = 0
        self.size = size #Projectile boundary box radius
        self.max_age = age #Projectile life length num. ticks
        self.age = 1
        self.image_name = image
        self.homing = homing
        self.scale = scale

        self.image_raw = self.load_image()
        self.image = ImageTk.PhotoImage(self.image_raw)
        self.shape = self.canvas.create_image(self.x, self.y, image=self.image)
        self.update_image(0,0)

    def get_target(self):
        return self.target
    
    def load_image(self, resize=None):
        image_file = os.getcwd() + '\\art\\projectile\\' + self.image_name + '.png' 
        image = Image.open(image_file)
        if resize != None:
            image = image.resize((resize,resize), Image.NEAREST)
        return image

    def rotate_image(self):
        if self.homing:
            # Angle between projectile and target in degrees
            angle = np.arctan2(self.target.get_y() - self.y, 
                               self.target.get_x() - self.x)*180/np.pi
            return -angle
        else: return -self.age*15%360

    def rescale_image(self):
        return int(np.log((self.rel_size**self.age))) + self.image_raw.size[0]

    def stretch_image(self):
        size = int(self.image_raw.size[0] + 10*self.age)
        return size

    def update_image(self, move_x, move_y):

        angle = self.rotate_image()
        x = self.image_raw.size[0]*self.scale
        y = self.image_raw.size[1]*self.scale

        self.image = ImageTk.PhotoImage(self.image_raw.resize((x, y), Image.NEAREST).rotate(angle))
        self.canvas.itemconfig(self.shape, image=self.image)
        self.canvas.move(self.shape, move_x, move_y)


    def remove(self):
        self.canvas.delete(self.shape)

    def dist_to_target(self):
        return ((self.x-self.target.get_x())**2
                + (self.y-self.target.get_y())**2)**0.5

    def move(self):
        
        # Get rid of projectiles older than 3 sec
        self.age += 1
        if self.age > self.max_age: return True, False

        if not self.target: return True, False
        if not self.target.get_alive(): return True, False

        delta_x = self.target.get_x() - self.x
        delta_y = self.target.get_y() - self.y

        delta_sum = abs(delta_x) + abs(delta_y)

        dir_x = delta_x / delta_sum
        dir_y = delta_y / delta_sum

        move_x = dir_x*self.speed
        move_y = dir_y*self.speed

        self.x += move_x
        self.y += move_y
        
        if self.dist_to_target() < self.size:
            unit_killed = self.target.do_damage(self.damage)
            return True, unit_killed
        else:
            self.update_image(move_x, move_y)

        return False, False