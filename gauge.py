from tkinter import *
from tkinter.font import *


class GaugeWidget():
    def __init__(
        self,
        parent,
        width=200,
        height=100,
        arc_size=20,
        value=0,
        unit='',
        max_val=None,
        thresholds=None,
        fg='white',
        bg='black',
        fontsize=30,
        value_var=None
    ):
        self.parent = parent
        self.width = width
        self.height = height
        self.arc_size = arc_size
        self.value = value
        self.max = max_val
        self.unit = unit
        self.thresholds = thresholds
        self.fontsize = fontsize
        self.fontname = "Arial Bold"
        self.fg = fg
        self.bg = bg
        self.value_var = value_var

        self.canvas_arc = None

    def _on_val_changed(self):
        self.value = self.value_var.get()
        self._redraw_arc()
        self._redraw_text()

    def _redraw_arc(self):
        if not self.canvas_arc:
            return

        if self.max is None:
            return

        pr = self.value / self.max
        if self.value >= self.max:
            pr = 1.0
        pr_extent = 180 * pr

        self.canvas.itemconfigure(
            self.canvas_arc,
            extent=pr_extent,
            start=180-pr_extent,
            outline=self._get_color(),
        )

    def _get_text_params(self):
        _value = round(self.value, 2)
        _text = str(_value) + self.unit

        font = Font(font=(self.fontname, self.fontsize))
        measured_width = font.measure(_text)
        fit_text_width = self.width - self.arc_size * 3

        fontsize = self.fontsize
        if measured_width > fit_text_width:
            diff = fit_text_width / measured_width
            fontsize = int(fontsize * diff)

        return (
            _text,
            (self.fontname, fontsize),
        )

    def _redraw_text(self):
        text, font = self._get_text_params()
        self.canvas.itemconfigure(self.canvas_text, text=text, font=font, fill=self._get_color())

    def _get_color(self):
        outline_color = self.fg
        if self.max is not None and self.value > self.max:
            outline_color = 'red'

        if self.thresholds is not None:
            outline_color = self.thresholds.get('_', self.fg)
            for key in self.thresholds.keys():
                if key == '_':
                    continue
                if self.value >= float(key):
                    outline_color = self.thresholds[key]

        return outline_color

    def draw_arc(self):
        if self.max is None:
            return

        start = (0 + self.arc_size / 2, self.arc_size / 2)
        end = (self.width - self.arc_size / 2, self.height * 2 - self.arc_size / 2)

        self.canvas.create_arc(start, end, style=ARC, width=self.arc_size, extent=180, outline='grey')

        pr = self.value / self.max
        if self.value > self.max:
            pr = 1.0
        pr_extent = 180 * pr
        self.canvas_arc = self.canvas.create_arc(
            start,
            end,
            style=ARC,
            width=self.arc_size,
            extent=pr_extent,
            start=180 - pr_extent,
            outline=self._get_color()
        )

    def make(self):
        outline_color = self._get_color()
        frame = Frame(self.parent, pady=10, bg=self.bg)
        self.canvas = Canvas(
            frame,
            width=self.width,
            height=self.height,
            bg=self.bg,
            bd=0,
            highlightthickness=0,
            relief='ridge',
        )
        self.canvas.pack(anchor=CENTER, expand=True)

        if self.max is not None:
            self.draw_arc()

        text, font = self._get_text_params()

        text_x = self.width / 2
        text_y = self.height / 2

        if self.canvas_arc is not None:
            text_y = self.height / 2 + self.arc_size

        self.canvas_text = self.canvas.create_text(
            (text_x, text_y),
            fill=outline_color,
            text=text,
            font=font
        )

        if self.value_var:
            self.value_var.trace_variable(
                'w',
                lambda _, __, ___: self._on_val_changed()
            )

        return frame
