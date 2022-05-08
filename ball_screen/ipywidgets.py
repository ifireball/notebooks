"""IPyWidgets-based implementation of a ball animation screen."""
from threading import Event, Thread

import ipywidgets as widgets  # type: ignore
from ipycanvas import Canvas, RoughCanvas, hold_canvas  # type: ignore

from .protocols import AnimationFunc, BallScreen


class _CanvasBallScreen(BallScreen):
    """Canvas based BallSceen implementation."""

    _width: int
    _height: int
    _canvas: Canvas
    _stop_event: Event

    def __init__(
        self, width: int, height: int, canvas: Canvas, stop_event: Event
    ) -> None:
        self._width = width
        self._height = height
        self._stop_event = stop_event
        self._canvas = canvas

    @property
    def screen_width(self) -> int:
        return self._width

    @property
    def screen_height(self) -> int:
        return self._height

    @property
    def should_stop(self) -> bool:
        return self._stop_event.is_set()

    def draw_ball(self, center_x: int, center_y: int, size: int) -> None:
        with hold_canvas():
            self._canvas.stroke_circle(center_x, center_y, size)
            self._canvas.fill_circle(center_x, center_y, size)

    def clear(self) -> None:
        self._canvas.clear()


def display_ball_animation(
    width: int, height: int, anim_func: AnimationFunc
) -> widgets.DOMWidget:
    """Return a widget that runs and displays the given animation."""
    thread = None
    stop_event = Event()
    start_btn = widgets.Button(icon="play", tooltip="start")
    stop_btn = widgets.Button(icon="stop", tooltip="stop")
    canvas = RoughCanvas(width=width, height=height)
    screen = _CanvasBallScreen(width, height, canvas, stop_event)

    def start_thread(*_):
        nonlocal thread
        print("Starting thread")
        thread = Thread(target=anim_func, kwargs={"screen": screen})
        thread.start()
        start_btn.disabled = True
        stop_btn.disabled = False

    def stop_thread(*_):
        nonlocal thread
        stop_event.set()
        thread.join()
        print("Thread stopped")
        thread = None
        stop_event.clear()
        start_btn.disabled = False
        stop_btn.disabled = True

    start_btn.on_click(start_thread)
    stop_btn.on_click(stop_thread)
    stop_btn.disabled = True

    return widgets.VBox([widgets.HBox([start_btn, stop_btn]), canvas])
