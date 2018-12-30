import matplotlib
import numpy as np
import os
import signal
import tkinter
import random

import input
import core

matplotlib.use('TkAgg')

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

THIS_HOUR = 'this-hour'
PREV_HOUR = 'prev-hour'

class Gui(tkinter.Tk):
    def __init__(self, debug, core, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._core = core

        if not debug:
            super().attributes("-fullscreen", True)
            super().config(cursor="none")

        self.size = (800, 480)
        self.geometry("{}x{}".format(*self.size))

        self.mxklabs_logo = tkinter.Label(self, text="mxklabs")
        self.mxklabs_logo.place(x=700, y=25, width=100, height=30)

        self.this_hour_button = tkinter.Button(self, text="THIS_HOUR",
            command=lambda : self._core.set_mode(core.THIS_HOUR))
        self.this_hour_button.place(x=700, y=50, width=100, height=50)

        self.prev_hour_button = tkinter.Button(self, text="PREV_HOUR",
            command=lambda : self._core.set_mode(core.PREV_HOUR))
        self.prev_hour_button.place(x=700, y=100, width=100, height=50)

        self.figure = Figure(figsize=(6,4))
        self.subplot = self.figure.add_subplot(111)

        self.canvas = FigureCanvasTkAgg(self.figure, master=self)
        self.canvas.get_tk_widget().place(x=0, y=0, width=700, height=480)
        self.canvas.draw()

        self._have_plot_update = False
        self._plot_update = None

        self._periodic_call()
    '''
    def populate_figure(self):
        # Today / Yesterday
        # This month / last month
        # This year / last year

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

        self._periodic_call()
    '''

    def update_plot(self, **kwargs):
        self._have_plot_update = True
        self._plot_update = kwargs

    def _periodic_call(self):
        if self._have_plot_update:
            self._update_plot()
            self._have_plot_update = False

        self.after(200, self._periodic_call)

    def _update_plot(self):
        #print("_plot_update")


        self.subplot.clear()

        self.figure.patch.set_facecolor('black')

        self.subplot.spines['bottom'].set_color('white')
        self.subplot.spines['top'].set_color('white')
        self.subplot.spines['left'].set_color('white')
        self.subplot.spines['right'].set_color('white')
        self.subplot.xaxis.label.set_color('white')
        self.subplot.yaxis.label.set_color('white')
        self.subplot.tick_params(axis='x', colors='white')
        self.subplot.tick_params(axis='y', colors='white')
        self.subplot.set_facecolor('black')

        p1 = self.subplot.plot(self._plot_update['x_humidity'],
                               self._plot_update['y_humidity'],
                               color='#008888')
        p2 = self.subplot.plot(self._plot_update['x_temperature'],
                               self._plot_update['y_temperature'],
                               color='#cccccc')

        # self.subplot.plot(p, range(2 +max(x)),color='blue')

        self.subplot.set_title(self._plot_update['title'], fontsize=16)
        #self.subplot.set_ylabel("Relative Humidity (%)", fontsize=14)
        self.subplot.set_ylim((0,100))
        self.subplot.set_yticks(range(0,110,10))

        self.subplot.set_xlim(self._plot_update['x_lim'])
        self.subplot.grid(b=True, color='#444444')
        #self.subplot.set_xlabel("X", fontsize=14)
        self.figure.legend((p1,p2), ('Relative Humidity (%)', 'Temperature (C)'))
        self.canvas.draw()

#def signal_handler(signum, frame):
#    gui.root.quit()
#    gui.root.update()

# Set the signal handler.
#signal.signal(signal.SIGINT, signal_handler)
