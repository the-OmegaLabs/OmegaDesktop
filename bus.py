import Frameworks.Logger as Logger
import Components.DisplayManager


class Application():
    def __init__(self):
        Logger.output('Loading Omega Desktop...')

        self.IS_DEVMODE   = True    # fullscreen
        self.IS_LOWGPU    = False   # disable animation
        self.UI_SCALE     = 1.15    # scale of UI
        self.UI_FPS       = 200     # animation fps
        self.UI_WIDTH     = 1600    # screen size (useless when devmode disabling)
        self.UI_HEIGHT    = 900    
        self.UI_THEME     = 'dark' 
        self.UI_LOCALE    = 'zh'    
        self.UI_ANIMATIME = 700

        # background paths
        self.IMG_bg_DisplayManager = './Resources/bg/1.png' 
        self.IMG_icon_logo         = './Resources/icons/main.png' 

        self.DisplayManager = Components.DisplayManager.Application(self)

        # max_key_len = max(len(key) for key in self.__dict__)  
        # for key, value in self.__dict__.items():
        #     Logger.output(f'{key:<{max_key_len}}  {str(value):<30} <class \'{type(value).__name__}\'>')


bus = Application()