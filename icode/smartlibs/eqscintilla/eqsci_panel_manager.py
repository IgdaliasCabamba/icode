from typing import Dict, List, Optional, Union, Iterator
from PyQt5.QtCore import QRect, QSize, QPoint, QObject
from PyQt5.Qsci import QsciScintilla
from qtpy.QtCore import QRect, QSize
from .eqsci_panel import Panel, PanelPosition, PanelSettings, ZoneSizes


class _BasePanelManager(QObject):

    def __init__(self, editor) -> None:
        super().__init__(editor)

        self._cached_cursor_pos: QPoint = (-1, -1)
        self._margin_sizes: tuple = (0, 0, 0, 0)
        self._top: int = -1
        self._left: int = -1
        self._right: int = -1
        self._bottom: int = -1
        self._panels: Dict[PanelPosition, Dict[str, Panel]] = {
            pos: {} for pos in PanelPosition.all_positions()
        }
        self._zones: list = self._panels.keys()

    def keys(self) -> list:
        return self._panels.keys()

    def values(self) -> list:
        return self._panels.values()

    def __iter__(self) -> Iterator:
        lst = []
        for zone, zone_dict in self._panels.items():
            for name, panel in zone_dict.items():
                lst.append(panel)
        return iter(lst)

    def __len__(self) -> int:
        lst = []
        for zone, zone_dict in self._panels.items():
            for name, panel in zone_dict.items():
                lst.append(panel)
        return len(lst)

    def panels_located_at_zone(self, zone: PanelPosition) -> list:
        panels_at_zone: dict = self._panels[zone]
        return list(panels_at_zone.values())

    def zone_where_panel_is_located(
            self, panel: Union[Panel, str]
            ) -> Union[PanelPosition, None]:
        if isinstance(panel, Panel):
            panel = panel.__name__

        for zone in self._zones:
            if panel in self._panels[zone]:
                return zone

        return None
        

    def _valid_panels_at(self, zone: PanelPosition, reverse: bool = False) -> list:
        panels = self.panels_located_at_zone(zone)
        panels.sort(key=lambda panel: panel.settings.order, reverse=reverse)
        for panel in panels:
            if not panel.isVisible():
                panels.remove(panel)
        return panels

    def _compute_zone_size(self, zone: PanelPosition) -> int:
        res: int = 0
        for panel in self.panels_located_at_zone(zone):
            if panel.isVisible():
                size_hint = panel.size()
                res += size_hint.width()
        return res

    def _viewport_margin(self, zone: PanelPosition) -> int:
        res: int = 0
        for panel in self.panels_located_at_zone(zone):
            if panel.isVisible():
                if zone == PanelPosition.LEFT or zone == PanelPosition.RIGHT:
                    res += panel.size().width()

                elif zone == PanelPosition.TOP or zone == PanelPosition.BOTTOM:
                    res += panel.size().height()
        return res

    @property
    def zones_sizes(self) -> ZoneSizes:
        """Compute panel zone sizes"""

        self._left = self._compute_zone_size(PanelPosition.LEFT)

        self._right = self._compute_zone_size(PanelPosition.RIGHT)

        self._top = self._compute_zone_size(PanelPosition.TOP)

        self._bottom = self._compute_zone_size(PanelPosition.BOTTOM)

        return ZoneSizes(
            left=self._left, right=self._right, top=self._top, bottom=self._bottom
        )

    def margin_size(self, zone=PanelPosition.LEFT) -> float:
        return self._margin_sizes[zone]


class _PanelsSizeHelpers(_BasePanelManager):
    def __init__(self, editor) -> None:
        super().__init__(editor)

    def resize_left(
        self,
        contents_rect: QRect,
        zone_sizes: ZoneSizes,
        heigth_offset: int,
    ) -> int:
        left_size = 0
        for panel in self._valid_panels_at(PanelPosition.LEFT, True):
            panel.adjustSize()
            size_hint: QSize = panel.size()

            x = contents_rect.left() + left_size
            y = contents_rect.top() + zone_sizes.top
            w = size_hint.width()
            h = (
                contents_rect.height()
                - zone_sizes.bottom
                - zone_sizes.top
                - heigth_offset
            )

            level = panel.settings.level

            if level == 1:
                h = contents_rect.height() - zone_sizes.top - heigth_offset

            elif level == 2:
                h = contents_rect.height() - heigth_offset

            panel.setGeometry(x, y, w, h)
            left_size += size_hint.width()

        return left_size

    def resize_right(
        self,
        contents_rect: QRect,
        zone_sizes: ZoneSizes,
        width_offset: int,
        heigth_offset: int,
    ) -> int:
        rigth_size = 0
        for panel in self._valid_panels_at(PanelPosition.RIGHT, True):
            panel.adjustSize()
            size_hint: QSize = panel.size()

            x = contents_rect.right() - rigth_size - size_hint.width() - width_offset
            y = contents_rect.top() + zone_sizes.top
            w = size_hint.width()
            h = (
                contents_rect.height()
                - zone_sizes.bottom
                - zone_sizes.top
                - heigth_offset
            )

            level = panel.settings.level

            if level == 1:
                h = contents_rect.height() - zone_sizes.top - heigth_offset

            elif level == 2:
                h = contents_rect.height() - heigth_offset

            panel.setGeometry(x, y, w, h)

            rigth_size += size_hint.width()

        return rigth_size

    def resize_top(
        self,
        contents_rect: QRect,
        width_offset: int,
        right_size: int,
    ) -> int:
        top_size = 0
        for panel in self._valid_panels_at(PanelPosition.TOP):
            panel.adjustSize()
            size_hint: QSize = panel.size()

            level = panel.settings.level

            x = contents_rect.left()
            y = contents_rect.top() + top_size
            w = contents_rect.width() - width_offset - right_size
            h = size_hint.height()

            if level == 1:
                w = contents_rect.width() - width_offset

            elif level == 2:
                w = contents_rect.width()

            panel.setGeometry(x, y, w, h)
            top_size += size_hint.height()

        return top_size

    def resize_bottom(
        self,
        contents_rect: QRect,
        width_offset: int,
        heigth_offset: int,
        right_size: int,
    ) -> int:
        bottom_size = 0
        for panel in self._valid_panels_at(PanelPosition.BOTTOM):
            panel.adjustSize()
            size_hint: QSize = panel.size()

            x = contents_rect.left()
            y = (
                contents_rect.bottom()
                - bottom_size
                - size_hint.height()
                - heigth_offset
            )
            w = contents_rect.width() - width_offset - right_size
            h = size_hint.height()

            level = panel.settings.level

            if level == 1:
                w = contents_rect.width() - width_offset

            elif level == 2:
                w = contents_rect.width()

            panel.setGeometry(x, y, w, h)
            bottom_size += size_hint.height()

        return bottom_size

    def resize_panels(self) -> None:
        contents_rect = self.editor.contentsRect()
        view_contents_rect = self.editor.viewport().contentsRect()
        zones_sizes = self.zones_sizes

        total_width = zones_sizes.left + zones_sizes.right
        total_height = zones_sizes.bottom + zones_sizes.top
        width_offset = contents_rect.width() - (
            view_contents_rect.width() + total_width
        )
        heigth_offset = contents_rect.height() - (
            view_contents_rect.height() + total_height
        )

        left_size = self.resize_left(contents_rect, zones_sizes, heigth_offset)
        right_size = self.resize_right(
            contents_rect, zones_sizes, width_offset, heigth_offset
        )
        top_size = self.resize_top(contents_rect, width_offset, right_size)
        bottom_size = self.resize_bottom(
            contents_rect, width_offset, heigth_offset, right_size
        )


class EQsciPanelManager(_PanelsSizeHelpers):
    """Panel manager for QscintillaEditor"""

    def __init__(self, editor: QsciScintilla):
        super().__init__(editor)
        self.editor = editor

        self.editor.linesChanged.connect(self.update_viewport_margins)
        self.editor.SCN_UPDATEUI.connect(self._handle_update)
        self.editor.SCN_PAINTED.connect(self._handle_update)

        self.editor.viewport().installEventFilter(self)

    def _call_panel(self, panel: Panel) -> Union[None, Panel]:
        if callable(panel):
            # avoid appending more than one of the same panel type
            if self.get(panel.__name__):
                return None
            panel = panel(self.editor)
        else:
            # avoid appending more than one of the same panel type
            if self.get(panel.__class__.__name__):
                return None
            panel = panel
        return panel

    def append(
        self, panel: Panel, zone: PanelPosition = PanelPosition.LEFT, allow_duplicates: Optional[bool] = False
    ) -> Panel:
        
        if not allow_duplicates:
            panel = self._call_panel(panel)

        if panel:
            panel_name = panel.__class__.__name__
            self._panels[zone][panel_name] = panel
            self.refresh()
            return panel

        # make it like a singleton
        if callable(panel):
            return self.get(panel.__name__)

        return self.get(panel.__class__.__name__)

    def remove(self, panel: Panel) -> None:
        if not isinstance(panel, str):
            panel_name = panel.__name__

        for zone in PanelPosition.all_positions():
            if panel_name in self._panels[zone]:
                panel = self._panels[zone][panel_name]
                panel.setParent(None)
                del self._panels[zone][panel_name]
                break

    def get(self, panel_name: Union[Panel, str]) -> Optional[Panel]:
        if isinstance(panel_name, Panel):
            panel_name = panel_name.__name__

        for zone in PanelPosition.all_positions():
            if panel_name in self._panels[zone]:
                return self._panels[zone][panel_name]

    def refresh(self) -> None:
        self.resize_panels()
        self._handle_update(self.editor.contentsRect(),
                            0, force_update_margins=True)

    def _handle_update(
        self, rect: object = None, delta_y: int = 0, force_update_margins: bool = True
    ) -> None:

        if not rect:
            rect = self.editor.contentsRect()

        if isinstance(rect, int):
            delta_y = rect
            rect = self.editor.contentsRect()

        for zone_id, zone in self._panels.items():
            if zone_id == PanelPosition.TOP or zone_id == PanelPosition.BOTTOM:
                continue

            panels = list(zone.values())
            for panel in panels:
                if panel.settings.scrollable and delta_y:
                    panel.scroll(0, delta_y)

                line, col = self.editor.getCursorPosition()
                cached_line, cached_column = self._cached_cursor_pos

                if line != cached_line or col != cached_column or panel.settings.scrollable:
                    panel.update(0, rect.y(), panel.width(), rect.height())
                self._cached_cursor_pos = self.editor.getCursorPosition()

        if rect.contains(self.editor.viewport().rect()) or force_update_margins:
            self.update_viewport_margins()

        self.resize_panels()

    def update_viewport_margins(self) -> None:
        top = self._viewport_margin(PanelPosition.TOP)
        left = self._viewport_margin(PanelPosition.LEFT)
        right = self._viewport_margin(PanelPosition.RIGHT)
        bottom = self._viewport_margin(PanelPosition.BOTTOM)

        self._margin_sizes = (top, left, right, bottom)
        self.editor.setViewportMargins(left, top, right, bottom)
