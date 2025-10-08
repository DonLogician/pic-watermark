from PyQt5.QtWidgets import (
    QFrame,
    QVBoxLayout,
    QPushButton,
    QLabel,
    QLineEdit,
    QSlider,
    QHBoxLayout,
    QColorDialog,
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5 import QtGui


class WatermarkSettingsSidebar(QFrame):
    # 定义信号，传递水印内容、透明度和颜色
    watermark_settings_changed = pyqtSignal(str, int, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.StyledPanel)
        self.setFixedWidth(300)
        layout = QVBoxLayout(self)

        self.btn_back = QPushButton("返回")
        layout.addWidget(self.btn_back)
        layout.addSpacing(20)

        layout.addWidget(QLabel("水印内容："))
        self.watermark_text_edit = QLineEdit()
        self.watermark_text_edit.textChanged.connect(self.emit_watermark_settings)
        layout.addWidget(self.watermark_text_edit)

        layout.addWidget(QLabel("水印透明度 (0-100%)："))
        transparency_layout = QHBoxLayout()
        self.watermark_transparency_slider = QSlider(Qt.Horizontal)
        self.watermark_transparency_slider.setRange(0, 100)
        self.watermark_transparency_slider.setValue(50)  # 默认值为50
        self.watermark_transparency_slider.valueChanged.connect(self.emit_watermark_settings)
        transparency_layout.addWidget(self.watermark_transparency_slider)

        self.watermark_transparency_input = QLineEdit()
        self.watermark_transparency_input.setFixedWidth(50)
        self.watermark_transparency_input.setText("50")  # 默认值为50
        self.watermark_transparency_input.setValidator(QtGui.QIntValidator(0, 100))
        self.watermark_transparency_input.textChanged.connect(self.emit_watermark_settings)
        transparency_layout.addWidget(self.watermark_transparency_input)

        layout.addLayout(transparency_layout)

        layout.addWidget(QLabel("水印颜色："))
        self.color_picker_button = QPushButton("")
        self.color_picker_button.clicked.connect(self.open_color_dialog)
        layout.addWidget(self.color_picker_button)

        self.selected_color = "#FFFFFF"  # 默认颜色为白色
        self.color_picker_button.setStyleSheet(
            f"background-color: {self.selected_color};"
        )

        layout.addStretch()

        # 连接滑块和输入框的值变化
        self.watermark_transparency_slider.valueChanged.connect(self.sync_transparency_input)
        self.watermark_transparency_input.textChanged.connect(self.sync_transparency_slider)

    def sync_transparency_input(self, value):
        self.watermark_transparency_input.setText(str(value))

    def sync_transparency_slider(self):
        text = self.watermark_transparency_input.text()
        if text.isdigit():
            self.watermark_transparency_slider.setValue(int(text))

    def open_color_dialog(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.selected_color = color.name()
            self.color_picker_button.setStyleSheet(
                f"background-color: {self.selected_color};"
            )
            self.emit_watermark_settings()

    def emit_watermark_settings(self):
        # 发射信号，传递水印内容、透明度和颜色
        text = self.watermark_text_edit.text()
        transparency = int(self.watermark_transparency_input.text()) if self.watermark_transparency_input.text().isdigit() else 0
        self.watermark_settings_changed.emit(text, transparency, self.selected_color)
