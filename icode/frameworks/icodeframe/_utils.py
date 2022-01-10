import sys
from os.path import join, dirname, abspath
import PyQt5.QtCore 
import platform

QT_VERSION = tuple(int(v) for v in PyQt5.QtCore.PYQT_VERSION_STR.split('.'))
""" tuple: Qt version. """

PLATFORM = platform.system()

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return join(sys._MEIPASS, dirname(abspath(__file__)), relative_path)
    return join(dirname(abspath(__file__)), relative_path)

_FL_STYLESHEET = """
#windowFrame {
  background-color: palette(Window);
}

#lblTitle{
  margin: 0px 4px 4px 4px;
}

#btnClose, #btnRestore, #btnMaximize, #btnMinimize {
  min-width: 14px;
  min-height: 14px;
  max-width: 14px;
  max-height: 14px;
  border-radius: 7px;
  margin: 0px 4px 4px 4px;
}

#btnRestore, #btnMaximize {
  background-color: hsv(123, 204, 198);
}

#btnRestore::hover, #btnMaximize::hover {
  background-color: hsv(123, 204, 148);
}

#btnRestore::pressed, #btnMaximize::pressed {
  background-color: hsv(123, 204, 98);
}

#btnMinimize {
  background-color: hsv(38, 218, 253);
}

#btnMinimize::hover {
  background-color: hsv(38, 218, 203);
}

#btnMinimize::pressed {
  background-color: hsv(38, 218, 153);
}

#btnClose {
  background-color: hsv(0, 182, 252);
}

#btnClose::hover {
  background-color: hsv(0, 182, 202);
}

#btnClose::pressed {
  background-color: hsv(0, 182, 152);
}

#btnClose::disabled, #btnRestore::disabled, #btnMaximize::disabled, #btnMinimize::disabled {
  background-color: palette(midlight);
}

#btnMenu{
  margin: 4px 4px 4px 4px;
}
#btnMenu::menu-indicator
{
    image:none;
} 
"""