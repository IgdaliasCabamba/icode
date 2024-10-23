from enum import Enum, auto
from typing import List
from dataclasses import dataclass
from PyQt5.QtWidgets import QFrame
from PyQt5.Qsci import QsciScintilla


class PanelPosition(Enum):
    LEFT = auto()
    RIGHT = auto()
    TOP = auto()
    BOTTOM = auto()
    
    @classmethod
    def all_positions(cls) -> List['PanelPosition']:
        return [PanelPosition.LEFT, PanelPosition.RIGHT, 
                PanelPosition.TOP, PanelPosition.BOTTOM]
    

@dataclass(frozen=True)
class ZoneSizes:
    left: int
    top: int
    right: int
    bottom: int


@dataclass
class PanelSettings:
    scrollable: bool = False
    level: int = 0  # 0: normal, 1: above scrollbar, 2: full width/height
    order: int = 0  # Order within zone (lower numbers appear first)

    
class Panel(QFrame):
    """Base class for editor panels"""
    def __init__(self, editor: QsciScintilla):
        super().__init__(editor)
        self.setAutoFillBackground(False)
        self.editor = editor
        self._position = PanelPosition.LEFT
        self._settings = PanelSettings()
        
    @property
    def position(self) -> PanelPosition:
        return self._position
        
    @position.setter 
    def position(self, value: PanelPosition):
        self._position = value
        
    @property
    def settings(self) -> PanelSettings:
        return self._settings
        
    @settings.setter
    def settings(self, value: PanelSettings):
        self._settings = value