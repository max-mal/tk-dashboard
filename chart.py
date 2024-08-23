from typing import Literal, Union
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg,
)
from matplotlib.figure import Figure
from tkinter import *
from tkinter.font import *

from datetime import datetime

import matplotlib
from matplotlib.animation import FuncAnimation

matplotlib.use('TkAgg')


class ChartWidget:
    def __init__(
        self,
        color='white',
        bg='black',
        mode: Union[Literal['data'], Literal['value']] = 'value',
        chart: Union[Literal['plot_date'], Literal['plot'], Literal['bar']] = 'plot_date',
        var=None,
        data=None,
        size_x=2,
        size_y=2,
    ):
        self.color = color
        self.bg = bg
        self.mode = mode
        self.var = var
        self.size_x = size_x
        self.size_y = size_y
        self.chart = chart

        self.x_data = []
        self.y_data = []

        if data is not None:
            self.x_data = data[0]
            self.y_data = data[1]

        if self.mode == 'data' and self.var:
            val = self.var.get()
            self.x_data = val[0]
            self.y_data = val[1]

    def _on_var_update(self):
        if self.var is None:
            return

        if self.mode == 'value':
            self.x_data.append(datetime.now())
            self.y_data.append(self.var.get())

        if self.mode == 'data':
            value = self.var.get()
            self.x_data = value[0]
            self.y_data = value[1]

    def _anim_update(self, _):
        self.line.set_data(self.x_data, self.y_data)
        self.figure.gca().relim()
        self.figure.gca().autoscale_view()
        return self.line,

    def make(self, parent):
        matplotlib.rcParams['axes.titlecolor'] = self.color
        matplotlib.rcParams['axes.labelcolor'] = self.color
        matplotlib.rcParams['axes.edgecolor'] = self.color
        matplotlib.rcParams['text.color'] = self.color

        # matplotlib.rc('axes',edgecolor=self.color)

        # create a figure
        self.figure = Figure(dpi=100, figsize=(self.size_x, self.size_y))
        self.figure.patch.set_facecolor(self.bg)

        # create FigureCanvasTkAgg object
        fr = Frame(parent, bg=self.bg, padx=10, pady=10)
        figure_canvas = FigureCanvasTkAgg(self.figure, fr)

        # create axes
        axes = self.figure.add_subplot()
        axes.patch.set_facecolor(self.bg)

        axes.spines['bottom'].set_color(self.color)
        axes.spines['top'].set_color(self.color)
        axes.xaxis.label.set_color(self.color)
        axes.tick_params(axis='x', colors=self.color)
        axes.tick_params(axis='y', colors=self.color)

        # x_data, y_data = [], []
        plot_fn = None
        if self.chart == 'plot_date':
            plot_fn = axes.plot_date
        if self.chart == 'plot':
            plot_fn = axes.plot
        if self.chart == 'bar':
            plot_fn = axes.bar

        if plot_fn is None:
            print(f"plot_fn unknown: {self.chart}")
            plot_fn = axes.plot

        if self.chart == 'bar':
            self.line = plot_fn(self.x_data, self.y_data, color=self.color)
        else:
            self.line, = plot_fn(self.x_data, self.y_data, '-', color=self.color)

        if self.var is not None:
            self.var.trace_add(
                'write',
                lambda _, __, ___: self._on_var_update()
            )

            self.anim = FuncAnimation(
                self.figure,
                self._anim_update,
                interval=1000
            )

        figure_canvas.get_tk_widget().pack(side=TOP, fill='x', expand=0)

        return fr
