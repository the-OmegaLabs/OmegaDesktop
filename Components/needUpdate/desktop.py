import datetime
from PIL import Image, ImageFilter, ImageDraw, ImageGrab
import maliang
import math
import maliang.animation
import maliang.theme
import maliang.toolbox

SCALE = 1.5
FOCUS = 0
LOWGPU = 0
animationFPS   = 1000
backgroundPath = 'bg/default.png'
avatarPath     = 'img/user.jpg'
iconPath       = 'img/main.png'
DMiconPath     = 'img/de.png'
loginUser      = 'Stevesuk'

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

def takeShot(*args):
    x, y = root.winfo_x(), root.winfo_y()
    img = ImageGrab.grab((x, y, x + WIDTH, y + HEIGHT))
    return img

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

def destroySubBar(event=None, fromSubBar=False):
    global subBarActivated
    try:
        if fromSubBar:
            subBarBack.destroy()
            subBar.destroy()
        else:
            if event.x < subBar.position[0] or event.x > subBar.position[0] + subBar.size[0] or event.y < subBar.position[1] or event.y > subBar.position[1] + subBar.size[1]:
                subBarBack.destroy()
                subBar.destroy()
    except:
        pass

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

def showAbout(appName, desc, version, company):
    aboutWindow = maliang.Label(cv, size=(scaled(300), scaled(400)), position=(WIDTH // 2 - scaled(150), HEIGHT // 2 - scaled(200)))

    maliang.Image(aboutWindow, position=(scaled(150), scaled(30)), anchor='n', image=maliang.PhotoImage(Image.open(DMiconPath).resize((scaled(200), scaled(200)), 1)))

    maliang.Text(aboutWindow, text=appName, 
                    position=(scaled(151), scaled(230)), anchor='center', 
                    family='源流黑体 CJK', fontsize=scaled(20), weight='bold')

    maliang.Text(aboutWindow, text=desc, 
                    position=(scaled(151), scaled(255)), anchor='center', 
                    family='源流黑体 CJK', fontsize=scaled(15)).style.set(fg='#DDDDDD')
    
    maliang.Text(aboutWindow, text=version, 
                    position=(scaled(151), scaled(275)), anchor='center', 
                    family='源流黑体 CJK', fontsize=scaled(10)).style.set(fg='#999999')
    
    maliang.Text(aboutWindow, text=company, 
                    position=(scaled(151), scaled(327)), anchor='center', 
                    family='源流黑体 CJK', fontsize=scaled(11)).style.set(fg='#DDDDDD')
    
    closeButton = maliang.Button(aboutWindow, text='确定', 
                    position=(scaled(151), scaled(355)), size=(scaled(100), scaled(40)), 
                    command=aboutWindow.destroy, anchor='center', family='源流黑体 CJK', fontsize=scaled(20))

    closeButton.style.set(ol=('', '', ''), bg=('', '', ''))

    enable_drag(aboutWindow)

def logout():
    maliang.animation.MoveWidget(dockBar, offset=(0, scaled(80)), duration=animationDuration, controller=maliang.animation.ease_out, fps=animationFPS).start(delay=animationDuration // 2)
    maliang.animation.MoveWidget(finderBar, offset=(0, 0 - scaled(50)), end=root.destroy, duration=animationDuration, controller=maliang.animation.ease_out, fps=animationFPS).start(delay=animationDuration // 2)
    
    
    
def subBarHandler(i):
    global subBarActivated
    subBarActivated = -1    
    destroySubBar(fromSubBar=True)

    if MenuBar.get() == 0 and i == 1:
        showAbout(appName='桌面', desc='OmegaOS 桌面体验', version='\"桌面\" 版本 1.0.0', company='© 2025 Omega Labs | OmegaOS 桌面环境')
    if MenuBar.get() == 0 and i == 9:
        logout()
        
        
def menubarHandler(i):
    global subBarBack, subBar, subBarActivated

    if subBarActivated == i:
        subBarActivated = -1
        destroySubBar(fromSubBar=True)
        return 0

    subBarActivated = i

    obj = []
    if i == 0:
        obj = [
            '关于本机',
            '关于桌面环境',
            '系统偏好设置...',
            'Plusto App Store...',
            '进程管理器...',
            '休眠',
            '重新启动...',
            '关机...',
            '锁定屏幕',
            f'退出登录 \"{loginUser}\"...              '
        ]
    elif i == 4:
        obj = [
            '关于此桌面环境',
        ]
        
        
    position = (MenuBar.children[i].position[0] + scaled(2), finderHEIGHT)
    
    subBar = maliang.SegmentedButton(
        finderBar, text=obj, position=position,
        family='源流黑体 CJK', fontsize=scaled(13), command=menubarHandler, layout='vertical'
    )

    size = subBar.size

    subBar.destroy()
        
    subBarBlur = makeImageBlur(backgroundImage.crop((position[0], position[1], position[0] + size[0], position[1] + size[1])))
    subBarMask = makeImageRadius(mergeImage(subBarBlur, makeImageMask(size)), alpha=1, radius=5)
    subBarBack = maliang.Image(cv, position=position, size=size, image=maliang.PhotoImage(subBarMask))

    subBar = maliang.SegmentedButton(
        finderBar, text=obj, position=position,
        family='源流黑体 CJK', fontsize=scaled(13), command=subBarHandler, layout='vertical'
    )
    
    subBar.style.set(bg=('', ''), ol=('', ''))
    for i in subBar.children:
        i.style.set(fg=('#DDDDDD', '#EEEEEE', '#FFFFFF', '#DDDDDD', '#FFFFFF', '#FFFFFF'), 
                    bg=('', '', '', '', '', ''), 
                    ol=('', '', '', '', '', ''))


backgroundImage = Image.open(backgroundPath).convert('RGBA')

image_width, image_height = backgroundImage.size
aspect_ratio = image_width / image_height
screen_aspect_ratio = WIDTH / HEIGHT

if aspect_ratio > screen_aspect_ratio:
    new_height = HEIGHT
    new_width = int(HEIGHT * aspect_ratio)
else:
    new_width = WIDTH
    new_height = int(WIDTH / aspect_ratio)

backgroundImage = backgroundImage.resize((new_width, new_height), 1)

left = (new_width - WIDTH) / 2
top = (new_height - HEIGHT) / 2
right = (new_width + WIDTH) / 2
bottom = (new_height + HEIGHT) / 2

backgroundImage = backgroundImage.crop((left, top, right, bottom))


domiantColor = getDominantColor(backgroundImage)
background = maliang.Image(cv, position=(0, 0), size=backgroundImage.size, image=maliang.PhotoImage(backgroundImage))

finderHEIGHT = scaled(45)
finderMask = makeImageMask(size=(WIDTH, finderHEIGHT))
finderBlur = makeImageBlur(mergeImage(backgroundImage.crop((0, 0, WIDTH, finderHEIGHT)), finderMask))
finderBar  = maliang.Image(cv, position=(0, 0), size=(WIDTH, finderHEIGHT), image=maliang.PhotoImage(finderBlur))
Icon = maliang.Image(finderBar, position=(scaled(30), scaled(45 // 1.9)), image=maliang.PhotoImage(iconImage.resize((scaled(30), scaled(30)), 1)), anchor='center')
Title = maliang.Text(finderBar, position=(scaled(65), scaled(45 // 3.75)), text='桌面', family='源流黑体 CJK', fontsize=scaled(15), weight='bold')
MenuBar = maliang.SegmentedButton(finderBar, text=['文件', '编辑', '前往', '窗口', '帮助'], position=(Title.position[0] + scaled(30) + scaled(len(Title.get()) * 4), scaled(45 // 2) + scaled(1)), family='源流黑体 CJK', fontsize=scaled(15), anchor='w', command=menubarHandler)
MenuBar.style.set(bg=('', ''), ol=('', ''))
nowTime = datetime.datetime.now()
Time = maliang.Text(finderBar, position=(WIDTH - scaled(12), finderHEIGHT // 2), text=f'{nowTime.month}/{nowTime.day} {nowTime.strftime(f"%a %H:%M")}', family='源流黑体 CJK', fontsize=scaled(15), weight='bold', anchor='e')
subBarActivated = -1

for i in MenuBar.children:
    i.style.set(fg=('#CCCCCC', '#DDDDDD', '#FFFFFF', '#CCCCCC', '#FFFFFF', '#FFFFFF'), bg=('', '', domiantColor, '', '', domiantColor), ol=('', '', '', '', '', ''))

root.bind("<Button-1>", lambda event: destroySubBar(event))

def launchApp(name):
    shakes = [-15, 15, -15, 15, -15, 15]
    def shakeAnimation(index):
        if index < len(shakes):
            i = shakes[index]
            duration = animationDuration // 3
            controller = maliang.animation.smooth

            animation = maliang.animation.MoveWidget(dockApplications['app'][name], offset=(0, scaled(i)), duration=duration, controller=controller, fps=animationFPS)
            animation.start()
            animation = maliang.animation.MoveWidget(dockApplications['tooltip'][name], offset=(0, scaled(i)), duration=duration, controller=controller, fps=animationFPS)
            animation.start()
            root.after(duration, shakeAnimation, index + 1)
        else:
            return 0

    cv.after(0, lambda: shakeAnimation(0))

icons = 2
dockHEIGHT = scaled(60)

dockBar = maliang.Label(cv, position=(WIDTH // 2, HEIGHT - dockHEIGHT - scaled(5)), size=(icons * dockHEIGHT, dockHEIGHT), anchor='n')
dockApplications = {'app': {}, 'tooltip': {}}

dockApplications['app']['finder'] = maliang.IconButton(dockBar, position=(0 - 1 * dockHEIGHT // 2, dockBar.size[1] // 2), size=(dockHEIGHT, dockHEIGHT), anchor='center', image=maliang.PhotoImage(Image.open('icons/file.png').resize((scaled(55), scaled(55)), 1)), command=lambda: (launchApp('finder')))
dockApplications['app']['settings'] = maliang.IconButton(dockBar, position=(1 * dockHEIGHT // 2, dockBar.size[1] // 2), size=(dockHEIGHT, dockHEIGHT), anchor='center', image=maliang.PhotoImage(Image.open('icons/settings.png').resize((scaled(55), scaled(55)), 1)), command=lambda: (launchApp('settings')))

maliang.configs.Env.system = 'Windows11'
dockApplications['tooltip']['finder'] = maliang.Tooltip(dockApplications['app']['finder'], text='文件管理器', align='up', fontsize=scaled(13), family='源流黑体 CJK')
dockApplications['tooltip']['settings'] = maliang.Tooltip(dockApplications['app']['settings'], text='系统偏好设置', align='up', fontsize=scaled(13), family='源流黑体 CJK')
maliang.configs.Env.system = 'Windows10'

dockBar.style.set(bg=('', ''), ol=('', ''))
dockBar.style.set(ol=('', ''))
for i in dockBar.children:
    i.style.set(bg=('', '', ''), ol=('', '', ''))

for i in dockApplications['tooltip']:
    dockApplications['tooltip'][i].style.set(ol=(''), theme='light')

maliang.animation.MoveWidget(finderBar, offset=(0, 0 - scaled(50)), duration=0, controller=maliang.animation.smooth, fps=animationFPS).start()
maliang.animation.MoveWidget(finderBar, offset=(0, scaled(50)), duration=animationDuration, controller=maliang.animation.ease_out, fps=animationFPS).start(delay=animationDuration // 2)

maliang.animation.MoveWidget(dockBar, offset=(0, scaled(80)), duration=0, controller=maliang.animation.smooth, fps=animationFPS).start()
maliang.animation.MoveWidget(dockBar, offset=(0, 0 - scaled(80)), duration=animationDuration, controller=maliang.animation.ease_out, fps=animationFPS).start(delay=animationDuration // 2)


root.mainloop()