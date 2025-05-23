from PIL import (
    Image,
    ImageFilter,
    ImageDraw, 
    ImageOps
)
from screeninfo import get_monitors

import Frameworks.Logger as Logger
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

    def setStatus(self):
        if self.UI_STATUS == 0:
            self.UI_STATUS = 2

            self.WDG_background.set(maliang.PhotoImage(self.IMG_bg_blured1))
            self.WDG_background.set(maliang.PhotoImage(self.IMG_bg_blured2))

            for i in self.WDG_title_time_shadow:
                i.destroy()
                
            for i in self.WDG_title_time_characters:
                i.destroy()

            self.WDG_title_date.destroy()
            

            self.WDG_passwdbox   = maliang.InputBox(self.WDG_loginContainer, position=(self.getScaled(400) // 2, self.getScaled(400 // 1.25)), size=(self.getScaled(250), self.getScaled(40)), anchor='center', fontsize=self.getScaled(15), family=self.UI_FAMILY, placeholder='密码', show='*')
            self.WDG_passwdbox_size = self.WDG_passwdbox.size
            self.WDG_passwdbox_position = self.WDG_passwdbox.position
            self.WDG_passwdbox.destroy()

            x1 = int(self.WDG_passwdbox_position[0] - self.WDG_passwdbox_size[0] // 2)
            y1 = int(self.WDG_passwdbox_position[1] - self.WDG_passwdbox_size[1] // 2 - self.UI_HEIGHT // 3)
            x2 = int(x1 + self.WDG_passwdbox_size[0])
            y2 = int(y1 + self.WDG_passwdbox_size[1])

            passwdImg = self.IMG_bg.crop((x1, y1, x2, y2))

            self.IMG_passwdMask  = self.makeRadiusImage(self.mergeImage(self.makeImageBlur(passwdImg), self.makeMaskImage(passwdImg.size)), radius=5, alpha=0.9)
            self.IMG_passwdMask_error  = self.makeRadiusImage(self.mergeImage(self.makeImageBlur(passwdImg), self.makeMaskImage(passwdImg.size, color=(96, 0, 0, 96))), radius=5, alpha=0.9)
            self.WDG_passwdMask  = maliang.Image(self.cv, position=(x1, y1), image=maliang.PhotoImage(self.IMG_passwdMask))
            self.WDG_passwdbox   = maliang.InputBox(self.WDG_loginContainer, position=(self.getScaled(400) // 2, self.getScaled(400 // 1.25)), size=(self.getScaled(250), self.getScaled(40)), anchor='center', fontsize=self.getScaled(15), family=self.UI_FAMILY, placeholder='密码', show='*')
            self.WDG_passwdbox.style.set(bg=('', '', ''), ol=('', '', ''))
            self.WDG_loginButton = maliang.IconButton(self.WDG_passwdbox, position=(self.getScaled(107), self.getScaled(0)), anchor='center', size=(self.getScaled(30), self.getScaled(30)), image=maliang.PhotoImage(self.IMG_icon_login.resize((self.getScaled(25), self.getScaled(25)), 1)), command=lambda: self.authenticate(self.WDG_passwdbox.get()))
            
            self.WDG_passwdbox.bind('<Return>', lambda _: self.authenticate(self.WDG_passwdbox.get()))
            self.WDG_passwdbox.style.set(bg=('', '', ''), ol=('', '', ''))
            self.WDG_loginButton.style.set(bg=('', '', ''), ol=('', '', ''))

            maliang.animation.MoveWidget(self.WDG_loginContainer, offset=(0, 0 - self.UI_HEIGHT // 3), duration=self.UI_ANIMATIME, controller=maliang.animation.ease_out, fps=self.UI_FPS).start()
            maliang.animation.MoveWidget(self.WDG_passwdMask, offset=(0, self.UI_HEIGHT // 1.5), duration=0, controller=maliang.animation.ease_out, fps=self.UI_FPS).start()
            maliang.animation.MoveWidget(self.WDG_passwdMask, offset=(0, 0 - self.UI_HEIGHT // 1.5), duration=self.UI_ANIMATIME, controller=maliang.animation.ease_out, fps=self.UI_FPS).start()
            
            self.UI_STATUS = 1


        elif self.UI_STATUS == 1:
            self.UI_STATUS = 2
    
            self.WDG_background.set(maliang.PhotoImage(self.IMG_bg_blured1))
            self.WDG_background.set(maliang.PhotoImage(self.IMG_bg))

            self.WDG_title_time_characters = []
            self.WDG_title_time_shadow = []

            nowTime = datetime.datetime.now()
            n1, n2, sp, n3, n4 = nowTime.strftime('%H:%M')

            self.WDG_title_time_shadow.append(maliang.Text(self.cv, position=(self.C_SCREENSIZE[0] // 2 - self.getScaled(35) * 1.85 + self.getScaled(1), self.C_SCREENSIZE[1] // 3.9 + self.getScaled(1)), text=n1, family=self.UI_FAMILY_TIME, fontsize=self.getScaled(65), weight='bold', anchor='center'))
            self.WDG_title_time_shadow.append(maliang.Text(self.cv, position=(self.C_SCREENSIZE[0] // 2 - self.getScaled(35) * 0.8  + self.getScaled(1), self.C_SCREENSIZE[1] // 3.9 + self.getScaled(1)), text=n2, family=self.UI_FAMILY_TIME, fontsize=self.getScaled(65), weight='bold', anchor='center'))
            self.WDG_title_time_shadow.append(maliang.Text(self.cv, position=(self.C_SCREENSIZE[0] // 2 + self.getScaled(35) * 0.8  + self.getScaled(1), self.C_SCREENSIZE[1] // 3.9 + self.getScaled(1)), text=n3, family=self.UI_FAMILY_TIME, fontsize=self.getScaled(65), weight='bold', anchor='center'))
            self.WDG_title_time_shadow.append(maliang.Text(self.cv, position=(self.C_SCREENSIZE[0] // 2 + self.getScaled(35) * 1.93 + self.getScaled(1), self.C_SCREENSIZE[1] // 3.9 + self.getScaled(1)), text=n4, family=self.UI_FAMILY_TIME, fontsize=self.getScaled(65), weight='bold', anchor='center'))    
            self.WDG_title_time_shadow.append(maliang.Text(self.cv, position=(self.C_SCREENSIZE[0] // 2 + self.getScaled(1), self.C_SCREENSIZE[1] // 3.9 + self.getScaled(1)), text=sp, family=self.UI_FAMILY_TIME, fontsize=self.getScaled(60), weight='bold', anchor='center'))    
            
            self.WDG_title_time_characters.append(maliang.Text(self.cv, position=(self.C_SCREENSIZE[0] // 2 - self.getScaled(35) * 1.85, self.C_SCREENSIZE[1] // 3.9), text=n1, family=self.UI_FAMILY_TIME, fontsize=self.getScaled(65), weight='bold', anchor='center'))
            self.WDG_title_time_characters.append(maliang.Text(self.cv, position=(self.C_SCREENSIZE[0] // 2 - self.getScaled(35) * 0.8,  self.C_SCREENSIZE[1] // 3.9), text=n2, family=self.UI_FAMILY_TIME, fontsize=self.getScaled(65), weight='bold', anchor='center'))
            self.WDG_title_time_characters.append(maliang.Text(self.cv, position=(self.C_SCREENSIZE[0] // 2 + self.getScaled(35) * 0.8,  self.C_SCREENSIZE[1] // 3.9), text=n3, family=self.UI_FAMILY_TIME, fontsize=self.getScaled(65), weight='bold', anchor='center'))
            self.WDG_title_time_characters.append(maliang.Text(self.cv, position=(self.C_SCREENSIZE[0] // 2 + self.getScaled(35) * 1.93, self.C_SCREENSIZE[1] // 3.9), text=n4, family=self.UI_FAMILY_TIME, fontsize=self.getScaled(65), weight='bold', anchor='center'))    
            self.WDG_title_time_characters.append(maliang.Text(self.cv, position=(self.C_SCREENSIZE[0] // 2, self.C_SCREENSIZE[1] // 3.9), text=sp, family=self.UI_FAMILY_TIME, fontsize=self.getScaled(60), weight='bold', anchor='center'))    
            self.WDG_title_date = maliang.Text(self.cv, position=(self.C_SCREENSIZE[0] // 2, self.C_SCREENSIZE[1] // 5), anchor='center', text=self.getDate(nowTime), family=self.UI_FAMILY, fontsize=self.getScaled(18), weight='bold')

            for i, widget in enumerate(self.WDG_title_time_characters):
                widget.style.set(fg=('#EEEEEE'))

            for i, widget in enumerate(self.WDG_title_time_shadow):
                widget.style.set(fg=('#9F9F9F'))

            if not self.IS_FIRSTSET:
                self.WDG_passwdbox.destroy()
                maliang.animation.MoveWidget(self.WDG_loginContainer, offset=(0, self.UI_HEIGHT // 3), duration=self.UI_ANIMATIME, controller=maliang.animation.ease_out, fps=self.UI_FPS).start()
                maliang.animation.MoveWidget(self.WDG_passwdMask, offset=(0, self.UI_HEIGHT // 1.5), duration=self.UI_ANIMATIME, controller=maliang.animation.ease_out, fps=self.UI_FPS).start()
            else:
                self.IS_FIRSTSET = False

            self.UI_STATUS = 0

        else:
            pass

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
        self.UI_FAMILY_TIME    = self.UI_FAMILY

        if self.IS_DEVMODE:
            self.C_SCREENSIZE = self.UI_WIDTH, self.UI_HEIGHT
        else:
            self.C_MONITOR    = get_monitors()[0]

            self.C_SCREENSIZE = self.C_MONITOR.width, self.C_MONITOR.height

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

        self.createWindow()
        self.loadWidget()

        max_key_len = max(len(key) for key in self.__dict__)  
        for key, value in self.__dict__.items():
            Logger.output(f'{key:<{max_key_len}}  {str(value):<30} <type \'{type(value).__name__}\'>', type=Logger.Type.DEBUG)

        self.root.mainloop()

    def createWindow(self):        
        maliang.Env.system = 'Windows10' # enable widget transparent

        self.root = maliang.Tk()
        
        def adjustResolution():
            self.C_MONITOR = get_monitors()[0]
            if self.C_SCREENSIZE != (self.C_MONITOR.width, self.C_MONITOR.height):
                Logger.output(f"Resolution changed: {self.C_SCREENSIZE} -> {self.C_MONITOR.width, self.C_MONITOR.height}")
                self.C_SCREENSIZE = (self.C_MONITOR.width, self.C_MONITOR.height)
                self.root.geometry(size=self.C_SCREENSIZE)
                self.cv.destroy()
                self.cv = maliang.Canvas(self.root, auto_zoom=False)
                self.cv.place(width=self.root.size[0], height=self.root.size[1])
                self.loadWidget()

            self.root.after(1000, adjustResolution)

        maliang.theme.manager.set_color_mode(self.UI_THEME)
        
        if not self.IS_DEVMODE:
            self.root.fullscreen()
        else:
            self.root.geometry(size=(self.UI_WIDTH, self.UI_HEIGHT))

        self.root.maxsize(self.C_SCREENSIZE[0], self.C_SCREENSIZE[1])
        self.root.minsize(self.C_SCREENSIZE[0], self.C_SCREENSIZE[1])

        self.root.icon(maliang.PhotoImage(Image.new('RGBA', size=(1, 1))))
        self.root.title('OmegaOS Display Manager')

        if self.IS_DEVMODE:
            maliang.theme.manager.hPyT.corner_radius.set(self.root, style="square")
            maliang.theme.manager.hPyT.maximize_minimize_button.hide(self.root,)
            maliang.theme.manager.hPyT.rainbow_border.start(self.root, interval=4)

        self.cv = maliang.Canvas(self.root, auto_zoom=False)
        self.cv.place(width=self.root.size[0], height=self.root.size[1])

        if not self.IS_DEVMODE:
            adjustResolution()

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

        aboutWindow = maliang.Label(self.cv, size=(self.getScaled(270), self.getScaled(400)), position=(self.C_SCREENSIZE[0] // 2 - self.getScaled(150), self.C_SCREENSIZE[1] // 2 - self.getScaled(200)))

        maliang.Image(aboutWindow, position=(self.getScaled(134), self.getScaled(30)), anchor='n', image=maliang.PhotoImage(self.IMG_icon_logo.resize((self.getScaled(150), self.getScaled(150)), 1)))

        maliang.Text(aboutWindow, text='显示管理器', 
                        position=(aboutWindow.size[0] // 2, self.getScaled(200)), anchor='center', 
                        family=self.UI_FAMILY, fontsize=self.getScaled(20), weight='bold')

        maliang.Text(aboutWindow, text='2.0.0', 
                        position=(aboutWindow.size[0] // 2, self.getScaled(225)), anchor='center', 
                        family=self.UI_FAMILY, fontsize=self.getScaled(15)).style.set(fg='#999999')
        
        maliang.Text(aboutWindow, text='© 2025 Omega Labs | OmegaOS 桌面环境', 
                        position=(aboutWindow.size[0] // 2, self.getScaled(327)), anchor='center', 
                        family=self.UI_FAMILY, fontsize=self.getScaled(11)).style.set(fg='#DDDDDD')
        
        closeButton = maliang.Button(aboutWindow, text='关闭', 
                        position=(aboutWindow.size[0] // 2, self.getScaled(360)), size=(self.getScaled(70), self.getScaled(30)), 
                        command=aboutWindow.destroy, anchor='center', family=self.UI_FAMILY, fontsize=self.getScaled(15))

        #closeButton.style.set(ol=('', '', ''), bg=('', '', ''))

        enable_drag(aboutWindow)

    def loadWidget(self):
        self.IMG_bg = self.getProportionalImage(img=self.IMG_original_bg, size=self.C_SCREENSIZE)
        self.IMG_bg_blured1 = self.makeImageBlur(img=self.IMG_bg, radius=5)
        self.IMG_bg_blured2 = self.makeImageBlur(img=self.IMG_bg, radius=10)
        self.WDG_background = maliang.Image(self.cv, position=(0, 0), size=self.C_SCREENSIZE, image=maliang.PhotoImage(self.IMG_bg))
        
        self.APP_finder_height = self.getScaled(45)

        self.WDG_finder = maliang.Image(self.cv, 
                                        position=(0, 0 - self.getScaled(50)), 
                                        image=maliang.PhotoImage(
                                            self.makeImageBlur(                                            
                                                self.mergeImage(
                                                    self.IMG_bg.crop((0, 0, self.C_SCREENSIZE[0], self.APP_finder_height)),
                                                    self.makeMaskImage(size=(self.C_SCREENSIZE[0], self.APP_finder_height))
                                                )
                                            )
                                        )
                        )

        self.WDG_finder_icon = maliang.Image(self.WDG_finder, position=(self.getScaled(30), self.APP_finder_height // 1.9), image=maliang.PhotoImage(self.IMG_icon_logo.resize((self.getScaled(30), self.getScaled(30)), 1)), anchor='center')
        self.WDG_finder_title = maliang.Text(self.WDG_finder, position=(self.getScaled(65), self.APP_finder_height // 3.75), text='显示管理器', family=self.UI_FAMILY, fontsize=self.getScaled(15), weight='bold')
        self.WDG_finder_title.style.set(fg=('#FFFFFF'))

        self.WDG_finder_MenuBar = maliang.SegmentedButton(self.WDG_finder, text=['关机', '重启', '进入固件设置', '关于'], position=(self.getScaled(70) + self.getScaled(5.75 * (8 + len(self.WDG_finder_title.get()))), self.APP_finder_height // 2 + 1), family=self.UI_FAMILY, fontsize=self.getScaled(15), anchor='w', command=self.dockHandler)
        self.WDG_finder_MenuBar.style.set(bg=('', ''), ol=('', ''))

        for i in self.WDG_finder_MenuBar.children:
            i.style.set(fg=('#CCCCCC', '#DDDDDD', '#FFFFFF', '#CCCCCC', '#FFFFFF', '#FFFFFF'), bg=('', '', '', '', '', ''), ol=('', '', '', '', '', ''))

        self.WDG_finder_time = maliang.Text(self.WDG_finder, position=(self.C_SCREENSIZE[0] - self.getScaled(50), self.getScaled(12)), text=datetime.datetime.now().strftime("%H:%M"), family=self.UI_FAMILY, fontsize=self.getScaled(15), weight='bold')
        self.WDG_finder_time.style.set(fg=('#FFFFFF'))

        self.WDG_finder_inputMethod_shape = maliang.Image(self.WDG_finder, position=(self.C_SCREENSIZE[0] - self.getScaled(145), self.getScaled(13)), image=maliang.PhotoImage(self.makeRadiusImage(self.makeMaskImage((self.getScaled(85), self.getScaled(20)), color=(255, 255, 255, 255)), radius=5, alpha=1)))
        self.WDG_finder_inputMethod_text = maliang.Text(self.WDG_finder_inputMethod_shape, position=(self.WDG_finder_inputMethod_shape.size[0] // 2 + self.getScaled(11), self.WDG_finder_inputMethod_shape.size[1] // 2 - self.getScaled(2)), text='AlphaBet', fontsize=self.getScaled(15), family=self.UI_FAMILY, weight='bold')
        self.WDG_finder_inputMethod_text.style.set(fg=('#000000'))

        self.UI_STATUS = 1
        self.setStatus()

        # self.testButton = maliang.Button(self.cv, position=(10, 60), size=(50, 50), command=self.setStatus)

        maliang.animation.MoveWidget(self.WDG_finder, offset=(0, self.getScaled(50)), duration=self.UI_ANIMATIME, controller=maliang.animation.ease_out, fps=self.UI_FPS).start(delay=self.UI_ANIMATIME // 2)

        self.WDG_loginContainer = maliang.Label(self.cv, position=(self.C_SCREENSIZE[0] // 2 - self.getScaled(200), self.C_SCREENSIZE[1] // 1.75), size=(self.getScaled(400), self.getScaled(400)))
        self.WDG_loginContainer.style.set(fg=('', ''), bg=('', ''), ol=('', ''))

        self.IMG_avatar = self.makeRadiusImage(self.IMG_icon_user, radius=self.IMG_icon_user.size[0], alpha=0.9).resize((self.getScaled(150), self.getScaled(150)), 1)
        self.WDG_avatar = maliang.IconButton(self.WDG_loginContainer, size=(self.getScaled(150), self.getScaled(150)), position=(self.getScaled(400) // 2, self.getScaled(400) // 2.75), image=maliang.PhotoImage(self.IMG_avatar), anchor='center', command=self.setStatus)
        self.WDG_avatar.style.set(bg=('', '', ''), ol=('', '', ''))

        self.loginUser_shadow   = maliang.Text(self.WDG_loginContainer, position=(self.getScaled(400) // 2 + self.getScaled(1), self.getScaled(400 / 1.55) + self.getScaled(1)), text=self.SET_USER, family=self.UI_FAMILY, fontsize=self.getScaled(28), anchor='center', weight='bold')
        self.loginUser   = maliang.Text(self.WDG_loginContainer, position=(self.getScaled(400) // 2,  self.getScaled(400 / 1.55)), text=self.SET_USER, family=self.UI_FAMILY, fontsize=self.getScaled(28), anchor='center', weight='bold')
        self.loginUser_shadow.style.set(fg=('#666666'))
