from PIL import (
    Image,
    ImageFilter,
    ImageDraw, 
    ImageOps
)
import psutil
from screeninfo import get_monitors

import Frameworks.Logger as Logger
import Frameworks.Device as Device
import maliang
import maliang.theme
from lunardate import LunarDate
import datetime
import maliang.animation
import pam
import threading
import platform

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

    def makeMaskImage(self, size, color=(0, 0, 0, 128)):
        if color == (0, 0, 0, 128):
            if self.UI_THEME == 'light':
                return Image.new("RGBA", size=size, color=(128, 128, 128, 128))
            else:
                return Image.new("RGBA", size=size, color=color)
        else:
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

    def getDate(self, now):
        if self.UI_LOCALE == 'zh':
            lunarDate = LunarDate.fromSolarDate(now.year, now.month, now.day)

            weekday = ["一", "二", "三", "四", "五", "六", "日"][now.weekday()]
            monthCN = ["", "一", "二", "三", "四", "五", "六", "七", "八", "九", "十", "十一", "十二"]
            dayCN = ['']
            
            for i in ['初', '十', '廿']:
                for j in range(1, 11, 1):
                    dayCN.append(f'{i}{monthCN[j]}')
                    
            dayCN[20] = '二十'

            ganzhiYear = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
            ganzhiMonth = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]

            yearGanZhi = f"{ganzhiYear[(lunarDate.year - 4) % 10]}{ganzhiMonth[(lunarDate.year - 4) % 12]}"

            return f'{now.month}月{now.day}日 星期{weekday} {yearGanZhi}年{monthCN[lunarDate.month]}月{dayCN[lunarDate.day]}'
        else:
            return now.strftime('%A, %B %d')

    def authenticate(self, password):
        shakes = [-15, 30, -30, 30, -15]
        
        def shakeAnimation(index):
            if index < len(shakes):
                i = shakes[index]
                animation = maliang.animation.MoveWidget(self.WDG_passwdMask, offset=(i, 0), duration=self.UI_ANIMATIME // 4, controller=maliang.animation.ease_out, fps=self.UI_FPS)
                animation.start()
                self.root.after(self.UI_ANIMATIME // 8, shakeAnimation, index + 1)
            else:
                self.setStatus()

        def failed():
            self.bus.playsound('./Resources/sound/auth_fail.mp3')
            Logger.output(f'Authentication failed')
            self.root.after(100, lambda: (self.WDG_auth_spinner.destroy()))
            self.cv.after(0, lambda: self.WDG_passwdMask.set(maliang.PhotoImage(self.IMG_passwdMask_error)))
            self.cv.after(0, lambda: shakeAnimation(0))
            

        def success():
            Logger.output(f'Authentication complete')
            self.root.after(100, self.WDG_auth_spinner.destroy())
            self.root.after(500, self.root.destroy)
            self.status = True

        def check():
            self.WDG_loginButton.destroy()
            self.WDG_passwdbox.disable(True)
            self.WDG_passwdbox.master.focus('')
            self.WDG_auth_spinner = maliang.Spinner(self.WDG_passwdbox, position=(self.getScaled(107), self.getScaled(0)), anchor='center', size=(self.getScaled(20), self.getScaled(20)), widths=(3, 3), mode='indeterminate')
        
            if platform.system() == 'Linux':
                authenticator = pam.pam()
                Logger.output(f'Authenticating {pam.PamAuthenticator}...')

                if password and authenticator.authenticate(username=self.SET_USER, password=password):
                    maliang.animation.MoveWidget(self.WDG_finder, end=success, offset=(0, 0 - self.getScaled(50)), duration=self.UI_ANIMATIME, controller=maliang.animation.ease_out, fps=self.UI_FPS).start()
                else:
                    failed()
            else:
                Logger.output(f'Bypass authenticating because host os is not Linux.')
                if password:
                    maliang.animation.MoveWidget(self.WDG_finder, end=success, offset=(0, 0 - self.getScaled(50)), duration=self.UI_ANIMATIME, controller=maliang.animation.ease_out, fps=self.UI_FPS).start()
                else:
                    self.cv.after(200, failed())

        threading.Thread(target=check, daemon=True).start()

    def adjustResolution(self):
        self.C_MONITOR = get_monitors()[0]
        if self.UI_WIDTH != self.C_MONITOR.width or self.UI_HEIGHT != self.C_MONITOR.height:
            Logger.output(f"Resolution changed: {(self.UI_WIDTH, self.UI_HEIGHT)} -> {self.C_MONITOR.width, self.C_MONITOR.height}")
            self.UI_WIDTH = self.C_MONITOR.width
            self.UI_HEIGHT = self.C_MONITOR.height
            self.root.geometry(size=(self.UI_WIDTH, self.UI_HEIGHT))
            self.cv.destroy()
            self.cv = maliang.Canvas(self.root, auto_zoom=False)
            self.cv.place(width=self.root.size[0], height=self.root.size[1])
            self.loadWidget()

        self.root.after(1000, lambda: self.adjustResolution())

    def updateTime(self):
        nowTime = datetime.datetime.now()

        self.WDG_finder_time.set(nowTime.strftime('%H:%M'))
        self.WDG_timeFrame_date.set(nowTime.strftime('%A, %B %d, %Y'))
        self.WDG_timeFrame_time.set(nowTime.strftime('%H:%M'))

        self.root.after(1000, lambda: self.updateTime())

    def __init__(self, args):
        Logger.output('Loading display manager...')

        self.status = False

        self.bus          = args
        self.IS_LOWGPU    = args.IS_LOWGPU    
        self.IS_DEVMODE   = args.IS_DEVMODE   

        self.UI_SCALE     = args.UI_SCALE     
        self.UI_FPS       = args.UI_FPS       
        self.UI_WIDTH     = args.UI_WIDTH     
        self.UI_HEIGHT    = args.UI_HEIGHT 
        self.UI_THEME     = args.UI_THEME 
        self.UI_ANIMATIME = args.UI_ANIMATIME
        self.UI_LOCALE    = args.UI_LOCALE
        self.UI_FAMILY    = args.UI_FAMILY
        self.APP_NOW_TIME = ""

        self.SET_USER     = args.SET_USER

        self.IS_FIRSTSET  = True
        
        self.IMG_bg_DisplayManager = args.IMG_bg_DisplayManager        
        self.IMG_original_bg = Image.open(self.IMG_bg_DisplayManager)
        
        self.IMG_icon_logo = args.IMG_icon_logo
        self.IMG_icon_user = args.IMG_icon_user
        self.IMG_icon_login  = args.IMG_icon_login

        self.IMG_icon_logo   = Image.open(self.IMG_icon_logo)
        self.IMG_icon_user   = Image.open(self.IMG_icon_user)
        self.IMG_icon_login  = Image.open(self.IMG_icon_login)
        self.BATTERY_STATUS  = True

        self.C_MONITOR = get_monitors()[0]
        self.UI_WIDTH, self.UI_HEIGHT = self.C_MONITOR.width, self.C_MONITOR.height

        self.createWindow()
        self.loadWidget()

        max_key_len = max(len(key) for key in self.__dict__)  
        for key, value in self.__dict__.items():
            Logger.output(f'{key:<{max_key_len}}  {str(value):<30} <type \'{type(value).__name__}\'>', type=Logger.Type.DEBUG)

        if not self.IS_DEVMODE:
            self.adjustResolution()

        self.root.mainloop()

    def createWindow(self):        
        maliang.Env.system = 'Windows10' # enable widget transparent

        self.root = maliang.Tk()

        maliang.theme.manager.set_color_mode(self.UI_THEME)
        
        if self.IS_DEVMODE:
            self.root.geometry(size=(self.UI_WIDTH, self.UI_HEIGHT))
        else:
            self.root.fullscreen()

        self.root.maxsize(self.UI_WIDTH, self.UI_HEIGHT)
        self.root.minsize(self.UI_WIDTH, self.UI_HEIGHT)

        self.root.icon(maliang.PhotoImage(Image.new('RGBA', size=(1, 1))))
        self.root.title('OmegaOS Display Manager')

        if self.IS_DEVMODE:
            maliang.theme.manager.hPyT.corner_radius.set(self.root, style="square")
            maliang.theme.manager.hPyT.maximize_minimize_button.hide(self.root,)
            maliang.theme.manager.hPyT.rainbow_border.start(self.root, interval=4)

        self.cv = maliang.Canvas(self.root, auto_zoom=False)
        self.cv.place(width=self.root.size[0], height=self.root.size[1])


    def dockHandler(self, i):
        if i == 0: # shutdown
            self.bus.shutdown()

        if i == 1: # reboot
            self.bus.reboot()

        if i == 2: # reboot into firmware
            self.bus.firmware_boot()
        
        if i == 3:
            self.showAbout()

    def showAbout(self):
        def enable_drag(widget):
            drag_data = {'x': None, 'y': None}

            def on_press(event):
                if widget.detect(event.x, event.y):
                    drag_data['x'] = event.x
                    drag_data['y'] = event.y

            def on_drag(event):
                if drag_data['x'] is not None and drag_data['y'] is not None:
                    dx = event.x - drag_data['x']
                    dy = event.y - drag_data['y']
                    widget.move(dx, dy)

                    drag_data['x'] = event.x
                    drag_data['y'] = event.y

            def on_release(event):
                drag_data['x'] = None
                drag_data['y'] = None

            widget.bind('<Button-1>', on_press)
            widget.bind('<B1-Motion>', on_drag)
            widget.bind('<ButtonRelease-1>', on_release)

        aboutWindow = maliang.Label(self.cv, size=(self.getScaled(350), self.getScaled(520)), position=((self.UI_WIDTH, self.UI_HEIGHT)[0] // 2 - self.getScaled(195), (self.UI_WIDTH, self.UI_HEIGHT)[1] // 2 - self.getScaled(260)))

        maliang.Image(aboutWindow, position=(self.getScaled(175), self.getScaled(40)), anchor='n', image=maliang.PhotoImage(self.IMG_icon_logo.resize((self.getScaled(195), self.getScaled(195)), 1)))

        maliang.Text(aboutWindow, text='Display Manager', 
                        position=(aboutWindow.size[0] // 2, self.getScaled(260)), anchor='center', 
                        family=self.UI_FAMILY, fontsize=self.getScaled(28), weight='bold')

        maliang.Text(aboutWindow, text='2.0.0', 
                        position=(aboutWindow.size[0] // 2, self.getScaled(295)), anchor='center', 
                        family=self.UI_FAMILY, fontsize=self.getScaled(20)).style.set(fg='#999999')
        
        maliang.Text(aboutWindow, text='© 2025 Omega Labs | Desktop Environment', 
                        position=(aboutWindow.size[0] // 2, self.getScaled(430)), anchor='center', 
                        family=self.UI_FAMILY, fontsize=self.getScaled(15)).style.set(fg='#DDDDDD')
        
        closeButton = maliang.Button(aboutWindow, text='Close', 
                        position=(aboutWindow.size[0] // 2, self.getScaled(470)), size=(self.getScaled(100), self.getScaled(40)), 
                        command=aboutWindow.destroy, anchor='center', family=self.UI_FAMILY, fontsize=self.getScaled(18))

        enable_drag(aboutWindow)

    def loadWidget(self):
        self.IMG_bg = self.getProportionalImage(img=self.IMG_original_bg, size=(self.UI_WIDTH, self.UI_HEIGHT))
        self.IMG_bg_blured1 = self.makeImageBlur(img=self.IMG_bg, radius=5)
        self.IMG_bg_blured2 = self.makeImageBlur(img=self.IMG_bg, radius=10)
        self.WDG_background = maliang.Image(self.cv, position=(0, 0), size=(self.UI_WIDTH, self.UI_HEIGHT), image=maliang.PhotoImage(self.IMG_bg))
        
        self.APP_finder_height = self.getScaled(55)
        self.APP_finder_widget_y = self.APP_finder_height // 2 + self.getScaled(2)

        self.WDG_finder = maliang.Label(self.cv, position=(0, 0 - self.getScaled(50)), size=(self.UI_WIDTH - 1, self.APP_finder_height))
        self.WDG_finder_bg = maliang.Image(self.WDG_finder, position=(1, 1), image=maliang.PhotoImage(self.makeImageBlur(self.mergeImage(self.IMG_bg.crop((0, 0, self.UI_WIDTH - 2, self.APP_finder_height - 1)), self.makeMaskImage(size=(self.UI_WIDTH - 2, self.APP_finder_height - 1))))))
        # self.WDG_finder.style.set(ol=('#888888', "#AAAAAA"))
        self.WDG_finder.style.set(ol=('', ''), bg=('', ''))



        self.WDG_finder_icon = maliang.Image(self.WDG_finder, position=(self.getScaled(20), self.APP_finder_widget_y), image=maliang.PhotoImage(self.IMG_icon_logo.resize((self.getScaled(36), self.getScaled(36)), 1)), anchor='w')
        self.WDG_finder_title = maliang.Text(self.WDG_finder, position=(self.WDG_finder_icon.position[0] * 2 + self.WDG_finder_icon.size[0], self.APP_finder_height // 2 + self.getScaled(2)), text='Display Manager', family=self.UI_FAMILY, fontsize=self.getScaled(20), anchor='w', weight='bold')
        self.WDG_finder_title.style.set(fg=('#FFFFFF'))


        self.WDG_finder_MenuBar = maliang.SegmentedButton(self.WDG_finder, text=['Poweroff', 'Reboot', 'Reboot into firmware', 'About'], position=(self.WDG_finder_title.position[0] + self.WDG_finder_title.size[0] + self.getScaled(5), self.APP_finder_height // 2 + self.getScaled(2)), family=self.UI_FAMILY, fontsize=self.getScaled(20), anchor='w', command=self.dockHandler, default=-1)
        self.WDG_finder_MenuBar.style.set(bg=('', ''), ol=('', ''))

        self.WDG_finder_time    = maliang.Text(self.WDG_finder, position=(self.UI_WIDTH - self.getScaled(20), self.APP_finder_widget_y), anchor='e', family=self.UI_FAMILY, fontsize=self.getScaled(20), weight='bold')


        for i in self.WDG_finder_MenuBar.children:
            i.style.set(fg=('#CCCCCC', "#FFFFFF", '#919191', '#CCCCCC', "#FFFFFF", '#919191'), bg=('', '', '', '', '', ''), ol=('', '', '', '', '', ''))

        #self.WDG_timeFrame      = maliang.Label(self.cv, anchor='n', position=(self.UI_WIDTH // 2, self.getScaled(115)), size=(self.getScaled(500), self.getScaled(130)),)
        self.WDG_timeFrame      = maliang.Label(self.cv, anchor='nw', position=(self.getScaled(105), self.getScaled(128)), size=(self.getScaled(500), self.getScaled(130)),)
        self.WDG_timeFrame.style.set(bg=('', ''), ol=('', ''))
            
        def generateTimeWidget():
            self.WDG_timeFrame_date = maliang.Text(self.WDG_timeFrame, position=(0, 0), family=self.UI_FAMILY, fontsize=self.getScaled(24)) 
            self.WDG_timeFrame_time = maliang.Text(self.WDG_timeFrame, position=(self.getScaled(-5), self.getScaled(20)), family="Mitype VF Heavy", fontsize=self.getScaled(96)) 

            self.updateTime()

        self.WDG_loginFrame     = maliang.Button(self.cv, anchor='sw', position=(self.getScaled(105), self.UI_HEIGHT - self.getScaled(80)), size=(self.getScaled(500), self.getScaled(90)))
        self.WDG_loginFrame.style.set(bg=('', '', ''), ol=('', '', ''))
        self.IMG_loginFrame_bg  = self.IMG_bg.crop((self.WDG_loginFrame.position[0], self.WDG_loginFrame.position[1] - self.getScaled(90), self.WDG_loginFrame.position[0] + self.WDG_loginFrame.size[0], self.WDG_loginFrame.position[1] + self.WDG_loginFrame.size[1] - self.getScaled(90)))
        self.IMG_loginFrame_bg  = self.makeRadiusImage(self.mergeImage(self.makeImageBlur(self.IMG_loginFrame_bg, radius=5), self.makeMaskImage(self.IMG_loginFrame_bg.size, color=(0, 0, 0, 96))), alpha=1, radius=self.getScaled(6))
        self.WDG_loginFrame_bg  = maliang.Image(self.WDG_loginFrame, position=(0, self.getScaled(-90)), image=maliang.PhotoImage(self.IMG_loginFrame_bg))

        maliang.animation.MoveWidget(self.WDG_finder, end=generateTimeWidget, offset=(0, self.getScaled(50)), duration=self.UI_ANIMATIME, controller=maliang.animation.ease_out, fps=self.UI_FPS).start(delay=self.UI_ANIMATIME // 2)
