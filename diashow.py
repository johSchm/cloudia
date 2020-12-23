from PIL import Image, ImageTk
import tkinter as tk
import time
import _thread
from navigation import NavigationFrame
from image_processing import load_downscale_image


DIASHOW_WINDOW_WIDTH = 512
DIASHOW_WINDOW_HEIGHT = 512
NAV_HEIGHT = 150


class ImageFrame(tk.Frame):
    """ Frame displaying the image.
    """

    def __init__(self, root_frame, *args, **kwargs):
        super().__init__(root_frame, *args, **kwargs)
        self.img = None
        self.pack()

    def update_image(self, img_path: str):
        size = (DIASHOW_WINDOW_WIDTH, DIASHOW_WINDOW_HEIGHT - NAV_HEIGHT)
        img = load_downscale_image(img_path, size)
        render = ImageTk.PhotoImage(img)
        if not self.img:
            self.img = tk.Label(self, image=render)
        self.img.configure(image=render)
        self.img.image = render
        self.img.place(x=0, y=0)
        self.img.pack(fill=tk.BOTH)


class Diashow:
    """ Diashow.
    Tkinker-based image diashow.
    Navigation arrows are there to switch images.
    """

    def __init__(self,
                 image_list: list,
                 initial_image_idx=0,
                 window_width=DIASHOW_WINDOW_WIDTH,
                 window_height=DIASHOW_WINDOW_HEIGHT,
                 *args, **kwargs):
        """ Init.
        :param window_width: the width of the window in pixel
        :param window_height: the height of the window in pixel
        """
        self.current_image_idx = initial_image_idx
        self.root = tk.Toplevel()
        self.image_list = image_list
        self.image_frame = ImageFrame(self.root,
                                      # bg='blue',
                                      width=DIASHOW_WINDOW_WIDTH)
        nav_pos = ((10, 10), (DIASHOW_WINDOW_WIDTH - 50, 10))
        self.nav_frame = NavigationFrame(self.root,
                                         # bg='green',
                                         positions=nav_pos)
        self.width = window_width
        self.height = window_height
        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()
        self.x_left = int((self.screen_width / 2) - (self.width / 2))
        self.y_top = int((self.screen_height / 2) - (self.height / 2))

        self.root.geometry(str(self.width) + "x" + str(self.height) + "+" + str(self.x_left) + "+" + str(self.y_top))
        self.root.title("Diashow")
        self.display(self.current_image_idx)
        self.image_frame.pack(fill=tk.BOTH, side=tk.TOP, expand=True)
        self.nav_frame.pack(fill=tk.BOTH, side=tk.BOTTOM, expand=True)
        self._create_event_listeners()
        self.root.mainloop()

    def display(self, idx=0):
        if idx < 0:
            idx = len(self.image_list) - 1
        elif idx >= len(self.image_list):
            idx = 0
        self.current_image_idx = idx
        img_path = self.image_list[idx]
        self.image_frame.update_image(img_path)

    def _nav_event_handler(self, thread_name, delay=0.01):
        while True:
            time.sleep(delay)
            if self.nav_frame.nav_left_click_event:
                self.display(self.current_image_idx - 1)
                self.nav_frame.nav_left_click_event = False
            elif self.nav_frame.nav_right_click_event:
                self.display(self.current_image_idx + 1)
                self.nav_frame.nav_right_click_event = False

    def _create_event_listeners(self):
        _thread.start_new_thread(self._nav_event_handler,
                                 ("Thread-Diashow-Navigation-Event-Listener",
                                  2, ))
