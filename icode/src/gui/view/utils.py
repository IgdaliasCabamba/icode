from PyQt5.QtCore import Qt

notebook_corner_style = """
	QTabWidget::right-corner
		{
			height: 50px;
			bottom: 10px;
		}
	"""


class consts:
    UP = 0

    DOWN = 1

    LEFT = 2

    RIGHT = 3

    ORIENTATIONS = {
        UP: Qt.Vertical,
        DOWN: Qt.Vertical,
        LEFT: Qt.Horizontal,
        RIGHT: Qt.Horizontal,
    }

    MOVES = {UP: -1, DOWN: 1, LEFT: -1, RIGHT: 1}


def parent_tab_widget(widget):
    while widget:
        if hasattr(widget,
                   "categories") and "tabwidget" in widget.categories():
            break
        widget = widget.parent()
    return widget
