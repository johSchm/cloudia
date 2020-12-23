import tkinter as tk
from tkinter import ttk


PROGRESS_WINDOW_WIDTH = 256
PROGRESS_WINDOW_HEIGHT = 64


class ProgressFrame(tk.Frame):
    """ frame with a progress bar for updates.
    """

    def __init__(self, root_frame, *args, **kwargs):
        super().__init__(root_frame, *args, **kwargs)

        self.bar = ttk.Progressbar(self,
                                   orient=tk.HORIZONTAL,
                                   length=100,
                                   mode='determinate')
        self.bar.pack(fill='both')

    def update(self, percentage=0.1):
        self.bar['value'] = percentage * 100
        self.update_idletasks()
        if percentage >= 1.0:
            self.update(0.0)
