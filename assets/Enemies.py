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

    def move(self):

        delta_x = -1 if self.goal[0] - self.x < 0 else 1
        delta_y = -1 if self.goal[1] - self.y < 0 else 1

        self.canvas.move(self.shape, delta_x*self.speed, delta_y*self.speed)

        self.x += delta_x
        self.y += delta_y
