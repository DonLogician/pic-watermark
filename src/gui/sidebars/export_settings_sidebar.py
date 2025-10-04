from PyQt5.QtWidgets import (
    QFrame,
    QVBoxLayout,
    QPushButton,
    QLabel,
    QComboBox,
    QLineEdit,
    QHBoxLayout,
)
from PyQt5.QtCore import pyqtSignal


class ExportSettingsSidebar(QFrame):
    # 修正信号定义，包含 4 个参数
    export_settings_changed = pyqtSignal(str, str, str, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.StyledPanel)
        self.setFixedWidth(300)
        layout = QVBoxLayout(self)
        self.btn_back = QPushButton("返回")
        layout.addWidget(self.btn_back)
        layout.addSpacing(20)
        layout.addWidget(QLabel("导出格式："))
        self.format_combo = QComboBox()
        self.format_combo.addItems(["JPEG", "PNG"])
        layout.addWidget(self.format_combo)
        layout.addWidget(QLabel("命名规则："))
        self.naming_rule_combo = QComboBox()
        self.naming_rule_combo.addItems(["保留原文件名", "添加前缀", "添加后缀"])
        layout.addWidget(self.naming_rule_combo)
        self.naming_prefix_edit = QLineEdit()
        self.naming_prefix_edit.setPlaceholderText("自定义前缀")
        layout.addWidget(self.naming_prefix_edit)
        self.naming_suffix_edit = QLineEdit()
        self.naming_suffix_edit.setPlaceholderText("自定义后缀")
        layout.addWidget(self.naming_suffix_edit)
        layout.addWidget(QLabel("导出路径："))
        path_layout = QHBoxLayout()
        self.export_path_edit = QLineEdit()
        self.export_path_edit.setReadOnly(True)
        path_layout.addWidget(self.export_path_edit)
        self.btn_select_export_path = QPushButton("选择")
        path_layout.addWidget(self.btn_select_export_path)
        layout.addLayout(path_layout)
        layout.addSpacing(40)
        layout.addStretch()
        # 绑定信号
        self.format_combo.currentIndexChanged.connect(self.on_format_changed)
        self.naming_rule_combo.currentIndexChanged.connect(self.on_naming_rule_changed)
        self.naming_prefix_edit.textChanged.connect(self.on_prefix_changed)
        self.naming_suffix_edit.textChanged.connect(self.on_suffix_changed)
        self.btn_select_export_path.clicked.connect(self.on_select_export_path)

        # 初始化时隐藏前缀和后缀输入框
        self.naming_prefix_edit.setVisible(False)
        self.naming_suffix_edit.setVisible(False)

    def on_format_changed(self, index):
        format = self.format_combo.currentText()
        self.emit_export_settings()
        print(f"导出格式已更改为: {format}")

    def on_naming_rule_changed(self, index):
        rule = self.naming_rule_combo.currentText()
        # 控制前缀/后缀输入框的显示状态
        if rule == "添加前缀":
            self.naming_prefix_edit.setVisible(True)
            self.naming_suffix_edit.setVisible(False)
        elif rule == "添加后缀":
            self.naming_prefix_edit.setVisible(False)
            self.naming_suffix_edit.setVisible(True)
        else:  # 保留原文件名
            self.naming_prefix_edit.setVisible(False)
            self.naming_suffix_edit.setVisible(False)
        self.emit_export_settings()
        print(f"命名规则已更改为: {rule}")

    def on_prefix_changed(self, text):
        # 可在此处添加前缀变更的逻辑
        self.emit_export_settings()
        print(f"前缀已更改为: {text}")

    def on_suffix_changed(self, text):
        # 可在此处添加后缀变更的逻辑
        self.emit_export_settings()
        print(f"后缀已更改为: {text}")

    def on_select_export_path(self):
        from PyQt5.QtWidgets import QFileDialog

        path = QFileDialog.getExistingDirectory(self, "选择导出文件夹")
        if path:
            self.export_path_edit.setText(path)
            self.emit_export_settings()
            print(f"导出路径已选择: {path}")

    def emit_export_settings(self):
        format = self.format_combo.currentText()
        prefix = (
            self.naming_prefix_edit.text()
            if self.naming_rule_combo.currentText() == "添加前缀"
            else ""
        )
        suffix = (
            self.naming_suffix_edit.text()
            if self.naming_rule_combo.currentText() == "添加后缀"
            else ""
        )
        export_path = self.export_path_edit.text()
        self.export_settings_changed.emit(format, prefix, suffix, export_path)
