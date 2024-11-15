from PyQt5.QtCore import Qt

notebook_corner_style = """
	QTabWidget::right-corner
		{
			height: 50px;
			bottom: 10px;
		}
	"""

def parent_tab_widget(widget):
    while widget:
        if hasattr(widget,
                   "categories") and "tabwidget" in widget.categories():
            break
        widget = widget.parent()
    return widget
