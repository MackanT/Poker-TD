from tkinter import *
import os

class Enemy:
    """ x_pos, y_pos, width, height, text, color, canvas
    """

    def __init__(self, canvas=None, x=None, y=None, hp=None, speed=None, goal=None):
        self.canvas = canvas
        self.x = x
        self.y = y
        self.hp = hp
        self.speed = speed
        self.goal = goal
        self.goal_index = 0

        self.shape = self.canvas.create_rectangle(self.x, self.y, self.x+20, self.y+20, fill='green')

    
    def get_x(self):
        return self.x
    
    def get_y(self):
        return self.y

    def set_goal(self, goal):
        self.goal = goal
        self.goal_index += 1

    def get_goal(self):
        return self.goal_index

    def __get_dir(self):
        delta_x = self.goal[0] - self.x
        delta_y = self.goal[1] - self.y

        dir_x = 0 if delta_x == 0 else (-1 if delta_x < 0 else 1)
        dir_y = 0 if delta_y == 0 else (-1 if delta_y < 0 else 1)

        return dir_x, dir_y

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