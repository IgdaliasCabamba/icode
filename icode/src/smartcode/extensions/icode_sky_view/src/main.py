from extension_api import *


class Init(ModelApp):

    def __init__(self, data) -> None:
        super().__init__(data, "icode_sky_view")
        self._db = CacheManager(self.local_storage_to("cache", "data.idt"))

        self.menu = QMenu("Sky View")
        self.action_manager = QActionGroup(self)

        self.opt_auto = QAction("Auto")
        self.opt_auto.setObjectName("auto")
        self.opt_auto.setCheckable(True)
        self.opt_auto.setChecked(True)

        self.opt_show = QAction("Show")
        self.opt_show.setObjectName("show")
        self.opt_show.setCheckable(True)
        self.opt_show.setChecked(False)

        self.opt_hide = QAction("Hide")
        self.opt_hide.setObjectName("hide")
        self.opt_hide.setCheckable(True)
        self.opt_hide.setChecked(False)

        self.action_manager.addAction(self.opt_auto)
        self.action_manager.addAction(self.opt_show)
        self.action_manager.addAction(self.opt_hide)
        self.menu.addAction(self.opt_auto)
        self.menu.addAction(self.opt_show)
        self.menu.addAction(self.opt_hide)
        self.ui.menu_bar.tools.addMenu(self.menu)

        self.load_settings()

        self.do_on(self.change_status, "action_manager", "triggered")

    def change_status(self, action):
        if action.objectName() == "auto":
            self.auto_tab_bars()

        elif action.objectName() == "show":
            self.show_tab_bars()

        elif action.objectName() == "hide":
            self.hide_tab_bars()

        self.save_settings()

    def show_tab_bars(self):
        for notebook in self.ui.notebooks:
            notebook.tabBar().show()

    def hide_tab_bars(self):
        for notebook in self.ui.notebooks:
            notebook.tabBar().hide()

    def auto_tab_bars(self):
        if self.opt_auto.isChecked():
            self.enable()
        else:
            self.disable()

    def enable(self):
        for notebook in self.ui.notebooks:
            notebook.setTabBarAutoHide(True)

    def disable(self):
        for notebook in self.ui.notebooks:
            notebook.setTabBarAutoHide(False)

    def load_settings(self):
        auto = getfn.get_bool_from_str(self._db.value("auto"))
        show = getfn.get_bool_from_str(self._db.value("show"))
        hide = getfn.get_bool_from_str(self._db.value("hide"))

        if isinstance(auto, bool):
            self.opt_auto.setChecked(auto)
            if auto:
                self.enable()
            else:
                self.disable()

        if isinstance(show, bool):
            self.opt_show.setChecked(show)
            if show:
                self.show_tab_bars()

        if isinstance(hide, bool):
            self.opt_hide.setChecked(hide)
            if hide:
                self.hide_tab_bars()

    def save_settings(self):
        self._db.setValue("auto", self.opt_auto.isChecked())
        self._db.setValue("show", self.opt_show.isChecked())
        self._db.setValue("hide", self.opt_hide.isChecked())
