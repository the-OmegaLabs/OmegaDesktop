import getpass
import maliang
import math
from PIL import Image, ImageFilter, ImageDraw
import maliang.theme
import maliang.toolbox
import datetime

SCALE = 2

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

maliang.toolbox.load_font('font.otf', private=True)
maliang.toolbox.load_font('light.otf', private=True)
maliang.toolbox.load_font('bold.otf', private=True)

root = maliang.Tk()
WIDTH = root.winfo_screenwidth()
HEIGHT = root.winfo_screenheight()
root.fullscreen(1)
iconImage = Image.open('main.png')
root.maxsize(WIDTH, HEIGHT)
root.minsize(WIDTH, HEIGHT)
root.icon(maliang.PhotoImage(iconImage))
maliang.theme.manager.customize_window(root, disable_maximize_button=True)

cv = maliang.Canvas(root, auto_zoom=False)
cv.place(width=WIDTH, height=HEIGHT)


finderHEIGHT = int(45 * SCALE)
backgroundImage = Image.open('background.png')
backgroundImage.thumbnail((WIDTH, WIDTH), Image.LANCZOS)

background = maliang.Image(cv, position=(0, 0), image=maliang.PhotoImage(backgroundImage))


finderMask = makeImageMask(size=(WIDTH, finderHEIGHT))
finderBlur = makeImageBlur(mergeImage(backgroundImage.crop((0, 0, WIDTH, finderHEIGHT)), finderMask))
finderBar  = maliang.Image(cv, position=(0, 0), size=(WIDTH, finderHEIGHT), image=maliang.PhotoImage(finderBlur))


Icon = maliang.Image(finderBar, position=(scaled(30), scaled(45 // 1.9)), image=maliang.PhotoImage(iconImage.resize((scaled(30), scaled(30)), 1)), anchor='center')
Title = maliang.Text(finderBar, position=(scaled(65), scaled(45 // 3.75)), text='登录管理器', family='源流黑体 CJK', fontsize=scaled(15), weight='bold')

now = datetime.datetime.now()
Time = maliang.Text(finderBar, position=(WIDTH - scaled(50), scaled(12)), text=now.strftime("%H:%M"), family='源流黑体 CJK', fontsize=scaled(15))

# loginContainer = maliang.Label(cv, position=(WIDTH // 2 - scaled(200), HEIGHT - scaled(500)), size=(scaled(400), scaled(400)))
loginContainer = maliang.Label(cv, position=(WIDTH // 2 - scaled(200), HEIGHT // 2 - scaled(200)), size=(scaled(400), scaled(400)))
loginContainer.style.set(fg=('', ''), bg=('', ''), ol=('', ''))
avatarImage = Image.open('user.jpg')
avatarImage = makeImageRadius(avatarImage, radius=avatarImage.size[0], alpha=0.9).resize((scaled(150), scaled(150)), 1)
account     = maliang.Image(loginContainer, position=(scaled(400) // 2, scaled(400) // 2.75), image=maliang.PhotoImage(avatarImage), anchor='center')
username    = maliang.Text(loginContainer, position=(scaled(400) // 2, scaled(400 / 1.55)), text=getpass.getuser(), family='源流黑体 CJK', fontsize=scaled(28), anchor='center', weight='bold')

passwdImg  = backgroundImage.crop((WIDTH // 2 - scaled(125), HEIGHT // 2 + scaled(103.03), WIDTH // 2 + scaled(125), HEIGHT // 2 + scaled(103.03) + scaled(35)))
passwdMask = mergeImage(makeImageBlur(passwdImg), makeImageMask(size=(passwdImg.size[0], passwdImg.size[1]), color=(0, 0, 0, 75)))
passwdMask = makeImageRadius(passwdMask, radius=scaled(5), alpha=1)

passwdbox   = maliang.Image(loginContainer, position=(scaled(400) // 2, scaled(400 // 1.25)), anchor='center', image=maliang.PhotoImage(passwdMask))
passwdwdg   = maliang.InputBox(passwdbox, position=(0, 0), anchor='center', size=(scaled(250), scaled(40)), fontsize=scaled(15), family='源流黑体 CJK', placeholder='密码', show='*')
passwdwdg.style.set(bg=('', '', ''), ol=('', '', ''))

root.mainloop()