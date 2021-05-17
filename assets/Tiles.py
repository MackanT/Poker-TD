from tkinter import *
import os

class Tile:
    """ x_pos, y_pos, width, height, text, color, canvas
    """

    def __init__(self, canvas, x=0, y=0, w=10, col=None):
        self.canvas = canvas

        self.x = x
        self.y = y
        self.w = w
        self.path = False
        if col != None: self.col = col
        else: self.col = 'white'

        self.tile = self.canvas.create_rectangle(self.x*self.w, self.y*self.w, (self.x+1)*self.w, (self.y+1)*self.w, fill=self.col)
        self.select = self.canvas.create_rectangle(self.x*self.w, self.y*self.w, (self.x+1)*self.w, (self.y+1)*self.w, fill='red', outline='', stipple='gray50', state='hidden')

    def set_path(self, color='red'):
        self.col = color
        self.path = True
        self.canvas.itemconfig(self.tile, fill=self.col, outline='')

    def get_path(self):
        return self.path

    def highlight_tile(self, state):
        if state: 
            self.canvas.itemconfig(self.select, state='normal')
        else:
            self.canvas.itemconfig(self.select, state='hidden')