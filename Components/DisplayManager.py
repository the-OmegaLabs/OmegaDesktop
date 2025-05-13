from   PIL import Image, ImageFilter, ImageDraw
from   lunardate import LunarDate
import Frameworks.Logger as Logger
import os
import threading
import maliang
import maliang.animation
import maliang.theme
import maliang.toolbox
import datetime
import pam
import platform

class Application():
    def getScaled(self, number):
        return number * self.UI_SCALE
    
    def __init__(self):
        self.UI_SCALE      = 1.5
        self.UI_IS_LOWGPU  = 0
        self.UI_FPS        = 200

        Logger.output('Hello, World!')

    