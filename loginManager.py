import maliang
import math
from PIL import Image, ImageFilter
from PIL import ImageDraw2 as ImageDraw
import maliang.theme
import maliang.toolbox
import datetime

WIDTH = 1920
HEIGHT = 1200
SCALE = 1.25

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


def makeImageBlur(img, radius=5):
    return img.filter(ImageFilter.GaussianBlur(radius=radius))


def makeImageMask(size, color=(0, 0, 0, 128), ):
    return Image.new("RGBA", size=size, color=color)


def mergeImage(a: Image, b: Image):
    try:
        return Image.alpha_composite(a, b)
    except ValueError:
        print(f'Can\'t merge image {a} and {b}.')

def scaled(number):
    return int(number * SCALE)

maliang.toolbox.load_font('font.otf', private=True)
maliang.toolbox.load_font('light.otf', private=True)

root = maliang.Tk(size=(WIDTH, HEIGHT), title='OmegaOS Desktop | Compositor Interface')
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
finderBlur = makeImageBlur(mergeImage(backgroundImage.crop((0, 0, WIDTH, finderHEIGHT)), finderMask), 10)
finderBar  = maliang.Image(cv, position=(0, 0), size=(WIDTH, finderHEIGHT), image=maliang.PhotoImage(finderBlur))


Icon = maliang.Image(finderBar, position=(scaled(30), scaled(45 // 2)), image=maliang.PhotoImage(iconImage.resize((scaled(30), scaled(30)), 1)), anchor='center')
Title = maliang.Text(finderBar, position=(scaled(65), scaled(45 // 3.75)), text='账户管理器', family='源流黑体 CJK', fontsize=scaled(15), weight='bold')

nowTime = datetime.datetime.now()
Time = maliang.Text(finderBar, position=(WIDTH - scaled(50), scaled(12)), text=f'{nowTime.hour}:{nowTime.day}', family='源流黑体 CJK', fontsize=scaled(15))

root.mainloop()