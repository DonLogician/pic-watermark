from PyQt5.QtWidgets import QFrame, QVBoxLayout, QPushButton, QListWidget
from PyQt5.QtCore import QSize


class MainSidebar(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.StyledPanel)
        self.setFixedWidth(300)
        layout = QVBoxLayout(self)
        self.btn_select_images = QPushButton("选择图片")
        layout.addWidget(self.btn_select_images)
        self.btn_add_images = QPushButton("添加图片")
        layout.addWidget(self.btn_add_images)
        self.btn_select_folder = QPushButton("选择文件夹")
        layout.addWidget(self.btn_select_folder)
        self.list_widget = QListWidget()
        self.list_widget.setIconSize(QSize(128, 128))
        self.list_widget.setMinimumHeight(400)
        layout.addWidget(self.list_widget)
        layout.addStretch()
