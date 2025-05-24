import math
import maliang.theme
import Frameworks.Logger as Logger
import maliang
from simpleeval import SimpleEval

from PIL import (
    Image
)

from math import * # for advance computing

class Application():
    def getScaled(self, number) -> int:
        return int(number * self.UI_SCALE)

    def __init__(self, args):
        self.status = False

        self.bus          = args 
        self.IS_DEVMODE   = args.IS_DEVMODE   

        self.UI_SCALE     = args.UI_SCALE       
        self.UI_WIDTH     = self.getScaled(400)
        self.UI_HEIGHT    = self.getScaled(50) 
        self.UI_THEME     = args.UI_THEME 

        self.IMG_icon_logo   = Image.open('./Resources/icons/calculator.png')

        self.createWindow()
        self.loadWidget()

        max_key_len = max(len(key) for key in self.__dict__)  
        for key, value in self.__dict__.items():
            Logger.output(f'{key:<{max_key_len}} <type \'{type(value).__name__}\'>', type=Logger.Type.DEBUG)

        def reset(event):
            self.WDG_prompt.destroy()
            self.UI_WIDTH = event.width
            self.loadWidget()

        self.root.bind('<Configure>', reset)
        self.root.mainloop()

    def createWindow(self):        
        maliang.Env.system = 'Windows10'

        maliang.theme.set_color_mode(self.UI_THEME)
        
        self.root = maliang.Tk(size=(self.UI_WIDTH, self.UI_HEIGHT))
        self.root.icon(maliang.PhotoImage(self.IMG_icon_logo))
        self.root.title('Calculator')

        self.root.maxsize(self.getScaled(10000), self.UI_HEIGHT)
        self.root.minsize(self.getScaled(300), self.UI_HEIGHT)

        self.cv = maliang.Canvas(self.root)
        self.cv.place(x=0, y=0, width=self.getScaled(10000), height=self.UI_HEIGHT)

    def compute(self, expression: str):
        try:
            if not expression:
                self.root.destroy()
                return

            s = SimpleEval()
            s.functions.update({
                name: obj for name, obj in vars(math).items()
                if not name.startswith("__")
            })
            s.functions.update({
                'abs': abs,
                'round': round,
                'pow': pow
            })

            result = s.eval(expression.strip())
            self.WDG_prompt.set(str(result))

        except Exception as f:
            self.WDG_prompt.style.set(fg=('#FF0000', '#FF0000', '#FF0000'), ol=('#FF0000', '#FF0000', '#FF0000'))
            self.WDG_prompt.disable(True)
            self.WDG_prompt.set(str(f))
            self.cv.after(1000, self.recoverStyle)


    def recoverStyle(self):
        self.WDG_prompt.disable(False)
        self.WDG_prompt.set("")
        self.WDG_prompt.style.set(fg=('#FFFFFF', '#FFFFFF', '#FFFFFF'), ol=('#797979', '#797979', '#0078D7'))

    def loadWidget(self):
        self.WDG_prompt = maliang.InputBox(self.cv, size=(self.UI_WIDTH - self.getScaled(5), self.UI_HEIGHT - self.getScaled(5)), position=(self.getScaled(3), self.getScaled(3)), family='Consolas', fontsize=self.getScaled(18))
        self.root.bind('<Return>', lambda _: self.compute(self.WDG_prompt.get()))