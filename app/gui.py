import datetime
import matplotlib
import tkinter

import core as intcore

matplotlib.use('TkAgg')

from tkinter.font import Font

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure


class Gui(tkinter.Tk):
    def __init__(self, debug, core, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._core = core
        self._logo_font = Font(family="Comfortaa", size=16)

        self.configure(background='black')

        if not debug:
            super().attributes("-fullscreen", True)
            super().config(cursor="none")

        self.size = (800, 480)
        self.geometry("{}x{}".format(*self.size))

        self.logo_panel = tkinter.PanedWindow(self, bg='black')
        self.logo_panel.place(x=700, y=0, width=100, height=50)

        self.mxklabs_logo1 = tkinter.Label(self.logo_panel, padx=0,
            text="mxk", font=self._logo_font, fg='#008888', bg='black')
        self.mxklabs_logo1.pack(side=tkinter.LEFT)

        self.mxklabs_logo2 = tkinter.Label(self.logo_panel, padx=0,
            text="labs", font=self._logo_font, fg='#cccccc', bg='black')
        self.mxklabs_logo2.pack(side=tkinter.LEFT)

        self._hour_view_button = tkinter.Button(self, text="HOUR\nVIEW",
            command=lambda : self._core.set_mode(intcore.HOUR_VIEW))
        self._hour_view_button.place(x=700, y=80, width=100, height=50)

        self._day_view_button = tkinter.Button(self, text="DAY\nVIEW",
            command=lambda : self._core.set_mode(intcore.DAY_VIEW))
        self._day_view_button.place(x=700, y=140, width=100, height=50)

        self._week_view_button = tkinter.Button(self, text="WEEK\nVIEW",
            command=lambda : self._core.set_mode(intcore.WEEK_VIEW))
        self._week_view_button.place(x=700, y=200, width=100, height=50)

        self._month_view_button = tkinter.Button(self, text="MONTH\nVIEW",
            command=lambda : self._core.set_mode(intcore.MONTH_VIEW))
        self._month_view_button.place(x=700, y=260, width=100, height=50)

        self._year_view_button = tkinter.Button(self, text="YEAR\nVIEW",
            command=lambda : self._core.set_mode(intcore.YEAR_VIEW))
        self._year_view_button.place(x=700, y=320, width=100, height=50)
        
        self.figure = Figure(figsize=(6,4))
        self.ax1 = self.figure.add_subplot(111)
        self.ax2 = self.ax1.twinx()

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

        self.ax1.clear()

        self.ax1.plot(x,v,color='red')
        #self.ax1.plot(p, range(2 +max(x)),color='blue')
        #self.ax1.invert_yaxis()

        self.ax1.set_title ("Estimation Grid", fontsize=16)
        self.ax1.set_ylabel("Y", fontsize=14)
        self.ax1.set_xlabel("X", fontsize=14)

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
        now = self._plot_update['now'].replace(minute=0, second=0, microsecond=0)

        # Update button text.
        #self._hour_view_button.config(text="" + \
        #    (now).strftime("%H:%M") + " - " + \
        #    (now + datetime.timedelta(hours=1)).strftime("%H:%M") + "")

        #self.prev_hour_button.config(text="" + \
        #    (now - datetime.timedelta(hours=1)).strftime("%H:%M") + " - " + \
        #    (now).strftime("%H:%M") + "")

        # Work out figure title.
        # TODO


        self.ax1.clear()
        self.ax2.clear()

        self.figure.patch.set_facecolor('black')

        self.ax1.spines['bottom'].set_color('white')
        self.ax1.spines['top'].set_color('white')
        self.ax1.spines['left'].set_color('white')
        self.ax1.spines['right'].set_color('white')
        self.ax1.xaxis.label.set_color('white')
        self.ax1.yaxis.label.set_color('white')
        self.ax1.tick_params(axis='x', colors='white')
        self.ax1.tick_params(axis='y', colors='#008888')
        self.ax1.set_facecolor('black')

        self.ax1.set_title(self._plot_update['title'], fontsize=16, color='white')

        p1 = self.ax1.plot(self._plot_update['x_humidity'],
                               self._plot_update['y_humidity'],
                               color='#008888')

        p2 = self.ax2.plot(self._plot_update['x_temperature'],
                      self._plot_update['y_temperature'],
                      color='#cccccc')

        self.ax1.set_ylim((0,100))
        self.ax1.set_yticks(range(0,110,10))

        #self.ax1.format_xdata = matplotlib.dates.DateFormatter('%H:%M')
        #self.ax2.format_xdata = matplotlib.dates.DateFormatter('%H:%M')
        #self.ax1.xaxis.set_major_formatter(matplotlib.dates.DateFormatter('%m/%d/%Y'))
        #self.ax1.xaxis.set_major_locator(matplotlib.dates.DayLocator())

        self.ax1.set_xlim(self._plot_update['x_lim'])



        self.ax1.grid(b=True, color='#222222')

        self.ax1.set_xticks(self._plot_update['x_ticks'])
        self.ax1.tick_params(axis='x', rotation=45)
        self.ax1.set_xticklabels(self._plot_update['x_ticklabels'])

        self.ax2.set_ylim((0, 35))
        self.ax2.set_yticks(range(0,40,5))
        self.ax2.tick_params(axis='y', colors='#cccccc')

        #self.figure.autofmt_xdate()

        #self.ax1.set_xlabel("X", fontsize=14)
        #self.figure.legend((p1,p2), ('Relative Humidity (%)', 'Temperature (C)'), edgecolor='white')
        self.canvas.draw()

#def signal_handler(signum, frame):
#    gui.root.quit()
#    gui.root.update()

# Set the signal handler.
#signal.signal(signal.SIGINT, signal_handler)
