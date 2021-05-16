from tkinter import *
import os

class Button:
    """ x_pos, y_pos, width, height, text, color, canvas
    """

    def __init__(self, canvas, x=0, y=0, w=10, h=10, col=None, image=None, text=None):
        self.canvas = canvas

        self.x_pos = x
        self.y_pos = y
        self.width = w
        self.height = h

        self.f_size = int(w/8)

        self.state = 0 # 0 = Standard, 1 = Selected
        
        if col != None:
            self.b_color = col[3]
            self.f_color = col[0]
        else:
            self.b_color = 'white'
            self.f_color = 'black'

        self.button_area = canvas.create_rectangle(self.x_pos, self.y_pos, self.x_pos + self.width, self.y_pos + self.height, fill=self.b_color)

        if text != None: 
            self.text = text
            self.button_text = canvas.create_text(self.x_pos + self.width/2, self.y_pos + self.height/2, text=text, fill=self.f_color, font=('Arial', self.f_size))
        elif (image != None):
            image_file = os.getcwd() + '\\art\\startup\\base_' + image + '.png'
            self.base_img = PhotoImage(file=image_file)
            image_file = os.getcwd() + '\\art\\startup\\select_' + image + '.png'
            self.select_img = PhotoImage(file=image_file)
            self.button_text = canvas.create_image(self.x_pos + self.width/2, self.y_pos + self.height/2, image=self.base_img)


    def get_x(self):
        return self.x_pos

    def get_y(self):
        return self.y_pos

    def get_width(self):
        return self.width

    def get_height(self):
        return self.height

    def get_name(self):
        return self.text

    def get_state(self):
        return self.state

    def set_state(self, state):
        """ Compares current and last state to determine how to update
            button layout. Returns "play sound t/f"
        """
        if state and self.state == False:
            self.canvas.itemconfig(self.button_area, fill='#A54044')
            self.canvas.itemconfig(self.button_text, image=self.select_img)
            self.state = True
            return True  
        elif state != True:
            self.canvas.itemconfig(self.button_area, fill=self.b_color)
            self.canvas.itemconfig(self.button_text, image=self.base_img)
            self.state = False
            return False


    def check_pos(self, x, y):
        """ Compares recieved cursor position with button and updates selection.
        Returns true if sound is to be played
        """

        x_bool = (x >= self.x_pos) and (x <= self.x_pos + self.width)
        y_bool = (y >= self.y_pos) and (y <= self.y_pos + self.height)             
        play = self.set_state(x_bool and y_bool)
        return play