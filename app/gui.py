__author__ = 'Dania'
import matplotlib
matplotlib.use('TkAgg')
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import tkinter

class Gui(tkinter.Tk):
    def __init__(self, debug, *args, **kwargs):
        super().__init__(*args, **kwargs)



        if not debug:
            super().attributes("-fullscreen", True)
            super().config(cursor="none")

        self.size = (800, 480)
        self.geometry("{}x{}".format(*self.size))
        self.box = tkinter.Entry(self)
        self.button = tkinter.Button(self, text="check", command=self.plot)
        self.box.pack ()
        self.button.pack()
        self.plot()

    def plot (self):
        x=np.array ([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
        v= np.array ([16,16.31925,17.6394,16.003,17.2861,17.3131,19.1259,18.9694,22.0003,22.81226])
        p= np.array ([16.23697,     17.31653,     17.22094,     17.68631,     17.73641 ,    18.6368,
            19.32125,     19.31756 ,    21.20247  ,   22.41444   ,  22.11718  ,   22.12453])

        fig = Figure(figsize=(6,4))
        a = fig.add_subplot(111)
        a.scatter(v,x,color='red')
        a.plot(p, range(2 +max(x)),color='blue')
        a.invert_yaxis()

        a.set_title ("Estimation Grid", fontsize=16)
        a.set_ylabel("Y", fontsize=14)
        a.set_xlabel("X", fontsize=14)

        canvas = FigureCanvasTkAgg(fig, master=self)
        canvas.get_tk_widget().pack()
        canvas.draw()

gui = Gui(debug=True)
gui.mainloop()