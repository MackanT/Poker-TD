from tkinter import *
import os

class Enemy:
    """ canvas, x_pos, y_pos, enemy hp, enemy speed, enemy movement goal
    """

    def __init__(self, canvas=None, x=None, y=None, hp=None, speed=None, goal=None, id=None):
        self.canvas = canvas
        self.x = x
        self.y = y
        self.hp = hp
        self.speed = speed
        self.goal = goal
        self.goal_index = 0
        self.id = id

        self.shape = self.canvas.create_rectangle(self.x, self.y, self.x+20, self.y+20, fill='green')

    
    def get_x(self):
        return self.x
    
    def get_y(self):
        return self.y

    def get_id(self):
        return self.id

    def set_goal(self, goal):
        self.goal = goal
        self.goal_index += 1

    def get_goal(self):
        return self.goal_index
    
    def do_damage(self, damage):
        self.hp -= damage
        if self.hp <= 0:
            return True
        else: return False

    def __get_dir(self):
        delta_x = self.goal[0] - self.x
        delta_y = self.goal[1] - self.y

        dir_x = 0 if delta_x == 0 else (-1 if delta_x < 0 else 1)
        dir_y = 0 if delta_y == 0 else (-1 if delta_y < 0 else 1)

        return dir_x, dir_y

    def remove(self):
        self.canvas.delete(self.shape)

    def move(self):

        dir_x0, dir_y0 = self.__get_dir()

        move_x = dir_x0*self.speed
        move_y = dir_y0*self.speed

        self.canvas.move(self.shape, move_x, move_y)

        self.x += move_x
        self.y += move_y

        dir_x1, dir_y1 = self.__get_dir()

        if dir_x0 != dir_x1 or dir_y0 != dir_y1: return True
        else: return False

class Projectile:
    """ canvas, x_pos, y_pos, amount of damage, speed of projectile [px], enemy target
    """

    def __init__(self, canvas=None, x=None, y=None, damage=None, speed=None, target=None):
        self.canvas = canvas
        self.x = x
        self.y = y
        self.damage = damage
        self.speed = speed
        self.target = target
        self.goal_index = 0

        self.shape = self.canvas.create_oval(self.x, self.y, self.x+10, self.y+10, fill='blue')

    def get_target(self):
        return self.target

    def __get_dir(self):
        delta_x = self.target.get_x() - self.x
        delta_y = self.target.get_y() - self.y

        dir_x = 0 if delta_x == 0 else (-1 if delta_x < 0 else 1)
        dir_y = 0 if delta_y == 0 else (-1 if delta_y < 0 else 1)

        return dir_x, dir_y

    def remove(self):
        self.canvas.delete(self.shape)

    def move(self):
        
        if not self.target: return True, False

        dir_x0, dir_y0 = self.__get_dir()

        # probs fix so even travel speed.....
        move_x = dir_x0*self.speed
        move_y = dir_y0*self.speed

        self.canvas.move(self.shape, move_x, move_y)

        self.x += move_x
        self.y += move_y

        dir_x1, dir_y1 = self.__get_dir()

        if dir_x0 != dir_x1 or dir_y0 != dir_y1: 
            unit_killed = self.target.do_damage(self.damage)
            return True, unit_killed
        else: 
            return False, False