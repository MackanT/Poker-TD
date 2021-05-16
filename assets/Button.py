from tkinter import *

class Button:

    def __init__(self, xPos, yPos, width, height, text, color, canvas):
        self.canvas = canvas
        self.xPos = xPos
        self.yPos = yPos
        self.width = width
        self.height = height
        self.text = text
        self.color = color

        self.buttonArea = canvas.create_rectangle(xPos, yPos,xPos + width, yPos + height, fill=self.color)
        self.buttonText = canvas.create_text(xPos + width/2, yPos + height/2, text=text)

    def getX(self):
        return self.xPos

    def getY(self):
        return self.yPos

    def getWidth(self):
        return self.width

    def getHeight(self):
        return self.height

    def getName(self):
        return self.text

    def pointInBox(self, x, y):

        xBool = (x >= self.xPos) and (x <= self.xPos + self.width)
        yBool = (y >= self.yPos) and (y <= self.yPos + self.height)

        if xBool == True and yBool == True:
            return True