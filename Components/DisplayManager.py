from PIL import (
    Image,
    ImageFilter,
    ImageDraw, 
    ImageOps
)

import Frameworks.Logger as Logger
import maliang
import maliang.theme
from lunardate import LunarDate
import datetime
import maliang.animation

# already ported with ^

import os
import threading
import maliang.toolbox
import pam
import math
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


    def setStatus(self):
        if self.UI_STATUS == 0:
            self.UI_STATUS = 1

            self.WDG_background.set(maliang.PhotoImage(self.IMG_bg_blured))

            for i in self.WDG_title_time_shadow:
                i.destroy()
                
            for i in self.WDG_title_time_characters:
                i.destroy()

            self.WDG_title_date.destroy()
            

        elif self.UI_STATUS == 1:
            self.UI_STATUS = 0
    
            self.WDG_background.set(maliang.PhotoImage(self.IMG_bg))

            self.WDG_title_time_characters = []
            self.WDG_title_time_shadow = []

            nowTime = datetime.datetime.now()
            n1, n2, sp, n3, n4 = nowTime.strftime('%H:%M')

            self.WDG_title_time_shadow.append(maliang.Text(self.cv, position=(self.UI_WIDTH // 2 - self.getScaled(35) * 1.85 + self.getScaled(1), self.UI_HEIGHT // 3.9 + self.getScaled(1)), text=n1, family='源流黑体 CJK', fontsize=self.getScaled(65), weight='bold', anchor='center'))
            self.WDG_title_time_shadow.append(maliang.Text(self.cv, position=(self.UI_WIDTH // 2 - self.getScaled(35) * 0.8  + self.getScaled(1), self.UI_HEIGHT // 3.9 + self.getScaled(1)), text=n2, family='源流黑体 CJK', fontsize=self.getScaled(65), weight='bold', anchor='center'))
            self.WDG_title_time_shadow.append(maliang.Text(self.cv, position=(self.UI_WIDTH // 2 + self.getScaled(35) * 0.8  + self.getScaled(1), self.UI_HEIGHT // 3.9 + self.getScaled(1)), text=n3, family='源流黑体 CJK', fontsize=self.getScaled(65), weight='bold', anchor='center'))
            self.WDG_title_time_shadow.append(maliang.Text(self.cv, position=(self.UI_WIDTH // 2 + self.getScaled(35) * 1.93 + self.getScaled(1), self.UI_HEIGHT // 3.9 + self.getScaled(1)), text=n4, family='源流黑体 CJK', fontsize=self.getScaled(65), weight='bold', anchor='center'))    
            self.WDG_title_time_shadow.append(maliang.Text(self.cv, position=(self.UI_WIDTH // 2 + self.getScaled(1), self.UI_HEIGHT // 3.9 + self.getScaled(1)), text=sp, family='源流黑体 CJK', fontsize=self.getScaled(60), weight='bold', anchor='center'))    
            
            self.WDG_title_time_characters.append(maliang.Text(self.cv, position=(self.UI_WIDTH // 2 - self.getScaled(35) * 1.85, self.UI_HEIGHT // 3.9), text=n1, family='源流黑体 CJK', fontsize=self.getScaled(65), weight='bold', anchor='center'))
            self.WDG_title_time_characters.append(maliang.Text(self.cv, position=(self.UI_WIDTH // 2 - self.getScaled(35) * 0.8,  self.UI_HEIGHT // 3.9), text=n2, family='源流黑体 CJK', fontsize=self.getScaled(65), weight='bold', anchor='center'))
            self.WDG_title_time_characters.append(maliang.Text(self.cv, position=(self.UI_WIDTH // 2 + self.getScaled(35) * 0.8,  self.UI_HEIGHT // 3.9), text=n3, family='源流黑体 CJK', fontsize=self.getScaled(65), weight='bold', anchor='center'))
            self.WDG_title_time_characters.append(maliang.Text(self.cv, position=(self.UI_WIDTH // 2 + self.getScaled(35) * 1.93, self.UI_HEIGHT // 3.9), text=n4, family='源流黑体 CJK', fontsize=self.getScaled(65), weight='bold', anchor='center'))    
            self.WDG_title_time_characters.append(maliang.Text(self.cv, position=(self.UI_WIDTH // 2, self.UI_HEIGHT // 3.9), text=sp, family='源流黑体 CJK', fontsize=self.getScaled(60), weight='bold', anchor='center'))    
            self.WDG_title_date = maliang.Text(self.cv, position=(self.C_SCREENSIZE[0] // 2, self.C_SCREENSIZE[1] // 5), anchor='center', text=self.getDate(nowTime), family='源流黑体 CJK', weight='bold')

            for i, widget in enumerate(self.WDG_title_time_characters):
                widget.style.set(fg=('#EEEEEE'))

            for i, widget in enumerate(self.WDG_title_time_shadow):
                widget.style.set(fg=('#9F9F9F'))

        else:
            pass

    def __init__(self, args):
        Logger.output('Loading display manager...')

        self.IS_LOWGPU    = args.IS_LOWGPU    
        self.IS_DEVMODE   = args.IS_DEVMODE   

        self.UI_SCALE     = args.UI_SCALE     
        self.UI_FPS       = args.UI_FPS       
        self.UI_WIDTH     = args.UI_WIDTH     
        self.UI_HEIGHT    = args.UI_HEIGHT 
        self.UI_THEME     = args.UI_THEME 
        self.UI_ANIMATIME = args.UI_ANIMATIME
        self.UI_LOCALE    = args.UI_LOCALE
        
        self.IMG_bg_DisplayManager = args.IMG_bg_DisplayManager
        self.IMG_icon_logo = args.IMG_icon_logo

        self.IMG_original_bg = Image.open(self.IMG_bg_DisplayManager)
        self.IMG_icon_logo   = Image.open(self.IMG_icon_logo)
        
        self.createWindow()
        self.loadWidget()

        max_key_len = max(len(key) for key in self.__dict__)  
        for key, value in self.__dict__.items():
            Logger.output(f'{key:<{max_key_len}}  {str(value):<50} <class \'{type(value).__name__}\'>')

        self.root.mainloop()

    def createWindow(self):        
        maliang.Env.system = 'Windows10' # enable widget transparent

        self.root = maliang.Tk()
        
        if self.IS_DEVMODE:
            self.C_SCREENSIZE = self.UI_WIDTH, self.UI_HEIGHT
        else:
            self.C_SCREENSIZE = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
        
        self.IMG_bg = self.getProportionalImage(img=self.IMG_original_bg, size=self.C_SCREENSIZE)
        self.IMG_bg_blured = self.makeImageBlur(img=self.IMG_bg)

        maliang.theme.manager.set_color_mode(self.UI_THEME)
        
        if not self.IS_DEVMODE:
            self.root.fullscreen()
        else:
            self.root.geometry(size=(self.UI_WIDTH, self.UI_HEIGHT))

        self.root.maxsize(self.C_SCREENSIZE[0], self.C_SCREENSIZE[1])
        self.root.minsize(self.C_SCREENSIZE[0], self.C_SCREENSIZE[1])

        self.root.icon(maliang.PhotoImage(Image.new('RGBA', size=(1, 1))))
        self.root.title('OmegaOS Display Manager')

        maliang.theme.manager.hPyT.corner_radius.set(self.root, style="square")
        maliang.theme.manager.hPyT.maximize_minimize_button.hide(self.root,)
        maliang.theme.manager.hPyT.rainbow_border.start(self.root, interval=4)

        self.cv = maliang.Canvas(self.root, auto_zoom=False)
        self.cv.place(width=self.root.size[0], height=self.root.size[1])

    def loadWidget(self):
        self.WDG_background = maliang.Image(self.cv, position=(0, 0), size=self.C_SCREENSIZE, image=maliang.PhotoImage(self.IMG_bg))
        
        self.APP_finder_height = self.getScaled(45)

        self.WDG_finder = maliang.Image(self.cv, 
                                        position=(0, 0), 
                                        image=maliang.PhotoImage(
                                            self.makeImageBlur(                                            
                                                self.mergeImage(
                                                    self.IMG_bg.crop((0, 0, self.C_SCREENSIZE[0], self.APP_finder_height)),
                                                    self.makeMaskImage(size=(self.C_SCREENSIZE[0], self.APP_finder_height))
                                                )
                                            )
                                        )
                        )

        self.WDG_finder_icon = maliang.Image(self.WDG_finder, position=(self.getScaled(30), self.getScaled(45 // 1.9)), image=maliang.PhotoImage(self.IMG_icon_logo.resize((self.getScaled(30), self.getScaled(30)), 1)), anchor='center')
        self.WDG_finder_title = maliang.Text(self.WDG_finder, position=(self.getScaled(65), self.getScaled(45 // 3.75)), text='显示管理器', family='源流黑体 CJK', fontsize=self.getScaled(15), weight='bold')
        self.WDG_finder_title.style.set(fg=('#FFFFFF'))

        self.WDG_finder_MenuBar = maliang.SegmentedButton(self.WDG_finder, text=['关机', '重启', '进入固件设置', '关于'], position=(self.getScaled(70) + self.getScaled(5.75 * (8 + len(self.WDG_finder_title.get()))), self.getScaled(45 // 2 + 1)), family='源流黑体 CJK', fontsize=self.getScaled(15), anchor='w')
        self.WDG_finder_MenuBar.style.set(bg=('', ''), ol=('', ''))

        for i in self.WDG_finder_MenuBar.children:
            i.style.set(fg=('#CCCCCC', '#DDDDDD', '#FFFFFF', '#CCCCCC', '#FFFFFF', '#FFFFFF'), bg=('', '', '', '', '', ''), ol=('', '', '', '', '', ''))

        self.WDG_finder_time = maliang.Text(self.WDG_finder, position=(self.C_SCREENSIZE[0] - self.getScaled(50), self.getScaled(12)), text=datetime.datetime.now().strftime("%H:%M"), family='源流黑体 CJK', fontsize=self.getScaled(15), weight='bold')
        self.WDG_finder_time.style.set(fg=('#FFFFFF'))

        self.WDG_finder_inputMethod_shape = maliang.Image(self.WDG_finder, position=(self.C_SCREENSIZE[0] - self.getScaled(150), self.getScaled(13)), image=maliang.PhotoImage(self.makeRadiusImage(self.makeMaskImage((100, 25), color=(255, 255, 255, 255)), radius=5, alpha=1)))
        self.WDG_finder_inputMethod_text = maliang.Text(self.WDG_finder_inputMethod_shape, position=(self.WDG_finder_inputMethod_shape.size[0] // 2 + self.getScaled(12), self.WDG_finder_inputMethod_shape.size[1] // 2 - self.getScaled(1)), text='AlphaBet', fontsize=self.getScaled(15), family='源流黑体 CJK', weight='bold')
        self.WDG_finder_inputMethod_text.style.set(fg=('#000000'))

        self.UI_STATUS = 1
        self.setStatus()

        self.testButton = maliang.Button(self.cv, position=(10, 60), size=(50, 50), command=self.setStatus)

        maliang.animation.MoveWidget(self.WDG_finder, offset=(0, 0 - self.getScaled(50)), duration=0, controller=maliang.animation.smooth, fps=self.UI_FPS).start()
        maliang.animation.MoveWidget(self.WDG_finder, offset=(0, self.getScaled(50)), duration=self.UI_ANIMATIME, controller=maliang.animation.ease_out, fps=self.UI_FPS).start(delay=self.UI_ANIMATIME // 2)

    