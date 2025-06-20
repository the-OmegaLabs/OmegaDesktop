import os
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
from screeninfo import get_monitors
import maliang.animation
# from Xlib import display
# import subprocess
# import pyatspi


class Application():
    def __init__(self, args):
        Logger.output('Loading display manager...')

        self.status = False

        self.bus          = args 
        self.IS_DEVMODE   = args.IS_DEVMODE   

        self.UI_SCALE     = args.UI_SCALE     
        self.UI_FPS       = args.UI_FPS       
        self.UI_WIDTH     = args.UI_WIDTH     
        self.UI_HEIGHT    = args.UI_HEIGHT 
        self.UI_THEME     = args.UI_THEME 
        self.UI_ANIMATIME = args.UI_ANIMATIME
        self.UI_LOCALE    = args.UI_LOCALE
        self.UI_FAMILY    = args.UI_FAMILY

        if self.IS_DEVMODE:
            (self.UI_WIDTH, self.UI_HEIGHT) = self.UI_WIDTH, self.UI_HEIGHT
        else:
            self.C_MONITOR    = get_monitors()[0]

            (self.UI_WIDTH, self.UI_HEIGHT) = self.C_MONITOR.width, self.C_MONITOR.height

        self.SET_USER     = args.SET_USER
        self.SET_UID      = args.SET_UID

        self.IS_FIRSTSET  = True
        
        self.IMG_icon_logo = args.IMG_icon_logo
        self.IMG_icon_user = args.IMG_icon_user
        self.IMG_icon_login  = args.IMG_icon_login

        self.IMG_icon_logo   = Image.open(self.IMG_icon_logo)
        self.IMG_icon_user   = Image.open(self.IMG_icon_user)
        self.IMG_icon_login  = Image.open(self.IMG_icon_login)

        self.IMG_bg = args.IMG_bg_Desktop
        self.IMG_original_bg = Image.open(self.IMG_bg)
        self.APP_FINDER_MENU = []
        self.APP_SUBBAR_ACTIVE = -1

        self.createWindow()
        self.loadWidget()

        max_key_len = max(len(key) for key in self.__dict__)  
        for key, value in self.__dict__.items():
            Logger.output(f'{key:<{max_key_len}}  {str(value):<30} <type \'{type(value).__name__}\'>', type=Logger.Type.DEBUG)

        if not self.IS_DEVMODE:
            self.root.fullscreen()
        else:
            self.root.geometry(size=(self.UI_WIDTH, self.UI_HEIGHT))

        self.root.mainloop()


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

    # def getActiveApplicationMenu(self):
    #     def find_menubar(obj):
    #         if obj.getRoleName() == "menu bar":
    #             return obj
    #         for i in range(obj.childCount):
    #             child = obj.getChildAtIndex(i)
    #             result = find_menubar(child)
    #             if result:
    #                 return result
    #         return None

    #     try:
    #         d = display.Display()
    #         root = d.screen().root
    #         NET_ACTIVE_WINDOW = d.intern_atom('_NET_ACTIVE_WINDOW')
    #         prop = root.get_full_property(NET_ACTIVE_WINDOW, 0)
    #         if prop is None:
    #             return [None, []]

    #         window_id = prop.value[0]

    #         window = d.create_resource_object('window', window_id)
    #         pid_atom = d.intern_atom('_NET_WM_PID')
    #         pid = window.get_full_property(pid_atom, 0).value[0]

    #         process_name = subprocess.check_output(['ps', '-p', str(pid), '-o', 'comm=']).decode().strip()

    #     except Exception as e:
    #         print("X11 error:", e)
    #         return [None, []]

    #     desktop = pyatspi.Registry.getDesktop(0)
    #     app = None
    #     for i in range(desktop.childCount):
    #         candidate = desktop.getChildAtIndex(i)
    #         if candidate.get_process_id() == pid:
    #             app = candidate
    #             break

    #     if not app:
    #         return (process_name, [])


    #     menubar = find_menubar(app)
    #     items = []

    #     if menubar:
    #         for i in range(menubar.childCount):
    #             items.append(menubar.getChildAtIndex(i).name)

    #     return [process_name, items]

    def createWindow(self):        
        maliang.Env.system = 'Windows10' # enable widget transparent

        self.root = maliang.Tk()
        
        def adjustResolution():
            self.C_MONITOR = get_monitors()[0]
            if (self.UI_WIDTH, self.UI_HEIGHT) != (self.C_MONITOR.width, self.C_MONITOR.height):
                Logger.output(f"Resolution changed: {(self.UI_WIDTH, self.UI_HEIGHT)} -> {self.C_MONITOR.width, self.C_MONITOR.height}")
                (self.UI_WIDTH, self.UI_HEIGHT) = (self.C_MONITOR.width, self.C_MONITOR.height)
                self.root.geometry(size=(self.UI_WIDTH, self.UI_HEIGHT))
                self.cv.destroy()
                self.cv = maliang.Canvas(self.root, auto_zoom=False)
                self.cv.place(width=self.root.size[0], height=self.root.size[1])
                self.loadWidget()

            self.root.after(1000, adjustResolution)


        maliang.theme.manager.set_color_mode(self.UI_THEME)

        self.root.maxsize((self.UI_WIDTH, self.UI_HEIGHT)[0], (self.UI_WIDTH, self.UI_HEIGHT)[1])
        self.root.minsize((self.UI_WIDTH, self.UI_HEIGHT)[0], (self.UI_WIDTH, self.UI_HEIGHT)[1])

        self.root.icon(maliang.PhotoImage(Image.new('RGBA', size=(1, 1))))
        self.root.title('OmegaOS Desktop Environment')

        if self.IS_DEVMODE:
            maliang.theme.manager.hPyT.corner_radius.set(self.root, style="square")
            maliang.theme.manager.hPyT.maximize_minimize_button.hide(self.root,)
            maliang.theme.manager.hPyT.rainbow_border.start(self.root, interval=4)

        self.cv = maliang.Canvas(self.root, auto_zoom=False)
        self.cv.place(width=self.root.size[0], height=self.root.size[1])

        if not self.IS_DEVMODE:
            adjustResolution()

        def keyPress(event):
            if event.keycode in (174, 175): # change volume
                self.bus.playsound('./Resources/sound/tink.mp3')

        def keyRelease(event):
            pass

        self.root.bind("<KeyPress>", keyPress)
        self.root.bind("<KeyRelease>", keyRelease)


    def MenuHandler(self, i):
        def subBarHandler(i):
            if self.APP_SUBBAR_ACTIVE == 0:
                if i == 4:
                    self.bus.reboot()
                if i == 5: # shutdown
                    self.bus.shutdown()
                if i == 6: # leave username session
                    self.root.destroy()

            self.WDG_SubBar.destroy()
            self.WDG_SubBar_bg.destroy()
            self.APP_SUBBAR_ACTIVE = -1 # original subbar deleted so just set status to first click

        
        if self.APP_SUBBAR_ACTIVE == -1: # first click
            self.APP_SUBBAR_ACTIVE = i

        elif self.APP_SUBBAR_ACTIVE != i: # another button
            self.WDG_SubBar.destroy()
            self.WDG_SubBar_bg.destroy()
            self.APP_SUBBAR_ACTIVE = i

        
        menu = []
        if i == 0:
            menu = [
                'About This Device',
                'System Settings...',
                'Plusto App Store...',
                'Task Manager...',
                'Restart...',
                'Shutdown...',
                f'Log Out \"{self.SET_USER}\"...              '
            ]

        if i == 1:
            menu = [
                'Undo',
                'Redo',
                'Cut',
                'Copy',
                'Paste',
                'Clipboard Utility...      '
            ]

        if i == 2:
            menu = [
                'Documents',
                'Downloads',
                'Desktop',
                'Network',
                f'{self.SET_USER}’s Home Folder     ',
            ]

        if i == 3:
            menu = [
                'Minimize Current Window   ',
                'Merge All Windows',
                'Bring All Windows to Front',
                'Hide All Windows'
            ]

        if i == 4:
            menu = [
                'What\'s New in OmegaOS 2.0 "Fuji"...',
                'Welcome to OmegaOS...',
                'Search Help Topics...',
                'Omega Desktop Help',
                'Feedback or Suggestions...',
                'Check for Updates...',
                'About This OmegaOS'
            ]



        subBarPosition = (self.WDG_finder_MenuBar.children[i].position[0] + self.getScaled(2), self.APP_finder_height)

        self.WDG_SubBar = maliang.SegmentedButton(
            self.cv, text=menu, position=subBarPosition,
            family=self.UI_FAMILY, fontsize=self.getScaled(13), command=subBarHandler, layout='vertical'
        )

        subBarSize = self.WDG_SubBar.size

        subBarBlur = self.makeImageBlur(self.IMG_bg.crop((subBarPosition[0], subBarPosition[1], subBarPosition[0] + subBarSize[0], subBarPosition[1] + subBarSize[1])))
        subBarMask = self.makeRadiusImage(self.mergeImage(subBarBlur, self.makeMaskImage(subBarSize)), alpha=1, radius=5)
        self.WDG_SubBar_bg = maliang.Image(self.cv, position=subBarPosition, size=subBarSize, image=maliang.PhotoImage(subBarMask))

        self.WDG_SubBar.lift()

        self.WDG_SubBar.style.set(bg=('', ''), ol=('', ''))
        for i in self.WDG_SubBar.children:
            i.style.set(fg=('#DDDDDD', '#EEEEEE', '#FFFFFF', '#DDDDDD', '#FFFFFF', '#FFFFFF'), 
                        bg=('', '', '', '', '', ''), 
                        ol=('', '', '', '', '', ''))
            
        def destroySubBar(event):
            if self.APP_SUBBAR_ACTIVE != -1:
                if event.x < self.WDG_SubBar.position[0] or event.x > self.WDG_SubBar.position[0] + self.WDG_SubBar.size[0] or event.y < self.WDG_SubBar.position[1] or event.y > self.WDG_SubBar.position[1] + self.WDG_SubBar.size[1]:
                    self.WDG_SubBar_bg.destroy()
                    self.WDG_SubBar.destroy()

                    self.APP_SUBBAR_ACTIVE = -1 # original subbar deleted so just set status to first click

        
        self.root.bind("<Button-1>", lambda event: destroySubBar(event))

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

        aboutWindow = maliang.Label(self.cv, size=(self.getScaled(270), self.getScaled(400)), position=((self.UI_WIDTH, self.UI_HEIGHT)[0] // 2 - self.getScaled(150), (self.UI_WIDTH, self.UI_HEIGHT)[1] // 2 - self.getScaled(200)))

        maliang.Image(aboutWindow, position=(self.getScaled(134), self.getScaled(30)), anchor='n', image=maliang.PhotoImage(self.IMG_icon_logo.resize((self.getScaled(150), self.getScaled(150)), 1)))

        maliang.Text(aboutWindow, text='显示管理器', 
                        position=(aboutWindow.size[0] // 2, self.getScaled(200)), anchor='center', 
                        family=self.UI_FAMILY, fontsize=self.getScaled(20), weight='bold')

        maliang.Text(aboutWindow, text='1.0.0', 
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
        self.IMG_bg = self.getProportionalImage(img=self.IMG_original_bg, size=(self.UI_WIDTH, self.UI_HEIGHT))
        self.IMG_bg_blured1 = self.makeImageBlur(img=self.IMG_bg, radius=5)
        self.IMG_bg_blured2 = self.makeImageBlur(img=self.IMG_bg, radius=10)
        self.WDG_background = maliang.Image(self.cv, position=(0, 0), size=(self.UI_WIDTH, self.UI_HEIGHT), image=maliang.PhotoImage(self.IMG_bg))
        
        self.APP_finder_height = self.getScaled(45)
        
        # self.WDG_finderWin = maliang.Toplevel(self.root, size=((self.UI_WIDTH, self.UI_HEIGHT)[0], self.APP_finder_height), position=(self.root.winfo_x(), self.root.winfo_y()))
        # self.WDG_finderWin.topmost(True)

        # self.WDG_finder = maliang.Canvas(self.WDG_finderWin)
        # self.WDG_finder.place(x=0, y=0, width=self.IMG_bg.size[0], height=self.IMG_bg.size[1])

        self.WDG_finder = maliang.Image(self.cv, position=(0, 0 - self.getScaled(50)), image=maliang.PhotoImage(self.makeImageBlur(self.mergeImage(self.IMG_bg.crop((0, 0, (self.UI_WIDTH, self.UI_HEIGHT)[0], self.APP_finder_height)), self.makeMaskImage(size=((self.UI_WIDTH, self.UI_HEIGHT)[0], self.APP_finder_height))))))

        self.WDG_finder_icon = maliang.Image(self.WDG_finder, position=(self.getScaled(30), self.APP_finder_height // 1.9), image=maliang.PhotoImage(self.IMG_icon_logo.resize((self.getScaled(30), self.getScaled(30)), 1)), anchor='center')
        self.WDG_finder_title = maliang.Text(self.WDG_finder, position=(self.getScaled(65), self.APP_finder_height // 3.75), text=self.SET_USER, family=self.UI_FAMILY, fontsize=self.getScaled(15), weight='bold')
        self.WDG_finder_title.style.set(fg=('#FFFFFF'))

        self.WDG_finder_MenuBar = maliang.SegmentedButton(
            self.WDG_finder,
            text=['File', 'Edit', 'Go', 'Window', 'Help'],
            position=(
                self.WDG_finder_title.position[0] +
                self.WDG_finder_title.size[0] +
                self.getScaled(5),
                self.APP_finder_height // 2 +
                self.getScaled(2)
            ),
            family=self.UI_FAMILY,
            fontsize=self.getScaled(15),
            anchor='w',
            command=self.MenuHandler
        )
        self.WDG_finder_MenuBar.style.set(bg=('', ''), ol=('', ''))

        for i in self.WDG_finder_MenuBar.children:
            i.style.set(fg=('#CCCCCC', '#DDDDDD', '#FFFFFF', '#CCCCCC', '#FFFFFF', '#FFFFFF'), bg=('', '', '', '', '', ''), ol=('', '', '', '', '', ''))

        self.WDG_finder_time = maliang.Text(self.WDG_finder, position=((self.UI_WIDTH, self.UI_HEIGHT)[0] - self.getScaled(50), self.getScaled(12)), text=datetime.datetime.now().strftime("%H:%M"), family=self.UI_FAMILY, fontsize=self.getScaled(15), weight='bold')
        self.WDG_finder_time.style.set(fg=('#FFFFFF'))

        self.WDG_finder_inputMethod_shape = maliang.Image(self.WDG_finder, position=((self.UI_WIDTH, self.UI_HEIGHT)[0] - self.getScaled(145), self.getScaled(13)), image=maliang.PhotoImage(self.makeRadiusImage(self.makeMaskImage((self.getScaled(85), self.getScaled(20)), color=(255, 255, 255, 255)), radius=5, alpha=1)))
        self.WDG_finder_inputMethod_text = maliang.Text(self.WDG_finder_inputMethod_shape, anchor='center', position=(self.WDG_finder_inputMethod_shape.size[0] // 2, self.WDG_finder_inputMethod_shape.size[1] // 2), text='AlphaBet', fontsize=self.getScaled(15), family=self.UI_FAMILY, weight='bold')
        self.WDG_finder_inputMethod_text.style.set(fg=('#000000'))

        # self.testButton = maliang.Button(self.cv, position=(10, 60), size=(50, 50), command=self.setStatus)

        maliang.animation.MoveWidget(self.WDG_finder, offset=(0, self.getScaled(50)), duration=self.UI_ANIMATIME, controller=maliang.animation.ease_out, fps=self.UI_FPS).start(delay=self.UI_ANIMATIME // 2)

        # def autoUpdateMenubar():
        #     try:
        #         title, temp = self.getActiveApplicationMenu()

        #         if self.APP_FINDER_MENU != temp and len(temp) != 0:

        #             self.WDG_finder_MenuBar.destroy()
        #             self.APP_FINDER_MENU = temp
                    
        #             self.WDG_finder_title.set(title)
        #             self.WDG_finder_MenuBar = maliang.SegmentedButton(self.WDG_finder, text=self.APP_FINDER_MENU, position=(self.WDG_finder_title.position[0] + len(self.WDG_finder_title.get()) * self.getScaled(10) + self.getScaled(5), self.APP_finder_height // 2) + self.getScaled(1)), family=self.UI_FAMILY, fontsize=self.getScaled(15), anchor='w', command=self.dockHandler)
        #             self.WDG_finder_MenuBar.style.set(bg=('', ''), ol=('', ''))
        #             for i in self.WDG_finder_MenuBar.children:
        #                 i.style.set(fg=('#CCCCCC', '#DDDDDD', '#FFFFFF', '#CCCCCC', '#FFFFFF', '#FFFFFF'), bg=('', '', '', '', '', ''), ol=('', '', '', '', '', ''))


        #         self.root.after(500, autoUpdateMenubar)
        #     except:
        #         self.root.after(500, autoUpdateMenubar)

        # autoUpdateMenubar()
