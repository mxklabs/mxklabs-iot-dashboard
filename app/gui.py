import datetime
import matplotlib
import os
import tkinter

import core as intcore

matplotlib.use('TkAgg')

from tkinter.font import Font

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

PLOT_AREA = [0.065, 0.115, 0.9, 0.8]

def get_resource_filename(filename):
    return os.path.join(os.path.dirname(os.path.realpath(__file__)), '..',
                        'resources', filename)

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

        self.button_idle_image = tkinter.PhotoImage(
            file=get_resource_filename("button_idle.png"))
        self.button_selected_image = tkinter.PhotoImage(
            file=get_resource_filename("button_selected.png"))

        def make_button(text, view):
            return tkinter.Button(self,
               text=text,
               command=lambda: self._core.set_mode(view),
               image=self.button_idle_image,
               compound=tkinter.CENTER,
               foreground='#008888', activeforeground='white',
               bg='black', activebackground='black',
               bd=0, highlightthickness=0,
               highlightcolor='white')

        self._hour_view_button = make_button("HOUR", intcore.HOUR_VIEW)
        self._hour_view_button.place(x=700, y=80, width=100, height=50)

        self._day_view_button = make_button("DAY", intcore.DAY_VIEW)
        self._day_view_button.place(x=700, y=140, width=100, height=50)

        self._week_view_button = make_button("WEEK", intcore.WEEK_VIEW)
        self._week_view_button.place(x=700, y=200, width=100, height=50)

        self._month_view_button = make_button("MONTH", intcore.MONTH_VIEW)
        self._month_view_button.place(x=700, y=260, width=100, height=50)

        self._year_view_button = make_button("YEAR", intcore.YEAR_VIEW)
        self._year_view_button.place(x=700, y=320, width=100, height=50)

        self.figure = Figure(figsize=(6,4))
        #self.figure.tight_layout()
        #self.ax1 = #self.figure.add_subplot(111)
        self.ax1 = self.figure.add_axes(PLOT_AREA)
        #self.ax2 = self.ax1.twinx()

        self.canvas = FigureCanvasTkAgg(self.figure, master=self)
        self.canvas.get_tk_widget().place(x=0, y=0, width=700, height=480)
        self.canvas.draw()

        self._have_plot_update = False
        self._plot_update = None

        self._periodic_call()

    def update_plot(self, **kwargs):
        self._have_plot_update = True
        self._plot_update = kwargs

    def _periodic_call(self):
        if self._have_plot_update:
            self._update_plot()
            self._have_plot_update = False

        self.after(200, self._periodic_call)

    def _set_button_state(self, button, state):
        if state:
            button.config(image=self.button_selected_image,
                          foreground='#000000', activeforeground='white',
                          bg='black', activebackground='black')
        else:
            button.config(image=self.button_idle_image,
                          foreground='#008888', activeforeground='white',
                          bg='black', activebackground='black')

    def _update_plot(self):
        now = self._plot_update['now'].replace(minute=0, second=0, microsecond=0)

        self.ax1.clear()
        #self.ax2.clear()

        self.figure.patch.set_facecolor('black')

        self.ax1.spines['bottom'].set_color('white')
        self.ax1.spines['top'].set_color('white')
        self.ax1.spines['left'].set_color('white')
        self.ax1.spines['right'].set_color('white')
        self.ax1.xaxis.label.set_color('white')
        self.ax1.yaxis.label.set_color('white')
        self.ax1.tick_params(axis='x', colors='white')
        self.ax1.tick_params(axis='y', colors='white')
        self.ax1.set_facecolor('black')

        self.ax1.set_title(self._plot_update['title'], fontsize=16, color='white')

        plots = [(self.ax1, 'humidity', '#008888', 'Humidity (%)'), (self.ax1, 'temperature', '#cccccc', 'Temperature (C)')]

        for plot in plots:
            ax = plot[0]
            colour = plot[2]
            label = plot[3]

            x = self._plot_update['x_{}'.format(plot[1])]
            y = self._plot_update['y_{}'.format(plot[1])]

            if (len(y) > 0 and isinstance(y[0],float)):
                p1 = ax.plot(x, y, color=colour, label=label)
            else:
                ymin = [i[0] for i in y]
                ymax = [i[1] for i in y]
                p1_min = ax.plot(x, ymax, color=colour, label=label)
                p1_max = ax.plot(x, ymin, color=colour, label='_nolegend_', linestyle='dashed', dashes=[1,1])

                start_indexes = [0] + [i + 1 for i in range(len(x)) if ymin[i] is None]
                end_indexes = [i for i in range(len(x)) if ymin[i] is None] + [len(x)]

                for x1, x2 in zip(start_indexes, end_indexes):
                     ax.fill_between(x[x1:x2], y1=ymin[x1:x2], y2=ymax[x1:x2], facecolor=colour, alpha=0.3)

        legend = self.ax1.legend(loc='upper right', facecolor='black')

        for text in legend.get_texts():
            text.set_color("white")
        self.ax1.set_ylim((0,100))
        self.ax1.set_yticks(range(0,110,10))

        mode = self._core.get_mode()

        self._set_button_state(self._hour_view_button, mode == intcore.HOUR_VIEW)
        self._set_button_state(self._day_view_button, mode == intcore.DAY_VIEW)
        self._set_button_state(self._week_view_button, mode == intcore.WEEK_VIEW)
        self._set_button_state(self._month_view_button, mode == intcore.MONTH_VIEW)
        self._set_button_state(self._year_view_button, mode == intcore.YEAR_VIEW)


        #self.ax1.format_xdata = matplotlib.dates.DateFormatter('%H:%M')
        #self.ax2.format_xdata = matplotlib.dates.DateFormatter('%H:%M')
        #self.ax1.xaxis.set_major_formatter(matplotlib.dates.DateFormatter('%m/%d/%Y'))
        #self.ax1.xaxis.set_major_locator(matplotlib.dates.DayLocator())

        self.ax1.margins(x=0, y=0)
        self.ax1.set_xlim(self._plot_update['x_lim'])
        self.ax1.grid(b=True, color='#222222')

        self.ax1.set_xticks(self._plot_update['x_ticks'])
        self.ax1.tick_params(axis='x', rotation=45)
        self.ax1.set_xticklabels(self._plot_update['x_ticklabels'])

        #self.ax2.set_ylim((0, 35))
        #self.ax2.set_yticks(range(0,40,5))
        ##  self.ax2.tick_params(axis='y', colors='#cccccc')

        #self.figure.autofmt_xdate()

        #self.ax1.set_xlabel("X", fontsize=14)
        #self.figure.legend((p1,p2), ('Relative Humidity (%)', 'Temperature (C)'), edgecolor='white')
        self.canvas.draw()

#def signal_handler(signum, frame):
#    gui.root.quit()
#    gui.root.update()

# Set the signal handler.
#signal.signal(signal.SIGINT, signal_handler)
