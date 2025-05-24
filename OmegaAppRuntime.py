import threading
import Frameworks.Logger as Logger
import playsound
import runpy
import sys
import importlib.machinery

###############
# Application #
###############
import maliang.animation
import maliang.theme
import lunardate
from PIL import Image, ImageOps, ImageFilter, ImageDraw, ImageTk
import screeninfo
import simpleeval
###############

class AppRuntime():
    def __init__(self):
        Logger.output('Prepare runtime environment...')

        self.IS_DEVMODE   = True   
        self.IS_LOWGPU    = False   # disable animation
        self.UI_SCALE     = 1.3     # scale of UI
        self.UI_FPS       = 200     # animation fps
        self.UI_WIDTH     = 1600    # screen size (useless when devmode disabling)
        self.UI_HEIGHT    = 900    
        self.UI_THEME     = 'dark' 
        self.UI_LOCALE    = 'zh'    
        self.UI_ANIMATIME = 500
        self.UI_FAMILY    = '源流黑体 CJK'
        self.SET_USER     = 'root'
        self.SET_UID      = 1000
        self.SET_MUTE     = False    # disable sound playing

        if self.IS_LOWGPU:
            self.UI_ANIMATIME = 0

        # background paths
        self.IMG_bg_DisplayManager = './Resources/bg/Fuji_alt.webp' 
        self.IMG_bg_Desktop        = './Resources/bg/Fuji_alt.webp' 

        self.IMG_icon_logo         = './Resources/icons/main.png' 
        self.IMG_icon_user         = './Resources/icons/user.png'
        self.IMG_icon_login        = './Resources/icons/login.png'
        
        if len(sys.argv) < 2:
            Logger.output('No application provided.')
            sys.exit()
        else:
            pyc_path = sys.argv[-1]
            loader = importlib.machinery.SourcelessFileLoader("loaded_module", pyc_path)
            module = loader.load_module()
            module.Application(self)

    def playsound(self, path):
        if not self.SET_MUTE:
            threading.Thread(target=playsound.playsound, args=[path], daemon=True).start()

bus = AppRuntime()