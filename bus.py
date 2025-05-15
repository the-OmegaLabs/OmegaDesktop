import Frameworks.Logger as Logger
import Components.DisplayManager


class Application():
    def __init__(self):
        Logger.output('Loading Omega Desktop...')

        self.IS_DEVMODE   = True  # fullscreen
        self.IS_LOWGPU    = False  # disable animation
        self.UI_SCALE     = 1.15    # scale of UI
        self.UI_FPS       = 200    # animation fps
        self.UI_WIDTH     = 1600   # screen size (useless when devmode disabling)
        self.UI_HEIGHT    = 900    
        self.UI_STYLE     = 'dark' # now only supports dark
        self.UI_LOCALE    = 'en'   #

        # background paths
        self.BG_DisplayManager = './Resources/bg/2.jpg' 

        for i in self.__dict__:
            Logger.output(f'{i}:   \t{self.__dict__[i]}\t{type(self.__dict__[i])}')

        self.DisplayManager = Components.DisplayManager.Application(self)
    

bus = Application()