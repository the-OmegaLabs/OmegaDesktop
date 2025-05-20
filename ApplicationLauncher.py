import threading
import Frameworks.Logger as Logger
import playsound

###############
# Application #
###############
import Application.calculator as App
###############

class Application():
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
        self.SET_USER     = 'root'
        self.SET_MUTE     = False    # disable sound playing

        if self.IS_LOWGPU:
            self.UI_ANIMATIME = 0

        # background paths
        self.IMG_bg_DisplayManager = './Resources/bg/1.png' 
        self.IMG_bg_Desktop        = './Resources/bg/1.png' 

        self.IMG_icon_logo         = './Resources/icons/main.png' 
        self.IMG_icon_user         = './Resources/icons/user.png'
        self.IMG_icon_login        = './Resources/icons/login.png'
        
        App.Application(args=self)

    def playsound(self, path):
        if not self.SET_MUTE:
            threading.Thread(target=playsound.playsound, args=[path], daemon=True).start()

bus = Application()