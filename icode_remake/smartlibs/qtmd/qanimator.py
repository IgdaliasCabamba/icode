from PyQt5.QtWidgets import QLabel, QSizePolicy
from PyQt5.QtGui import QMovie
from PyQt5.QtCore import QSize


class Animator(QLabel):
    def __init__(self, parent, animation=None) -> None:
        super().__init__(parent)
        self.size_policy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setSizePolicy(self.size_policy)

        self.animation = animation
        self._animation_size = QSize(32, 32)
        if self.animation is not None:
            self.set_animation(self.animation)

    @property
    def movie(self):
        return self._movie

    def set_animation(self, animation_path: str = None, play: bool = True) -> None:
        self.animation = animation_path
        self._movie = QMovie(self.animation)
        self.setMovie(self._movie)
        if play:
            self.play()

    def set_scaled_size(self, w: int, h: int):
        if self.animation is not None:
            self._animation_size = QSize(w, h)
            self._movie.setScaledSize(self._animation_size)

    def update_movie(self):
        if self.animation is not None:
            self._movie.setScaledSize(self._animation_size)

    def play(self, visiblity: bool = True):
        if self.animation is not None:
            self._movie.start()
            self.setVisible(visiblity)
            self.update_movie()

    def stop(self, visiblity: bool = False):
        if self.animation is not None:
            self._movie.stop()
            self.setVisible(visiblity)
