import tkinter as tk
import _thread
import time
from networking import RemoteNavigator
from navigation import NavigationFrame
from PIL import Image, ImageTk
from progress import ProgressFrame
from image_processing import load_downscale_image
from diashow import Diashow
import math
import os


WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
IP = '192.168.178.39'  # '192.168.178.68'  # '192.168.0.14'
CACHE_PATH = 'tmp'
CHUNK_SIZE = 16
PATH_START_POINT = '//mnt/HD/HD_a2/Public/Backup'
NAVIGATION_FRAME_HEIGHT = 100


class FolderTreeFrame(tk.Frame):
    """ This frame is responsible for holding the folder tree.
    """

    def __init__(self, root_frame, *args, **kwargs):
        super().__init__(root_frame, *args, **kwargs)
        self.folder_image = tk.PhotoImage(file="icons/folder.png")
        self.folder_names = None
        self.folder_buttons = None
        self.listbox = tk.Listbox(self, selectmode=tk.SINGLE)
        self.scrollbar = tk.Scrollbar(self, orient='vertical')
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y, expand=True)
        self.listbox.config(yscrollcommand=self.scrollbar.set)
        self.scrollbar.config(command=self.listbox.yview)
        self.listbox.bind('<<ListboxSelect>>', self._click_handler_folder)
        self.listbox.pack(side=tk.LEFT, fill=tk.Y, expand=True)
        self.selected_folder = None

    def _click_handler_folder(self, event):
        item_id = event.widget.curselection()
        if len(item_id) > 0:
            item_name = self.listbox.get(item_id[0])
            self.selected_folder = item_name

    def update_folders(self, names: list):
        if self.listbox.size() != 0:
            self.listbox.delete(0, self.listbox.size())
        for name in names:
            self.listbox.insert(tk.END, name)


class FolderManagerFrame(tk.Frame):
    """ Main folder manager frame.
    """

    def __init__(self, root_frame, controller=None, *args, **kwargs):
        super().__init__(root_frame, *args, **kwargs)
        self.controller = controller
        self.file_list = None
        nav_frame_text = os.path.basename(os.path.normpath(PATH_START_POINT))
        self.nav_frame = NavigationFrame(self,
                                         # bg='blue',
                                         text=nav_frame_text,
                                         width=WINDOW_WIDTH / 2,
                                         height=NAVIGATION_FRAME_HEIGHT)
        self.tree_frame = FolderTreeFrame(self,
                                          # bg='green',
                                          width=WINDOW_WIDTH / 2,
                                          height=WINDOW_HEIGHT - NAVIGATION_FRAME_HEIGHT)
        self.nav_frame.pack(side=tk.TOP)
        self.tree_frame.pack(side=tk.BOTTOM)
        self.nav_frame.pack_propagate(0)
        self.tree_frame.pack_propagate(0)
        self.tree_frame.update_folders(self._get_folder_names())
        self._create_event_listeners()
        self.update_id = 0

    def _update_id(self):
        self.update_id = 0 if self.update_id > 64 else self.update_id + 1
        print('Updating tracking ID to {}.'.format(self.update_id))

    def _nav_event_handler(self, thread_name, delay=0.01):
        while True:
            time.sleep(delay)
            if self.nav_frame.nav_left_click_event:
                print('going back')
                folders = self._get_folder_names('..')
                self.file_list = self._get_file_names()
                self.tree_frame.update_folders(folders)
                self.nav_frame.nav_left_click_event = False
                self._update_id()
            elif self.nav_frame.nav_right_click_event:
                self.nav_frame.nav_right_click_event = False
                self._update_id()

    def _folder_event_handler(self, thread_name, delay=0.01):
        while True:
            time.sleep(delay)
            if self.tree_frame.selected_folder is not None:
                folder_name = self.tree_frame.selected_folder
                folders = self._get_folder_names(folder_name)
                self.file_list = self._get_file_names()
                self.tree_frame.update_folders(folders)
                self.tree_frame.selected_folder = None
                self._update_id()

    def _get_folder_names(self, target=None) -> list:
        """ Getter for the remote folder names.
        :param target: the parent directory
        :return list of folder names.
        """
        if self.controller:
            if target:
                directory = self.controller.goto(target)
                directory = os.path.basename(os.path.normpath((directory[0])))
                self.nav_frame.update_text(directory)
            return self.controller.list(include_files=False)
        return []

    def _get_file_names(self, target=None) -> list:
        """ Getter for the remote file names.
        :param target: the parent directory
        :return list of file names.
        """
        if self.controller:
            if target:
                self.controller.goto(target)
            return self.controller.chunk(CHUNK_SIZE)
        return []

    def _create_event_listeners(self):
        _thread.start_new_thread(self._nav_event_handler, ("Thread-Navigation-Event-Listener", 2, ))
        _thread.start_new_thread(self._folder_event_handler, ("Thread-Folder-Event-Listener", 2, ))


class FileGridFrame(tk.Frame):
    """ Main file grid frame.
    """

    def __init__(self, root_frame, *args, **kwargs):
        super().__init__(root_frame, *args, **kwargs)
        self.preview_width = 64
        self.preview_height = 64
        self.n_fig_per_row = math.floor((WINDOW_WIDTH / 2) / self.preview_width)
        self.loading_lock = False
        self.image_paths = None

    def delete(self):
        for label in self.grid_slaves():
            label.grid_forget()

    def load(self, img_paths: list):
        self.loading_lock = True
        self.image_paths = img_paths
        n_rows = math.floor(len(img_paths) / self.n_fig_per_row) + 1
        for r in range(n_rows):
            for c in range(self.n_fig_per_row):
                if c + c * r >= len(img_paths):
                    self.loading_lock = False
                    return
                img = load_downscale_image(img_paths[c + c * r],
                                           (self.preview_width, self.preview_height))
                render = ImageTk.PhotoImage(img)
                element = tk.Label(self, image=render)
                element.grid(row=r+1, column=c+1)
                element.bind("<Double-Button-1>", lambda event, r=r, c=c: self._btn_event_handler(r, c))
                element.image = render
        self.loading_lock = False

    def _btn_event_handler(self, r, c):
        print('Opening image ({0},{1}).'.format(r, c))
        Diashow(self.image_paths, initial_image_idx=c + c * r)


class FileManagerFrame(tk.Frame):
    """ Main file manager frame.
    """

    def __init__(self, root_frame, *args, **kwargs):
        super().__init__(root_frame, *args, **kwargs)
        self.nav_frame = NavigationFrame(self,
                                         # bg='red',
                                         width=WINDOW_WIDTH / 2,
                                         height=NAVIGATION_FRAME_HEIGHT)
        self.grid_frame = FileGridFrame(self,
                                        # bg='yellow',
                                        width=WINDOW_WIDTH / 2,
                                        height=WINDOW_HEIGHT - NAVIGATION_FRAME_HEIGHT)
        self.process_frame = ProgressFrame(self,
                                           # bg='blue',
                                           width=WINDOW_WIDTH / 2,
                                           height=NAVIGATION_FRAME_HEIGHT / 2)
        self.nav_frame.pack(side=tk.TOP)
        self.process_frame.pack(side=tk.TOP)
        self.grid_frame.pack(side=tk.TOP)
        self.nav_frame.pack_propagate(0)
        self.grid_frame.pack_propagate(0)
        self.process_frame.pack_propagate(0)
        self._create_event_listeners()
        self.chunk_idx = 0

    def _create_event_listeners(self):
        _thread.start_new_thread(self._update_grid,
                                 ("Thread-File-Grid-Navigation-Listener", 2, ))

    def _update_grid(self, thread_name, delay=0.01):
        while True:
            time.sleep(delay)
            if self.nav_frame.nav_left_click_event:
                print('File Manager Navigation Click Event (Left).')
                self.chunk_idx = 0 if self.chunk_idx <= 0 else self.chunk_idx - 1
                self.nav_frame.nav_left_click_event = False
            elif self.nav_frame.nav_right_click_event:
                print('File Manager Navigation Click Event (Right).')
                self.chunk_idx += 1
                self.nav_frame.nav_right_click_event = False


class Application:
    """ The main application class.
    """

    def __init__(self,
                 window_width=WINDOW_WIDTH,
                 window_height=WINDOW_HEIGHT,
                 ip=IP):
        """ Init.
        :param window_width: the width of the window in pixel
        :param window_height: the height of the window in pixel
        """
        self.remote_controller = RemoteNavigator(ip, CACHE_PATH)
        self.remote_controller.connect()
        self.remote_controller.goto(PATH_START_POINT)

        self.root = tk.Tk()
        self.width = window_width
        self.height = window_height
        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()
        self.x_left = int((self.screen_width / 2) - (self.width / 2))
        self.y_top = int((self.screen_height / 2) - (self.height / 2))

        self.root.geometry(str(self.width) + "x" + str(self.height) + "+" + str(self.x_left) + "+" + str(self.y_top))
        self.root.title("Cloud File Manager")

        self.folder_manager_frame = FolderManagerFrame(self.root,
                                                       # bg='blue',
                                                       controller=self.remote_controller,
                                                       width=WINDOW_WIDTH / 2,
                                                       height=WINDOW_HEIGHT)
        self.file_manager_frame = FileManagerFrame(self.root,
                                                   # bg='red',
                                                   width=WINDOW_WIDTH / 2,
                                                   height=WINDOW_HEIGHT)
        self.update_tracking_id = self.folder_manager_frame.update_id

        self.folder_manager_frame.pack(side=tk.LEFT)
        self.file_manager_frame.pack(side=tk.RIGHT)
        self.folder_manager_frame.pack_propagate(0)
        self.file_manager_frame.pack_propagate(0)
        # self.folder_manager_frame.grid(row=0, column=0, padx=(10, 10))
        # self.file_manager_frame.grid(row=0, column=1, padx=(10, 10))

        self._create_event_listeners()
        self.root.mainloop()

    def _create_event_listeners(self):
        _thread.start_new_thread(self._file_list_handler, ("Thread-File-List-Listener", 2, ))

    def _file_list_handler(self, thread_name, delay=0.01):
        previous_chunk = -1
        update = False
        while True:
            time.sleep(delay)
            if self.folder_manager_frame.file_list is not None \
                    and not self.file_manager_frame.grid_frame.loading_lock:
                if len(self.folder_manager_frame.file_list) <= 0:
                    chunk_text = '{0}/{1}'.format(0, 0)
                    self.file_manager_frame.nav_frame.update_text(chunk_text)
                    self.file_manager_frame.grid_frame.delete()
                    continue
                chunk_idx = self.file_manager_frame.chunk_idx
                if self.update_tracking_id != self.folder_manager_frame.update_id:
                    self.update_tracking_id = self.folder_manager_frame.update_id
                    update = True
                    chunk_idx = 0
                elif chunk_idx >= len(self.folder_manager_frame.file_list):
                    chunk_idx = len(self.folder_manager_frame.file_list) - 1
                if chunk_idx != previous_chunk or update:
                    print('Loading chunk {}'.format(chunk_idx))
                    chunk_text = '{0}/{1}'.format(chunk_idx, len(self.folder_manager_frame.file_list))
                    self.file_manager_frame.nav_frame.update_text(chunk_text)
                    self.file_manager_frame.grid_frame.delete()
                    self.remote_controller.update_file_list(self.folder_manager_frame.file_list,
                                                            idx=chunk_idx)
                    self.file_manager_frame.process_frame.update(0.2)
                    self.remote_controller.download(use_file_list=True)
                    self.file_manager_frame.process_frame.update(0.6)
                    img_paths = os.listdir(CACHE_PATH)
                    img_paths = ['tmp/' + i for i in img_paths]
                    self.file_manager_frame.grid_frame.load(img_paths)
                    self.file_manager_frame.process_frame.update(1.0)
                    previous_chunk = chunk_idx
                update = False


if __name__ == "__main__":
    app = Application()
