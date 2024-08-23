import os
from tkinter import *
from tkinter.font import *
from threading import Thread
import time
from datetime import datetime
from gauge import GaugeWidget
from chart import ChartWidget
from sources.mysql import MysqlSource
from config import config
from jsonpath_ng import jsonpath, parse


# Mimic tkinter var behavior
class GenericVar():
    def __init__(self):
        self.listeners = []
        self.value = None

    def get(self):
        return self.value

    def set(self, value):
        self.value = value
        self._trigger_listeners()

    def _trigger_listeners(self):
        for listener in self.listeners:
            listener(self.value, None, None)

    def trace_add(self, mode, callback):
        self.listeners.append(callback)


class App:
    def __init__(self, config):
        self.exit = False
        self.config = config

        self.registered_widgets = {
            'frame': self.make_frame,
            'label': self.make_label,
            'clocks': self.make_clocks,
            'gauge': self.make_gauge,
            'chart': self.make_chart,
        }

        self.variables = {}
        self.sources = {}

        self.bg = 'black'
        self.color = 'white'

        self.window = Tk()
        self.window.title("Dashboard")

        if os.environ.get('TEST') == "1":
            self.window.geometry('512x384')
        else:
            self.window.attributes('-fullscreen', True)

        self.window['padx'] = 20
        self.window['pady'] = 10
        self.window['bg'] = self.bg

        self.clocks_var = StringVar()
        self.variables['$clocks'] = self.clocks_var

        self.counter = IntVar()
        self.counter.set(0)
        self.variables['$counter'] = self.counter

        self.init_variables()
        self.init_sources()
        self.build(
            self.config.get('layout')
        )

    def init_variables(self):
        variables = self.config.get('variables', {})
        for var_name in variables.keys():
            params = variables.get(var_name)
            var_type = params.get('type', 'str')

            var = None
            if var_type == 'str':
                var = StringVar()
            if var_type == 'int':
                var = IntVar()
            if var_type == 'double':
                var = DoubleVar()
            if var_type == 'generic':
                var = GenericVar()

            if var is None:
                continue

            var_value = params.get('value')
            if var_value is not None:
                var.set(var_value)

            self.variables[var_name] = var

    def init_sources(self):
        sources = self.config.get('sources', {})

        for name in sources.keys():
            source = sources[name]
            source_type = source.get('type')

            if not source_type:
                continue
            if source_type == 'mysql':
                self.sources[name] = MysqlSource(source)

    def _build(self, parent, children, row=0):
        for index, widget_params in enumerate(children):
            widget_type = widget_params.get('_')
            widget_params['_col'] = index
            widget_params['_row'] = row

            widget_builder = self.registered_widgets.get(widget_type)

            widget = None
            if not widget_builder:
                widget = self.make_label(parent, {
                    'text': f'widget not found: {widget_type}'
                })
            else:
                widget = widget_builder(parent, widget_params)

            children = widget_params.get('children', [])
            self._build(widget, children)

    def build(self, tree: dict):
        for row_index, row in enumerate(tree):
            row_frame = Frame(self.window, pady=5, bg=self.bg)
            row_frame.grid(row=row_index, column=0, sticky="ew")
            self.window.grid_columnconfigure(0, weight=1)
            self._build(row_frame, row, row=row_index)

    def get_var(self, name):
        variable = None
        if name is not None:
            variable = self.variables.get(name)

        return variable

    def make_gauge(self, parent, params: dict):
        # thresholds {
        #     '_': 'green',
        #     '50': 'yellow',
        #     '100': 'red',
        # },

        w = GaugeWidget(
            parent=parent,
            width=params.get('width', 200),
            height=params.get('height', 100),
            arc_size=params.get('arc_size', 20),
            value=params.get('value', 0),
            unit=params.get('unit', ''),
            max_val=params.get('max'),
            thresholds=params.get('thresholds'),
            fg=self.color,
            bg=self.bg,
            fontsize=params.get('fontsize', 30),
            value_var=self.get_var(params.get('var'))
        )

        widget = w.make()
        widget.pack()

        return widget

    def make_chart(self, parent, params: dict):
        w = ChartWidget(
            color=params.get('color', self.color),
            bg=params.get('bg', self.bg),
            mode=params.get('mode', 'value'),
            var=self.get_var(params.get('var')),
            data=params.get('data'),
            size_x=params.get('size_x', 2),
            size_y=params.get('size_y', 2),
            chart=params.get('chart', 'plot_date')
        )

        widget = w.make(parent)
        widget.pack(side=TOP, fill='x', expand=0)

        return widget

    def make_clocks(self, parent, params: dict):
        fontsize = params.get('fontsize', 50)
        widget = self.make_label(parent, {
            'var': '$clocks',
            'fontsize': fontsize,
        })
        widget.pack()

        return widget

    def make_label(self, parent, params: dict):
        fontsize = params.get('fontsize', 20)
        text = params.get('text')
        textvar = params.get('var')
        color = params.get('color')

        variable = None
        if textvar is not None:
            variable = self.variables.get(textvar)

        if not color:
            color = self.color

        label = Label(
            parent,
            text=text,
            textvariable=variable,
            font=("Arial Bold", fontsize),
            bg=self.bg,
            fg=color
        )
        label.pack(fill='both', expand=1)

        return label

    def _set_frame_visibility(self, frame, var, row, col, weight, uniform, parent):
        value = var.get()
        if value:
            frame.grid(
                row=row,
                column=col,
                sticky="nsew"
            )
            parent.grid_columnconfigure(col, weight=weight, uniform=uniform)
        else:
            frame.grid_forget()
            parent.grid_columnconfigure(col, weight=0, uniform=uniform)

    def make_frame(self, parent, params: dict):
        col = params.get('_col', 0)
        row = params.get('_row', 0)

        weight = params.get('weight', 1)
        uniform = params.get('uniform', 'group1')
        title = params.get('title', '')

        frame = Frame(
            parent,
            background=self.bg,
            padx=5,
            # pady=2,
            highlightbackground='grey',
            highlightthickness=0
        )

        visible = params.get('visible', '1')
        if visible.startswith('$'):
            visible_var = self.get_var(visible)
            if visible_var is not None:
                visible = visible_var.get()
                visible_var.trace_add('write', lambda _, __, ___: self._set_frame_visibility(
                    frame,
                    visible_var,
                    row,
                    col,
                    weight,
                    uniform,
                    parent
                ))
            else:
                visible = False

        if visible:
            frame.grid(
                row=row,
                column=col,
                sticky="nsew"
            )

            parent.grid_columnconfigure(col, weight=weight, uniform=uniform)

        if len(title):
            self.make_label(frame, {
                'text': title,
                'fontsize': 15,
            })

        return frame

    def json_path(self, data, select_exp):
        exp = parse(select_exp)
        matches = exp.find(data)
        result = [match.value for match in matches]
        return result

    def get_sub_value(self, sub):
        source_name = sub.get('source')
        if not source_name:
            return None

        source = self.sources.get(source_name)
        if not source:
            return None

        fn = getattr(source, sub.get('action'))
        if not fn:
            return None

        args = sub.get('args', [])
        result = fn(*args)

        if sub.get('get', 'all') == 'chart':
            data_x = self.json_path(result, sub.get('select_x'))
            data_y = self.json_path(result, sub.get('select_y'))
            return [data_x, data_y]

        select_exp = sub.get('select')
        if select_exp is not None:
            result = self.json_path(result, select_exp)

        if sub.get('get', 'all') == 'first':
            return result[0]

        return result

    def process_subs(self):
        subs = self.config.get('subs', {})
        for sub_name in subs.keys():
            sub = subs[sub_name]
            value = self.get_sub_value(sub)

            if value is not None:
                var = self.get_var(sub_name)
                if var is None:
                    continue

                var.set(value)

    def ticker(self):
        while not self.exit:
            a = datetime.today()
            self.clocks_var.set(a.strftime("%H:%M:%S"))
            time.sleep(0.1)

    def subs_thread(self):
        while not self.exit:
            time.sleep(3)
            self.process_subs()

    def run(self):
        t = Thread(target=self.ticker, args=[])
        t.start()

        t1 = Thread(target=self.subs_thread, args=[])
        t1.start()

        self.window.mainloop()
        self.exit = True

        t.join()
        t1.join()


app = App(config)
app.run()
