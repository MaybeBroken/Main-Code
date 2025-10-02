IMG_PATH = "./img.png"

import sys
import math
from dataclasses import dataclass

from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import Qt
from PySide6.QtGui import (
    QAction,
    QCursor,
    QFont,
    QImage,
    QPainter,
    QPixmap,
)
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFormLayout,
    QGridLayout,
    QGroupBox,
    QLabel,
    QSlider,
    QSpinBox,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)


class ScreensaverWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_OpaquePaintEvent)
        self.setAttribute(Qt.WA_NoSystemBackground)
        self.setMouseTracking(True)
        self.image = QImage(IMG_PATH)
        self.image = self.image.scaled(
            400, 400, Qt.KeepAspectRatio, Qt.SmoothTransformation
        )
        self.image = self.image.convertToFormat(QImage.Format_ARGB32)
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update_animation)
        self.timer.start(16)  # Approximately 60 FPS
        self.x = 0
        self.y = 0
        self.min_x = 0
        self.min_y = 0
        self.x_dir = 1
        self.y_dir = 1
        self.max_x = 0
        self.max_y = 0
        self.speed_fac = 1.8
        self.scale = 1.0

    def update_animation(self):
        # Recompute bounds based on current size so the image moves correctly
        self.max_x = max(0, self.width() - (self.image.width() * self.scale))
        self.max_y = max(0, self.height() - (self.image.height() * self.scale))

        self.x += self.x_dir * self.speed_fac
        self.y += self.y_dir * self.speed_fac
        if self.x >= self.max_x or self.x <= self.min_x:
            self.x_dir *= -1
            self.x = max(self.min_x, min(self.x, self.max_x))
        if self.y >= self.max_y or self.y <= self.min_y:
            self.y_dir *= -1
            self.y = max(self.min_y, min(self.y, self.max_y))
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), Qt.black)

        if not self.image.isNull():
            image = self.image.scaled(
                int(400 * self.scale),
                int(400 * self.scale),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation,
            )
            painter.drawImage(self.x, self.y, image)

        painter.end()
        event.accept()


class UISettingsWindow(QDialog):
    def __init__(self, root: "ScreensaverApp"):
        super().__init__()
        self.setWindowTitle("Screensaver Settings")
        self.screensaver_widget = root.screensaver_widget
        self.root = root
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.speed_label = QLabel("Speed:")
        self.speed_slider = QSlider(Qt.Horizontal)
        self.speed_slider.setMinimum(1)
        self.speed_slider.setMaximum(100)
        self.speed_slider.setValue(int(self.screensaver_widget.speed_fac * 10))
        self.speed_slider.valueChanged.connect(self.update_speed)

        self.scale_label = QLabel("Scale:")
        self.scale_slider = QSlider(Qt.Horizontal)
        self.scale_slider.setMinimum(10)
        self.scale_slider.setMaximum(300)
        self.scale_slider.setValue(int(self.screensaver_widget.scale * 100))
        self.scale_slider.valueChanged.connect(self.update_scale)

        self.layout.addWidget(self.speed_label)
        self.layout.addWidget(self.speed_slider)
        self.layout.addWidget(self.scale_label)
        self.layout.addWidget(self.scale_slider)

        self.button_box = QDialogButtonBox(QDialogButtonBox.Close)
        self.button_box.rejected.connect(self.close)
        self.layout.addWidget(self.button_box)

    def keyPressEvent(self, arg__1):
        if arg__1.key() == Qt.Key_C:
            self.root.ui_toggle()

    def update_speed(self, value):
        self.screensaver_widget.speed_fac = value / 10.0

    def update_scale(self, value):
        self.screensaver_widget.scale = value / 100.0


class ScreensaverApp(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TV Screensaver")
        self.setGeometry(100, 100, 800, 600)
        self.screensaver_widget = ScreensaverWidget(self)
        self.setCentralWidget(self.screensaver_widget)
        self.ui_window = None
        self.ui_visible = False
        self.setCursor(Qt.BlankCursor)
        self.screensaver_widget.setCursor(Qt.BlankCursor)
        self.showFullScreen()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Q:
            self.close()
        elif event.key() == Qt.Key_C:
            self.ui_toggle()

    def closeEvent(self, event):
        self.screensaver_widget.timer.stop()
        event.accept()

    def ui_toggle(self):
        self.ui_visible = not self.ui_visible
        if self.ui_visible:
            if self.ui_window is None:
                self.ui_window = UISettingsWindow(self)
            self.ui_window.show()
            # Show the mouse cursor
            self.unsetCursor()
            self.screensaver_widget.unsetCursor()
        else:
            if self.ui_window is not None:
                self.ui_window.hide()
            # Hide the mouse cursor over the screensaver
            self.setCursor(Qt.BlankCursor)
            self.screensaver_widget.setCursor(Qt.BlankCursor)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ScreensaverApp()
    window.show()
    sys.exit(app.exec())
