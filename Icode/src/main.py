from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
import sys
from core.server import Server

def run(args=None, call_out=None) -> None:
    qapp = QApplication(sys.argv)
    qapp.setDesktopFileName("Icode")
    qapp.setApplicationVersion("0.0.1")
    qapp.setApplicationName("Intelligent Code")
    qapp.setDesktopSettingsAware(False)
    
    #exe = MainWindow(None, styler.windows_style, qapp)
    #app = App(exe, qapp)
    #settings.restore_window(exe, app, getfn)
    #if call_out is not None:
        #qapp.lastWindowClosed.connect(call_out)
    #exe.show_()
    #sys.exit(qapp.exec())


if __name__ == "__main__":
    run()
