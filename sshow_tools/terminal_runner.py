import os
from selectors import EVENT_READ, DefaultSelector
from subprocess import DEVNULL, PIPE, Popen
from threading import Thread
from typing import Any

import panel
import panel.pane
import panel.viewable
import panel.widgets


class TerminalRunner(panel.viewable.Viewer):
    """Show a panel-based terminal and controls for running the given command in the background

    Need to run the following for this to work in a notebook:

        panel.extension('terminal', 'gridstack')

    """
    PLAY_LABEL = "▶"
    STOP_LABEL = "⏹"

    def __init__(self, args: str):
        self._terminal = panel.widgets.Terminal(
            options={"cursorBlink": True},
            sizing_mode='scale_both',
            width=160,
            height=70,
            margin=(5, 10, 0, 10),
        )
        self._process: Popen[Any] | None = None
        self._thread: Thread | None = None
        self._args = args

        self._run_btn = panel.widgets.Button(
            name=self.PLAY_LABEL,
            width=30,
            height=30,
            sizing_mode="fixed",
            margin=(5, 10, 5, 5),
        )
        self._run_btn.on_click(self._on_btn_click)
        self._panel = panel.Column(
            panel.Row(
                panel.pane.Markdown(
                    f"```bash\n{args}\n```",
                    sizing_mode="stretch_both",
                    margin=10,
                ),
                self._run_btn,
                sizing_mode="stretch_width",
                background="#f8f8f8",
                # style={"border": "1px solid #f0f0f0"},
                margin=(0, 25, 0, 10),
            ),
            self._terminal,
            width=160,
            height=80,
            sizing_mode="scale_both"
        )

    def _on_btn_click(self, event: Any) -> None:
        if self._thread:
            if self._process:
                self._process.terminate()
        else:
            self._thread = Thread(target=self._stream_proc_to_output)
            self._thread.start()

    def __panel__(self) -> panel.Column:
        return self._panel

    def _stream_proc_to_output(self) -> None:
        try:
            with Popen(
                self._args,
                shell=True,
                stdin=DEVNULL,
                stdout=PIPE,
                stderr=PIPE,
                close_fds=True,
                bufsize=0,
                universal_newlines=True,
            ) as self._process:
                self._run_btn.name = self.STOP_LABEL
                self._terminal.clear()
                with DefaultSelector() as selector:
                    if self._process.stdout:
                        selector.register(self._process.stdout, EVENT_READ)
                    if self._process.stderr:
                        selector.register(self._process.stderr, EVENT_READ)
                    while selector.get_map():
                        ready = selector.select()
                        for key, _events in ready:
                            buf = os.read(key.fd, 10)
                            if buf:
                                self._terminal.write(buf.decode())
                            else:
                                selector.unregister(key.fileobj)
                                if hasattr(key.fileobj, "close"):
                                    key.fileobj.close()
        finally:
            self._terminal.write("\033[31;1mTerminated\033[0m\n")
            self._process = None
            self._thread = None
            self._run_btn.name = self.PLAY_LABEL
