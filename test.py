import maliang
from PIL import ImageGrab, Image
import mss
import threading

WIDTH = 1600
HEIGHT = 1000
RESAMPLE = 0

root = maliang.Tk(size=(WIDTH, HEIGHT), position=(0, 0))

def cheese():
    sct = mss.mss()
    shot = sct.grab(sct.monitors[1])
    img.set(maliang.PhotoImage(Image.frombytes("RGB", shot.size, shot.rgb).resize((WIDTH, HEIGHT), RESAMPLE)))

def update():
    while True:
        cheese()

cv = maliang.Canvas(root)
cv.place(x=0, y=0, width=WIDTH, height=HEIGHT)
img = maliang.Image(cv, (0, 0), size=(WIDTH, HEIGHT), image=maliang.PhotoImage(ImageGrab.grab().resize((WIDTH, HEIGHT), RESAMPLE)))

root.after(10, update)

root.mainloop()