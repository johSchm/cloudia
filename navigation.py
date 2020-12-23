from utils import mouse_click_identifier, MouseEvents
import tkinter as tk


class NavigationFrame(tk.Frame):
    """ This frame is responsible for holding the navigation objects.
    """

    def __init__(self,
                 root_frame,
                 text='...',
                 positions=((10, 10), (100, 10)),
                 *args, **kwargs):
        super().__init__(root_frame, *args, **kwargs)
        self.nav_left_image = tk.PhotoImage(file="icons/arrow_left.png")
        self.nav_right_image = tk.PhotoImage(file="icons/arrow_right.png")
        self.nav_left_button = tk.Button(self, image=self.nav_left_image)
        self.nav_right_button = tk.Button(self, image=self.nav_right_image)
        self.text_widget = tk.Label(self, text=text,
                                    font=('Arial bold', 16))
        self.text_widget.pack(side=tk.TOP)
        # self.nav_left_button.place(x=positions[0][0], y=positions[0][1])
        # self.nav_right_button.place(x=positions[1][0], y=positions[1][1])
        self.nav_left_button.pack(side=tk.LEFT)
        self.nav_right_button.pack(side=tk.RIGHT)
        self.nav_left_button.bind("<Button-1>", self._click_handler_btn_left)
        self.nav_right_button.bind("<Button-1>", self._click_handler_btn_right)
        self.nav_left_click_event = False
        self.nav_right_click_event = False

    def update_text(self, text: str):
        self.text_widget.config(text=text)
        self.text_widget.update()

    def _click_handler_btn_left(self, event):
        """ Note that binding <Button-1> means listening to left button clicks.
        We have one listener for each arrow (left, right).
        But both allow only interactions with left mouse clicks.
        That's why MouseEvents.LEFT and <Button-1> is used.
        """
        if mouse_click_identifier(event) == MouseEvents.LEFT:
            self.nav_left_click_event = True

    def _click_handler_btn_right(self, event):
        """ Note that binding <Button-1> means listening to left button clicks.
        We have one listener for each arrow (left, right).
        But both allow only interactions with left mouse clicks.
        That's why MouseEvents.LEFT and <Button-1> is used.
        """
        if mouse_click_identifier(event) == MouseEvents.LEFT:
            self.nav_right_click_event = True
