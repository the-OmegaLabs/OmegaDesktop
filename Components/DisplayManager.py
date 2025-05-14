from PIL import (
    Image,
    ImageFilter,
    ImageDraw, 
    ImageFile
)


from lunardate import LunarDate
import Frameworks.Logger as Logger
import os
import threading
import maliang
import maliang.animation
import maliang.theme
import maliang.toolbox
import datetime
import pam
import math
import platform

class Application():
    def getScaled(self, number):
        return number * self.UI_SCALE

    def makeImageBlur(self, img, radius=10):
        return img.filter(ImageFilter.GaussianBlur(radius=radius))

    def __init__(self, args):
        Logger.output('Loading display manager...')

        self.IS_LOWGPU    = args.IS_LOWGPU    
        self.IS_DEVMODE   = args.IS_DEVMODE   

        self.UI_SCALE     = args.UI_SCALE     
        self.UI_FPS       = args.UI_FPS       
        self.UI_WIDTH     = args.UI_WIDTH     
        self.UI_HEIGHT    = args.UI_HEIGHT 
        self.UI_STYLE     = args.UI_STYLE 
        
        self.BG_DisplayManager = args.BG_DisplayManager

        self.IMG_original_bg = Image.open(self.BG_DisplayManager)

        self.createWindow()

    def getProportionalPicture(self, img: ImageFile.ImageFile, max_width: int, max_height: int):
        image_gcd = math.gcd(img.size[0], img.size[1])
        image_ratio = (img.size[0] // image_gcd, img.size[1] // image_gcd)
        target_gcd = math.gcd(max_width, max_height)

        return img.resize(size=(max_width, target_gcd * image_ratio[1]), resample=Image.Resampling.LANCZOS)

    def createWindow(self):        
        maliang.Env.system = 'Windows10' # enable widget transparent

        self.root = maliang.Tk()
        self.C_SCREENSIZE = self.root.size
        self.IMG_bg = self.getProportionalPicture(self.IMG_original_bg, self.C_SCREENSIZE[0], self.C_SCREENSIZE[1])
        self.IMG_blured_bg = self.makeImageBlur(self.IMG_bg)

        maliang.theme.manager.set_color_mode(self.UI_STYLE)
        
        if not self.IS_DEVMODE:
            self.root.fullscreen()
        else:
            self.root.geometry(size=(self.UI_WIDTH, self.UI_HEIGHT))

        self.cv = maliang.Canvas(self.root, auto_zoom=False)
        self.cv.place(width=self.root.size[0], height=self.root.size[1])

        self.WDG_background = maliang.Image(self.cv, position=(0, 0), size=self.root.size, image=maliang.PhotoImage(self.IMG_bg))

        self.root.mainloop()