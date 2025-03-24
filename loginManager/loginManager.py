import getpass
import maliang
import math
from PIL import Image, ImageFilter, ImageDraw
import maliang.animation
import maliang.theme
import maliang.toolbox
import datetime

SCALE = 1
FOCUS = 0
LOWGPU = 0
animationFPS = 100
backgroundPath = 'bg/default.png'
avatarPath = 'img/user.jpg'
iconPath = 'img/main.png'

maliang.Env.system = 'Windows10'

if LOWGPU:
    animationDuration = 0
else:
    animationDuration = 700

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


def makeImageMask(size, color=(0, 0, 0, 128), ):
    return Image.new("RGBA", size=size, color=color)


def mergeImage(a: Image, b: Image):
    try:
        return Image.alpha_composite(a, b)
    except ValueError as f:
        print(f'Can\'t merge image {a} and {b}: {f}.')

def scaled(number):
    return int(number * SCALE)

maliang.toolbox.load_font('font/font.otf', private=True)
maliang.toolbox.load_font('font/light.otf', private=True)
maliang.toolbox.load_font('font/bold.otf', private=True)

root = maliang.Tk(position=(150, 150))
# WIDTH = root.winfo_screenwidth()
# HEIGHT = root.winfo_screenheight()
# root.fullscreen(1)
WIDTH =  1366
HEIGHT = 768
iconImage = Image.open(iconPath)
root.maxsize(WIDTH, HEIGHT)
root.minsize(WIDTH, HEIGHT)
root.icon(maliang.PhotoImage(iconImage))
maliang.theme.manager.customize_window(root, disable_maximize_button=True)

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
finderBar  = maliang.Image(cv, position=(0, 0), size=(WIDTH, finderHEIGHT), image=maliang.PhotoImage(finderBlur))


Icon = maliang.Image(finderBar, position=(scaled(30), scaled(45 // 1.9)), image=maliang.PhotoImage(iconImage.resize((scaled(30), scaled(30)), 1)), anchor='center')
Title = maliang.Text(finderBar, position=(scaled(65), scaled(45 // 3.75)), text='登录管理器', family='源流黑体 CJK', fontsize=scaled(15), weight='bold')

now = datetime.datetime.now()
Time = maliang.Text(finderBar, position=(WIDTH - scaled(50), scaled(12)), text=now.strftime("%H:%M"), family='源流黑体 CJK', fontsize=scaled(15))

def setFocus(stat):
    global FOCUS
    FOCUS = stat

def login(passwd):
    print(passwd)

def loginFocus():
    global FOCUS, passwdbox, passwdwdg
    if FOCUS == 0:
        FOCUS = 2

        backgroundBlur()
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
    elif FOCUS == 2:
        pass

# loginContainer = maliang.Label(cv, position=(WIDTH // 2 - scaled(200), HEIGHT - scaled(500)), size=(scaled(400), scaled(400)))
loginContainer = maliang.Label(cv, position=(WIDTH // 2 - scaled(200), HEIGHT // 2 - scaled(200)), size=(scaled(400), scaled(400)))
loginContainer.style.set(fg=('', ''), bg=('', ''), ol=('', ''))
avatarImage = Image.open(avatarPath)
avatarImage = makeImageRadius(avatarImage, radius=avatarImage.size[0], alpha=0.9).resize((scaled(150), scaled(150)), 1)
account     = maliang.IconButton(loginContainer, size=(scaled(150), scaled(150)), position=(scaled(400) // 2, scaled(400) // 2.75), image=maliang.PhotoImage(avatarImage), anchor='center', command=lambda: loginFocus())
account.style.set(bg=('', '', ''), ol=('', '', ''))
username    = maliang.Text(loginContainer, position=(scaled(400) // 2, scaled(400 / 1.55)), text=getpass.getuser(), family='源流黑体 CJK', fontsize=scaled(28), anchor='center', weight='bold')
passwdImg   = backgroundImage.crop((WIDTH // 2 - scaled(125), HEIGHT // 2 + scaled(103.03), WIDTH // 2 + scaled(125), HEIGHT // 2 + scaled(103.03) + scaled(35)))
loginIcon   = Image.open('img/login.png')
passwdMask  = mergeImage(makeImageBlur(passwdImg), makeImageMask(size=(passwdImg.size[0], passwdImg.size[1]), color=(0, 0, 0, 96)))
passwdMask  = makeImageRadius(passwdMask, radius=scaled(5), alpha=1)


maliang.animation.MoveWidget(loginContainer, offset=(0, HEIGHT // 3), duration=0, controller=maliang.animation.smooth, fps=animationFPS).start()
maliang.animation.MoveWidget(finderBar, offset=(0, 0 - scaled(50)), duration=0, controller=maliang.animation.smooth, fps=animationFPS).start()
maliang.animation.MoveWidget(finderBar, offset=(0, scaled(50)), duration=animationDuration, controller=maliang.animation.ease_out, fps=animationFPS).start(delay=200)


root.mainloop()