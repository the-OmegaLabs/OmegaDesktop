import os
import platform
import sys
import Components.Desktop
import Components.DisplayManager

import Frameworks.Device as Device
import Frameworks.Logger as Logger

class Application():
    def __init__(self):
        Logger.output('Loading Omega Desktop...')

        self.IS_DEVMODE   = True    # fullscreen
        self.IS_LOWGPU    = False   # disable animation
        self.UI_SCALE     = 1.3   # scale of UI
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
        self.IMG_bg_DisplayManager = './Resources/bg/Fuji.webp' 
        self.IMG_bg_Desktop        = './Resources/bg/Fuji.webp' 

        self.IMG_icon_logo         = './Resources/icons/main.png' 
        self.IMG_icon_user         = './Resources/icons/user.png'
        self.IMG_icon_login        = './Resources/icons/login.png'
        
        while True:        
            self.RET_display_manager = Components.DisplayManager.Application(self).status

            #self.RET_display_manager = True # bypass login

            Logger.output(f'DisplayManager Status: {self.RET_display_manager}')
            
            if self.RET_display_manager:
                Components.Desktop.Application(self)    


            max_key_len = max(len(key) for key in self.__dict__)  
            for key, value in self.__dict__.items():
                Logger.output(f'{key:<{max_key_len}}  {str(value):<30} <type \'{type(value).__name__}\'>', type=Logger.Type.DEBUG)

            if self.IS_DEVMODE:
                break

    def playsound(self, path):
        Device.SoundSystem.playSound(path)

    def shutdown(self):
        Logger.output('Shutting down...')
        if not self.IS_DEVMODE and platform.system() == 'Linux':
            os.system('systemctl poweroff')
        else:
            sys.exit()

    def reboot(self):
        Logger.output('Rebooting...')
        if not self.IS_DEVMODE and platform.system() == 'Linux':
            os.system('systemctl reboot')
        else:
            sys.exit()

    def firmware_boot(self):
        Logger.output('Rebooting into firmware...')
        if not self.IS_DEVMODE and platform.system() == 'Linux':
            os.system('systemctl reboot --firmware-setup')
        else:
            sys.exit()

bus = Application()