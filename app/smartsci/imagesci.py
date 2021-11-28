import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.Qsci import *

class ImageScintilla(QsciScintilla):
    class Image:

        def __init__(self, image, position, size=None):
            if isinstance(image, str) == False:
                raise Exception("Enter path to image as a string.")
            elif isinstance(position, tuple) == False or len(position) != 2:
                raise Exception("Image position should be of type tuple(int, int)!")
            elif size != None and (isinstance(position, tuple) == False \
                                           or len(position) != 2):
                raise Exception("Image size has to be of type tuple(int, int)!")
            self.image = QImage(image)
            if size != None:
                self.image = self.image.scaled(*size)
            self.position = position
            self.size = size

    maximum_image_count = 100
    image_list = None
    calculation_font = None
    line_list = None

    def __init__(self, parent=None):
        super().__init__(parent)
        self.image_list = {}
        self.line_list = []
        self.calculation_font = self.font()
        self.SCN_MODIFIED.connect(self.text_changed)

    def set_calculation_font(self, font):
        if isinstance(font, QFont) == False:
            raise Exception("The calculation font has to be a QFont!")
        self.calculation_font = font

    def add_image(self, image, position, size):
        image = self.Image(image, position, size)
        for i in range(self.maximum_image_count):
            if not (i in self.image_list.keys()):
                self.image_list[i] = image
                return i
        else:
            raise Exception("Too many images in the editor, the maximum is '{}'"\
                            .format(self.maximum_image_count))

    def delete_image(self, index):
        if isinstance(index, int) == False or index > self.maximum_image_count:
            raise Exception(
                "Index for deletion should be smaller integer than maximum_image_count")
        self.image_list.pop(index, None)

    def get_font_metrics(self, font):
        font_metrics = QFontMetrics(font)
        single_character_width = font_metrics.width("A")
        single_character_height = font_metrics.height()
        return single_character_width, single_character_height

    def text_changed(self,
                     position,
                     mod_type,
                     text,
                     length,
                     lines_added,
                     line,
                     fold_level_now,
                     fold_level_prev,
                     token,
                     additional_lines_added):
        insert_flag = mod_type & 0b1
        delete_flag = mod_type & 0b10
        if insert_flag or delete_flag:
            change_line, change_column = self.lineIndexFromPosition(position)
            
            if lines_added != 0:
                
                for key, image in self.image_list.items():
                    x, y = image.position
                    if y >= change_line:
                        image.position = (x, y + lines_added)

    def paintEvent(self, e):
        super().paintEvent(e)
        
        current_parent_size = self.size()
        first_visible_line = self.SendScintilla(self.SCI_GETFIRSTVISIBLELINE)
        column_offset_in_pixels = self.SendScintilla(self.SCI_GETXOFFSET)
        single_character_width, single_character_height = self.get_font_metrics(
            self.calculation_font
        )
        
        painter = QPainter()
        painter.begin(self.viewport())
        
        for i in self.image_list.keys():
            
            image = self.image_list[i].image
            paint_offset_x = (self.image_list[i].position[0] * single_character_width)\
                             - column_offset_in_pixels
            paint_offset_y = (self.image_list[i].position[1] - first_visible_line)\
                             * single_character_height
            
            painter.drawImage(QPoint(paint_offset_x, paint_offset_y), image)
        
        painter.end()