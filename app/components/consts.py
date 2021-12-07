from PyQt5.QtCore import QSize, QRect

APP_BASE_FONT_SIZE:int = 11
MAINWINDOW_BASE_GEOMETRY:QRect = QRect(0, 0, 1000, 600)
DIV_CHILD_SIZES:list = [1000,1000,0]
DIV_MAIN_SIZES:list = [300,1000,300]
DIV_MAIN_MIN_SIZE:QSize = QSize(100, 100)
INIT_TAB_COUNT:int = 0
MAX_TITLE_LENGTH:int = 20
EXPANDED_TAB_WIDTH:int = 8
LAB_BASE_SIZE:int = 300

WINDOW_NO_STATE:int = 0
WINDOW_MINIMIZED:int=1
WINDOW_MAXIMIZED:int = 2
WINDOW_FULLSCREEN:int = 4

MINIMAP_MINIMUM_ZOOM:int = -10
MINIMAP_CURSOR:int = 8
MINIMAP_EXTRA_ASCENT:int = -1
MINIMAP_EXTRA_DESCENT:int = -1
MINIMAP_FIXED_WIDTH = 160
MINIMAP_BOX_FIXED_WIDTH = 160
MINIMAP_SLIDER_OPACITY_MIN = 0
MINIMAP_SLIDER_OPACITY_MID = 15
MINIMAP_SLIDER_OPACITY_MAX = 30
MINIMAP_SLIDER_AREA_FIXED_SIZE = QSize(160, 80)
MINIMAP_SHADOW_MIN_TEXT_WIDTH = 50
MINIMAP_BOX_SHADOW_BLURRADIUS = 12
MINIMAP_BOX_SHADOW_Y_OFFSET = -3
MINIMAP_BOX_SHADOW_X_OFFSET = 0

EDITOR_LAYOUT_SPACING = 0
EDITOR_DIV_SIZES = [100,100]
EDITOR_MIN_WIDTH = 200
UP_MAP_FIXED_HEIGHT = 24
UP_MAP_SHADOW_BLURRADIUS_STATE0 = 2
UP_MAP_SHADOW_Y_OFFSET_STATE0 = 0
UP_MAP_SHADOW_X_OFFSET_STATE0 = 0
UP_MAP_SHADOW_BLURRADIUS_STATE1 = 10
UP_MAP_SHADOW_Y_OFFSET_STATE1 = 0
UP_MAP_SHADOW_X_OFFSET_STATE1 = 3

JEDI_TEXT_WRAP_WIDTH = 50
JEDI_HELP_SHORTEN_WIDTH = 400
JEDI_SIGNATURES_WRAP_WIDTH = 90

EOL_WINDOWS = 0
EOL_MAC = 1
EOL_LINUX = 2

CODE_PAGE_JAPANESE = 932
CODE_PAGE_SIMPLIFIED_CHINESE = 936
CODE_PAGE_TRADITIONAL_CHINESE = 950
CODE_PAGE_KOREAN_UNIFIED = 949
CODE_PAGE_KOREAN_JOHAB = 1361
