from PIL import (
    Image,
    ImageFilter,
    ImageDraw, 
    ImageOps
)

import Frameworks.Logger as Logger
import maliang
import maliang.theme

# already ported with ^

import os
import threading
import maliang.animation
import maliang.toolbox
import datetime
import pam
import math
import platform
from lunardate import LunarDate

class Application():
    def getScaled(self, number) -> int:
        return int(number * self.UI_SCALE)

    def makeImageBlur(self, img: Image.Image, radius: int = 10) -> Image.Image:
        return img.filter(ImageFilter.GaussianBlur(radius=radius))
    
    def makeRadiusImage(self, img: Image.Image, radius: int = 30, alpha: float = 0.5) -> Image.Image:
        img = img.convert("RGBA")

        mask = Image.new("L", img.size, 0)
        draw = ImageDraw.Draw(mask)

        draw.rounded_rectangle(
            (0, 0, img.size[0], img.size[1]), radius, fill=int(256 * alpha))

        img.putalpha(mask)

        return img

    def makeMaskImage(self, size: tuple, color: tuple = (0, 0, 0, 128)) -> Image.Image:
        return Image.new("RGBA", size=size, color=color)

    def mergeImage(self, a: Image.Image, b: Image.Image) -> Image.Image:
        if a.format != 'RGBA': # ValueError: image has wrong mode 
            a = a.convert('RGBA')

        if b.format != 'RGBA':
            b = b.convert('RGBA')
        return Image.alpha_composite(a, b)

    def getProportionalImage(self, img: Image.Image, size: tuple) -> Image.Image:
        target_width, target_height = size
        scale_width = target_width / img.width
        scale_height = target_height / img.height
        scale = min(scale_width, scale_height)
        
        new_width = int(img.width * scale)
        new_height = int(img.height * scale)
        
        resized_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        resized_img = ImageOps.fit(resized_img, (target_width, target_height), Image.Resampling.LANCZOS, 0, (0.5, 0.5))
        
        return resized_img

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
        self.loadWidget()

        self.root.mainloop()


    def createWindow(self):        
        maliang.Env.system = 'Windows10' # enable widget transparent

        self.root = maliang.Tk()
        
        if self.IS_DEVMODE:
            self.C_SCREENSIZE = self.UI_WIDTH, self.UI_HEIGHT
        else:
            self.C_SCREENSIZE = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
        
        self.IMG_bg = self.getProportionalImage(img=self.IMG_original_bg, size=self.C_SCREENSIZE)

        maliang.theme.manager.set_color_mode(self.UI_STYLE)
        
        if not self.IS_DEVMODE:
            self.root.fullscreen()
        else:
            self.root.geometry(size=(self.UI_WIDTH, self.UI_HEIGHT))

        self.root.maxsize(self.C_SCREENSIZE[0], self.C_SCREENSIZE[1])
        self.root.minsize(self.C_SCREENSIZE[0], self.C_SCREENSIZE[1])

        self.cv = maliang.Canvas(self.root, auto_zoom=False)
        self.cv.place(width=self.root.size[0], height=self.root.size[1])


    def loadWidget(self):
        self.WDG_background = maliang.Image(self.cv, position=(0, 0), size=self.C_SCREENSIZE, image=maliang.PhotoImage(self.IMG_bg))
        
        self.APP_finder_height = self.getScaled(45)

        self.WDG_finder = maliang.Image(self.cv, 
                                        position=(0, 0), 
                                        image=maliang.PhotoImage(
                                            # self.makeImageBlur(                                            
                                                self.mergeImage(
                                                    self.IMG_original_bg.crop((0, 0, self.C_SCREENSIZE[0], self.APP_finder_height)),
                                                    self.makeMaskImage(size=(self.C_SCREENSIZE[0], self.APP_finder_height))
                                                )
                                            # )
                                        )
                        )


        Logger.output(f'Croping background for finder. ({self.WDG_finder.get()})')