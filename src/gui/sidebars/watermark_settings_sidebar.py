from PyQt5.QtWidgets import QFrame, QVBoxLayout, QPushButton, QLabel, QLineEdit


class WatermarkSettingsSidebar(QFrame):
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
        layout.addWidget(self.watermark_text_edit)
        # 可扩展更多水印设置项
        layout.addStretch()
