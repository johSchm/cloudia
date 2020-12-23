from enum import Enum


class MouseEvents(Enum):
    RIGHT = 0
    LEFT = 1
    MIDDLE = 2


def mouse_click_identifier(event):
    """ event also has x & y attributes
    """
    if event.num == 1:
        return MouseEvents.LEFT
    elif event.num == 2:
        return MouseEvents.RIGHT
    else:
        return MouseEvents.MIDDLE
