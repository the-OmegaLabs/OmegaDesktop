import os
import threading
import maliang
import math
from PIL import Image, ImageFilter, ImageDraw
import maliang.animation
import maliang.theme
import maliang.toolbox
import datetime
import pam
import platform
from lunardate import LunarDate

SCALE = 1.5
FOCUS = 0
LOWGPU = 0
animationFPS   = 1000
backgroundPath = 'bg/default.png'
avatarPath     = 'img/user.jpg'
iconPath       = 'img/main.png'
DMiconPath     = 'img/dm.png'
loginUserName  = 'Stevesuk'

if LOWGPU:
    animationDuration = 0
else:
    animationDuration = 700

def getDominantColor(image):
    image = image.convert('RGB')
    colors = image.getcolors(image.size[0] * image.size[1])
    
    topColors = sorted(colors, key=lambda x: x[0], reverse=True)[:300]
    
    brightnessValues = []
    for count, (r, g, b) in topColors:
        brightness = 0.299 * r + 0.587 * g + 0.114 * b
        brightnessValues.append((brightness, (r, g, b)))
    
    brightestColor = max(brightnessValues, key=lambda x: x[0])[1]
    
    return f"#{brightestColor[0]:02X}{brightestColor[1]:02X}{brightestColor[2]:02X}"    

def showAbout():
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

    aboutWindow = maliang.Label(cv, size=(scaled(300), scaled(400)), position=(WIDTH // 2 - scaled(150), HEIGHT // 2 - scaled(200)))

    maliang.Image(aboutWindow, position=(scaled(150), scaled(30)), anchor='n', image=maliang.PhotoImage(Image.open(DMiconPath).resize((scaled(200), scaled(200)), 1)))

    maliang.Text(aboutWindow, text='显示管理器', 
                    position=(scaled(151), scaled(230)), anchor='center', 
                    family='源流黑体 CJK', fontsize=scaled(20), weight='bold')

    maliang.Text(aboutWindow, text='1.0.0', 
                    position=(scaled(151), scaled(255)), anchor='center', 
                    family='源流黑体 CJK', fontsize=scaled(15)).style.set(fg='#999999')
    
    maliang.Text(aboutWindow, text='© 2025 Omega Labs | OmegaOS 桌面环境', 
                    position=(scaled(151), scaled(327)), anchor='center', 
                    family='源流黑体 CJK', fontsize=scaled(11)).style.set(fg='#DDDDDD')
    
    closeButton = maliang.Button(aboutWindow, text='Close', 
                    position=(scaled(151), scaled(355)), size=(scaled(100), scaled(40)), 
                    command=aboutWindow.destroy, anchor='center', family='源流黑体 CJK', fontsize=scaled(20))

    closeButton.style.set(ol=('', '', ''), bg=('', '', ''))

    enable_drag(aboutWindow)


def getRatio(size):
    gcd = math.gcd(size[0], size[1]) 
    return f"{size[0] // gcd}:{size[1] // gcd}"

def makeImageRadius(img, radius=30, alpha=0.5):
    img = img.convert("RGBA")

    mask = Image.new("L", img.size, 0)
    draw = ImageDraw.Draw(mask)

    draw.rounded_rectangle(
        (0, 0, img.size[0], img.size[1]), radius, fill=int(256 * alpha))

    img.putalpha(mask)

    return img


def makeImageBlur(img, radius=10):
    return img.filter(ImageFilter.GaussianBlur(radius=radius))


def makeImageMask(size, color=(0, 0, 0, 128)):
    return Image.new("RGBA", size=size, color=color)


def mergeImage(a: Image, b: Image):
    try:
        return Image.alpha_composite(a, b)
    except ValueError as f:
        print(f'Can\'t merge image {a} and {b}: {f}.')

def scaled(number):
    return int(number * SCALE)

maliang.toolbox.load_font('font/light.otf', private=True)
maliang.toolbox.load_font('font/bold.otf', private=True)

root = maliang.Tk(position=(-5, 0))
root.title('[DEVELOPMENT] Omega Desktop Compositor')
WIDTH = root.winfo_screenwidth()
HEIGHT = root.winfo_screenheight()
root.fullscreen(1)
# WIDTH  = 1600
# HEIGHT = 900
iconImage = Image.open(iconPath)
root.maxsize(WIDTH, HEIGHT)
root.minsize(WIDTH, HEIGHT)
root.icon(maliang.PhotoImage(iconImage))

maliang.Env.system = 'Windows10'
maliang.theme.manager.set_color_mode('dark')

cv = maliang.Canvas(root, auto_zoom=False)
cv.place(width=WIDTH, height=HEIGHT)


finderHEIGHT = int(45 * SCALE)
backgroundImage = Image.open(backgroundPath).convert('RGBA')
backgroundImage.thumbnail((WIDTH, WIDTH), 1)


background = maliang.Image(cv, position=(0, 0), image=maliang.PhotoImage(backgroundImage))
blurBackground = maliang.Image(cv, position=(0, HEIGHT * 1.5), image=maliang.PhotoImage(makeImageBlur(backgroundImage, 15)))

backList = []

def backgroundBlur():
    maliang.animation.MoveWidget(blurBackground, offset=(0, 0 - HEIGHT * 1.5), duration=animationDuration,
                                     controller=maliang.animation.ease_out, fps=animationFPS).start()

def backgroundNoBlur():
    maliang.animation.MoveWidget(blurBackground, offset=(0, HEIGHT * 1.5), duration=animationDuration,
                                     controller=maliang.animation.smooth, fps=animationFPS).start()


finderMask = makeImageMask(size=(WIDTH, finderHEIGHT))
finderBlur = makeImageBlur(mergeImage(backgroundImage.crop((0, 0, WIDTH, finderHEIGHT)), finderMask))

def menubarHandler(name):
    if name == 0:
        os.system('systemctl poweroff')
        if platform.system() != 'Linux':
            root.destroy()
    
    elif name == 1:
        os.system('systemctl reboot')
    
    elif name == 2:
        os.system('systemctl reboot --firmware-setup')

    elif name == 3:
        showAbout()

    else:
        print(f"Unknown command: {name}")

def setFocus(stat):
    global FOCUS
    FOCUS = stat

def login(passwd):    
    loginButton.destroy()
    
    passwdwdg.disable(True)
    passwdwdg.master.focus('')
    spinner = maliang.Spinner(passwdwdg, position=(scaled(107), scaled(0)), anchor='center', size=(scaled(20), scaled(20)), widths=(3, 3), mode='indeterminate')
    
    shakes = [-15, 30, -30, 30, -15]

    def shakeAnimation(index):
        if index < len(shakes):
            i = shakes[index]
            animation = maliang.animation.MoveWidget(passwdbox, offset=(i, 0), duration=animationDuration // 4, controller=maliang.animation.ease_out, fps=animationFPS)
            animation.start()
            root.after(animationDuration // 8, shakeAnimation, index + 1)
        else:
            loginFocus()

    def failed():
        cv.after(0, lambda: spinner.destroy())  
        cv.after(0, lambda: passwdbox.set(maliang.PhotoImage(passwdEMask)))
        cv.after(0, lambda: shakeAnimation(0))

    def success():
        maliang.animation.MoveWidget(finderBar, offset=(0, 0 - scaled(50)), duration=animationDuration, controller=maliang.animation.ease_out, fps=animationFPS).start(delay=animationDuration // 2)
        root.after(500, lambda: (loginFocus(), spinner.destroy()))
        root.after(1000, lambda: (os.system('python desktop.py')))
        root.after(1000, lambda: maliang.animation.MoveWidget(finderBar, offset=(0, scaled(50)), duration=animationDuration, controller=maliang.animation.ease_out, fps=animationFPS).start())

    
    def authenticate():
        if platform.system() == 'Linux':
            auth = pam.pam()
            if auth.authenticate(loginUserName, passwd):
                success()
            else:
                failed()
        else:
            if not passwd:
                failed()
            else:
                success()

    
    threading.Thread(target=authenticate, daemon=True).start()

def generateTimeText(now: datetime.datetime):
    global timeText, timebg, timeShadow
    nowTime = now.strftime('%H:%M')

    lunarDate = LunarDate.fromSolarDate(now.year, now.month, now.day)

    weekday = ["一", "二", "三", "四", "五", "六", "日"][now.weekday()]
    monthCN = ["", "一", "二", "三", "四", "五", "六", "七", "八", "九", "十", "十一", "十二"]
    dayCN = ["", "初一", "初二", "初三", "初四", "初五", "初六", "初七", "初八", "初九", "初十",
                "十一", "十二", "十三", "十四", "十五", "十六", "十七", "十八", "十九", "二十",
                "廿一", "廿二", "廿三", "廿四", "廿五", "廿六", "廿七", "廿八", "廿九", "三十"]
    ganzhiYear = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
    ganzhiMonth = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]
    yearGanZhi = f"{ganzhiYear[(lunarDate.year - 4) % 10]}{ganzhiMonth[(lunarDate.year - 4) % 12]}"

    nowDate = f'{now.month}月{now.day}日 星期{weekday} {yearGanZhi}年{monthCN[lunarDate.month]}月{dayCN[lunarDate.day]}'

    n1, n2, sp, n3, n4 = nowTime[0], nowTime[1], nowTime[2], nowTime[3], nowTime[4]

    timebg   = maliang.Image(cv, position=(WIDTH // 2 + scaled(2), HEIGHT // 6 + scaled(5)), anchor='center') # , image=maliang.PhotoImage(timeBack)

    timeShadow = []
    timeShadow.append(maliang.Text(cv, position=(WIDTH // 2 - scaled(35) * 1.85 + scaled(1), HEIGHT // 5 + scaled(1)), text=n1, family='源流黑体 CJK', fontsize=scaled(65), weight='bold', anchor='center'))
    timeShadow.append(maliang.Text(cv, position=(WIDTH // 2 - scaled(35) * 0.8 + scaled(1), HEIGHT // 5 + scaled(1)), text=n2, family='源流黑体 CJK', fontsize=scaled(65), weight='bold', anchor='center'))
    timeShadow.append(maliang.Text(cv, position=(WIDTH // 2 + scaled(1), HEIGHT // 5 + scaled(1)), text=sp, family='源流黑体 CJK', fontsize=scaled(60), weight='bold', anchor='center'))    
    timeShadow.append(maliang.Text(cv, position=(WIDTH // 2 + scaled(35) * 0.8 + scaled(1), HEIGHT // 5 + scaled(1)), text=n3, family='源流黑体 CJK', fontsize=scaled(65), weight='bold', anchor='center'))
    timeShadow.append(maliang.Text(cv, position=(WIDTH // 2 + scaled(35) * 1.93 + scaled(1), HEIGHT // 5 + scaled(1)), text=n4, family='源流黑体 CJK', fontsize=scaled(65), weight='bold', anchor='center'))    

    timeText = []
    timeText.append(maliang.Text(cv, position=(WIDTH // 2 - scaled(35) * 1.85, HEIGHT // 5), text=n1, family='源流黑体 CJK', fontsize=scaled(65), weight='bold', anchor='center'))
    timeText.append(maliang.Text(cv, position=(WIDTH // 2 - scaled(35) * 0.8, HEIGHT // 5), text=n2, family='源流黑体 CJK', fontsize=scaled(65), weight='bold', anchor='center'))
    timeText.append(maliang.Text(cv, position=(WIDTH // 2, HEIGHT // 5), text=sp, family='源流黑体 CJK', fontsize=scaled(60), weight='bold', anchor='center'))    
    timeText.append(maliang.Text(cv, position=(WIDTH // 2 + scaled(35) * 0.8, HEIGHT // 5), text=n3, family='源流黑体 CJK', fontsize=scaled(65), weight='bold', anchor='center'))
    timeText.append(maliang.Text(cv, position=(WIDTH // 2 + scaled(35) * 1.93, HEIGHT // 5), text=n4, family='源流黑体 CJK', fontsize=scaled(65), weight='bold', anchor='center'))    
    timeText.append(maliang.Text(cv, position=(WIDTH // 2 + scaled(7), timebg.position[1] - scaled(37)), text=nowDate, anchor='n', family='源流黑体 CJK', fontsize=scaled(19)))

    for i, widget in enumerate(timeShadow):
        widget.style.set(fg=('#9F9F9F'))

    for i, widget in enumerate(timeText):
        widget.style.set(fg=('#EEEEEE'))

    for i in (0, 1, 3, 4):
        if timeText[i].get() == '1':
            timeText[i].style.set(fg=(getDominantColor(backgroundImage)))
            break


def loginFocus():
    global FOCUS, passwdbox, passwdwdg, loginButton, passwdImg
    if FOCUS == 0:
        FOCUS = 2

        for i in timeText:
            i.destroy()
        for i in timeShadow:
            i.destroy()
        backgroundBlur()
        timebg.destroy()

        passwdbox   = maliang.Image(loginContainer, position=(scaled(400) // 2, scaled(400 // 1.25)), anchor='center', image=maliang.PhotoImage(passwdMask))
        passwdwdg   = maliang.InputBox(passwdbox, position=(0, 0), anchor='center', size=(scaled(250), scaled(40)), fontsize=scaled(15), family='源流黑体 CJK', placeholder='密码', show='*')
        loginButton = maliang.IconButton(passwdwdg, position=(scaled(107), scaled(0)), anchor='center', size=(scaled(30), scaled(30)), image=maliang.PhotoImage(loginIcon.resize((scaled(25), scaled(25)), 1)), command=lambda: login(passwdwdg.get()))
        passwdwdg.bind('<Return>', lambda _: login(passwdwdg.get()))
        passwdwdg.style.set(bg=('', '', ''), ol=('', '', ''))
        loginButton.style.set(bg=('', '', ''), ol=('', '', ''))
        

        maliang.animation.MoveWidget(loginContainer, end=lambda: setFocus(1), offset=(0, 0 - HEIGHT // 3), duration=animationDuration, controller=maliang.animation.ease_out, fps=animationFPS).start()
        
    elif FOCUS == 1:
        FOCUS = 2

        backgroundNoBlur()

        passwdwdg.destroy()
        passwdbox.destroy()
        maliang.animation.MoveWidget(loginContainer, end=lambda: (setFocus(0)), offset=(0, HEIGHT // 3), duration=animationDuration, controller=maliang.animation.ease_out, fps=animationFPS).start()

        generateTimeText(datetime.datetime.now())

    elif FOCUS == 2:
        pass

# loginContainer = maliang.Label(cv, position=(WIDTH // 2 - scaled(200), HEIGHT - scaled(500)), size=(scaled(400), scaled(400)))
loginContainer = maliang.Label(cv, position=(WIDTH // 2 - scaled(200), HEIGHT // 2 - scaled(200)), size=(scaled(400), scaled(400)))
loginContainer.style.set(fg=('', ''), bg=('', ''), ol=('', ''))
avatarImage = Image.open(avatarPath)
avatarImage = makeImageRadius(avatarImage, radius=avatarImage.size[0], alpha=0.9).resize((scaled(150), scaled(150)), 1)
account     = maliang.IconButton(loginContainer, size=(scaled(150), scaled(150)), position=(scaled(400) // 2, scaled(400) // 2.75), image=maliang.PhotoImage(avatarImage), anchor='center', command=lambda: loginFocus())
account.style.set(bg=('', '', ''), ol=('', '', ''))
loginUserO   = maliang.Text(loginContainer, position=(scaled(400) // 2 + scaled(1), scaled(400 / 1.55) + scaled(1)), text=loginUserName, family='源流黑体 CJK', fontsize=scaled(28), anchor='center', weight='bold')
loginUser    = maliang.Text(loginContainer, position=(scaled(400) // 2, scaled(400 / 1.55)), text=loginUserName, family='源流黑体 CJK', fontsize=scaled(28), anchor='center', weight='bold')
loginUserO.style.set(fg=('#666666'))
passwdImg   = backgroundImage.crop((WIDTH // 2 - scaled(125), HEIGHT // 2 + scaled(103.03), WIDTH // 2 + scaled(125), HEIGHT // 2 + scaled(103.03) + scaled(35)))
loginIcon   = Image.open('img/login.png')
passwdMask  = makeImageRadius(mergeImage(makeImageBlur(passwdImg), makeImageMask(size=(passwdImg.size[0], passwdImg.size[1]), color=(0, 0, 0, 96))), radius=scaled(5), alpha=1)
passwdEMask = makeImageRadius(mergeImage(makeImageBlur(passwdImg), makeImageMask(size=(passwdImg.size[0], passwdImg.size[1]), color=(96, 0, 0, 96))), radius=scaled(5), alpha=1)

finderBar  = maliang.Image(cv, position=(0, 0), size=(WIDTH, finderHEIGHT), image=maliang.PhotoImage(finderBlur))
Icon = maliang.Image(finderBar, position=(scaled(30), scaled(45 // 1.9)), image=maliang.PhotoImage(iconImage.resize((scaled(30), scaled(30)), 1)), anchor='center')
Title = maliang.Text(finderBar, position=(scaled(65), scaled(45 // 3.75)), text='显示管理器', family='源流黑体 CJK', fontsize=scaled(15), weight='bold')
MenuBar = maliang.SegmentedButton(finderBar, text=['关机', '重启', '进入固件设置', '关于'], position=(scaled(70) + scaled(5.75 * (8 + len(Title.get()))), scaled(45 // 2 + 1)), family='源流黑体 CJK', fontsize=scaled(15), anchor='w', command=menubarHandler)
MenuBar.style.set(bg=('', ''), ol=('', ''))
Time = maliang.Text(finderBar, position=(WIDTH - scaled(50), scaled(12)), text=datetime.datetime.now().strftime("%H:%M"), family='源流黑体 CJK', fontsize=scaled(15), weight='bold')
for i in MenuBar.children:
    i.style.set(fg=('#CCCCCC', '#DDDDDD', '#FFFFFF', '#CCCCCC', '#FFFFFF', '#FFFFFF'), bg=('', '', '', '', '', ''), ol=('', '', '', '', '', ''))

maliang.animation.MoveWidget(loginContainer, offset=(0, HEIGHT // 3), duration=0, controller=maliang.animation.smooth, fps=animationFPS).start()
maliang.animation.MoveWidget(finderBar, offset=(0, 0 - scaled(50)), duration=0, controller=maliang.animation.smooth, fps=animationFPS).start()
maliang.animation.MoveWidget(finderBar, offset=(0, scaled(50)), duration=animationDuration, controller=maliang.animation.ease_out, fps=animationFPS).start(delay=animationDuration // 2)

generateTimeText(datetime.datetime.now())


root.mainloop()
