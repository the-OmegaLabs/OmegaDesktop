import threading
import Frameworks.Logger as Logger
import maliang
import maliang.theme
import maliang.animation
import os
from lunardate import LunarDate

from PIL import (
    Image,
    ImageFilter,
    ImageDraw, 
    ImageOps
)

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
        
    def __init__(self, args):
        Logger.output('Loading display manager...')

        self.status = False

        self.bus          = args 
        self.IS_DEVMODE   = args.IS_DEVMODE   

        self.UI_SCALE     = args.UI_SCALE     
        self.UI_FPS       = args.UI_FPS       
        self.UI_WIDTH     = 1000
        self.UI_HEIGHT    = 750 
        self.UI_THEME     = args.UI_THEME 
        self.UI_ANIMATIME = args.UI_ANIMATIME
        self.UI_LOCALE    = args.UI_LOCALE
        self.UI_FAMILY    = args.UI_FAMILY

        self.SET_USER     = args.SET_USER

        self.IS_FIRSTSET  = True
        
        self.IMG_icon_logo = args.IMG_icon_logo
        self.IMG_icon_user = args.IMG_icon_user
        self.IMG_icon_login  = args.IMG_icon_login

        self.IMG_icon_logo   = './Resources/icons/fileman.png'
        self.IMG_icon_user   = Image.open(self.IMG_icon_user)
        self.IMG_icon_login  = Image.open(self.IMG_icon_login)

        self.IMG_bg = args.IMG_bg_Desktop
        self.IMG_icon_logo   = Image.open(self.IMG_icon_logo)
        self.IMG_original_bg = Image.open(self.IMG_bg)
        self.APP_FINDER_MENU = []
        self.APP_SUBBAR_ACTIVE = -1

        self.createWindow()
        self.loadWidget()

        max_key_len = max(len(key) for key in self.__dict__)  
        for key, value in self.__dict__.items():
            Logger.output(f'{key:<{max_key_len}}  {str(value):<30} <type \'{type(value).__name__}\'>', type=Logger.Type.DEBUG)

        self.root.mainloop()

    def createWindow(self):        
        maliang.Env.system = 'Windows10' # enable widget transparent

        self.root = maliang.Tk()
        maliang.theme.manager.set_color_mode(self.UI_THEME)
        self.root.icon(maliang.PhotoImage(self.IMG_icon_logo))
        self.root.title('Omega Explorer')

        if self.IS_DEVMODE:
            maliang.theme.manager.hPyT.corner_radius.set(self.root, style="square")
            maliang.theme.manager.hPyT.rainbow_border.start(self.root, interval=4)

        self.cv = maliang.Canvas(self.root, auto_zoom=False)
        self.cv.place(width=self.root.size[0], height=self.root.size[1])

        def on_mousewheel(event):
            self.cv.yview_scroll(-1 * (event.delta // 120), "units")  # Windows /macOS

        def on_mousewheel_linux(event):
            if event.num == 4:
                self.cv.yview_scroll(-1, "units")
            elif event.num == 5:
                self.cv.yview_scroll(1, "units")

        self.cv.bind_all("<MouseWheel>", on_mousewheel)
        self.cv.bind_all("<Button-4>", on_mousewheel_linux)
        self.cv.bind_all("<Button-5>", on_mousewheel_linux)

        # 可选：更新 scrollregion（取决于 maliang.Canvas 是否支持）
        def reconfigureWindow(event):
            width = event.width 
            height = event.height
            if hasattr(self.cv, 'configure'):
                self.cv.configure(scrollregion=self.cv.bbox("all"))

        self.root.bind("<Configure>", reconfigureWindow)

        
    
    def loadWidget(self):
        for i, item in enumerate(os.listdir('C:\Windows')):
            print(f'[{i+1} / {len(os.listdir('C:\Windows'))}]')
            maliang.Text(self.cv, position=(self.getScaled(18), i * self.getScaled(18)), text=item, family=self.UI_FAMILY, weight='bold', fontsize=self.getScaled(15))
