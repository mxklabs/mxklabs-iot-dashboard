import matplotlib
import numpy as np
import tkinter
import random

matplotlib.use('TkAgg')

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

class Gui(tkinter.Tk):
    def __init__(self, debug, *args, **kwargs):
        super().__init__(*args, **kwargs)



        if not debug:
            super().attributes("-fullscreen", True)
            super().config(cursor="none")

        self.size = (800, 480)
        self.geometry("{}x{}".format(*self.size))
        self.box = tkinter.Entry(self)
        self.button = tkinter.Button(self, text="check", command=self.populate_figure)
        self.box.place(x=700, y=0, width=100, height=50)
        self.button.place(x=700, y=50, width=100, height=50)

        self.figure = Figure(figsize=(6,4))
        self.subplot = self.figure.add_subplot(111)

        self.canvas = FigureCanvasTkAgg(self.figure, master=self)
        self.canvas.get_tk_widget().place(x=0, y=0, width=700, height=480)
        self.canvas.draw()

    def populate_figure(self):
        x = np.array ([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
        v = np.array([random.uniform(10,20) for _ in x])
        p = np.array([random.uniform(10,20) for _ in x])

        print("v={}".format(v))

        self.subplot.clear()

        self.subplot.plot(x,v,color='red')
        #self.subplot.plot(p, range(2 +max(x)),color='blue')
        #self.subplot.invert_yaxis()

        self.subplot.set_title ("Estimation Grid", fontsize=16)
        self.subplot.set_ylabel("Y", fontsize=14)
        self.subplot.set_xlabel("X", fontsize=14)

        self.canvas.draw()


gui = Gui(debug=True)
gui.mainloop()