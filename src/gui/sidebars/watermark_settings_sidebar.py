from PyQt5.QtWidgets import (
    QFrame,
    QVBoxLayout,
    QPushButton,
    QLabel,
    QLineEdit,
    QSlider,
    QHBoxLayout,
    QColorDialog,
    QComboBox,
    QMessageBox,
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5 import QtGui
from src.watermark_tools.settings_manager import (
    save_watermark_template,
    load_watermark_template,
    delete_watermark_template,
    get_available_templates
)


class WatermarkSettingsSidebar(QFrame):
    # 定义信号，传递水印内容、透明度、颜色、字号和位置
    watermark_settings_changed = pyqtSignal(str, int, str, int, str)
    # 定义信号，用于通知主窗口刷新模板列表
    templates_changed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.StyledPanel)
        self.setFixedWidth(300)
        layout = QVBoxLayout(self)
        self.parent = parent

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

        # 添加水印字号设置
        layout.addWidget(QLabel("水印字号："))
        self.font_size_input = QLineEdit()
        self.font_size_input.setFixedWidth(50)
        self.font_size_input.setText("24")  # 初始值为24
        self.font_size_input.setValidator(QtGui.QIntValidator(1, 1000))
        self.font_size_input.textChanged.connect(self.emit_watermark_settings)
        layout.addWidget(self.font_size_input)

        # 添加水印位置设置
        layout.addWidget(QLabel("水印位置："))
        self.watermark_position_combo = QComboBox()
        self.watermark_position_combo.addItems(["中央", "左上角", "右上角", "左下角", "右下角", "自定义(0-1)"])
        self.watermark_position_combo.currentIndexChanged.connect(self.emit_watermark_settings)
        self.watermark_position_combo.currentIndexChanged.connect(self.toggle_custom_position_inputs)
        layout.addWidget(self.watermark_position_combo)
        
        # 添加自定义位置输入框
        self.custom_position_layout = QHBoxLayout()
        
        self.x_position_input = QLineEdit()
        self.x_position_input.setFixedWidth(80)
        self.x_position_input.setPlaceholderText("X坐标")
        self.x_position_input.setValidator(QtGui.QDoubleValidator(0.0, 1.0, 3))
        self.x_position_input.textChanged.connect(self.emit_watermark_settings)
        
        self.y_position_input = QLineEdit()
        self.y_position_input.setFixedWidth(80)
        self.y_position_input.setPlaceholderText("Y坐标")
        self.y_position_input.setValidator(QtGui.QDoubleValidator(0.0, 1.0, 3))
        self.y_position_input.textChanged.connect(self.emit_watermark_settings)
        
        self.custom_position_layout.addWidget(self.x_position_input)
        self.custom_position_layout.addWidget(self.y_position_input)
        
        # 默认隐藏自定义位置输入框
        self.custom_position_widget = QFrame()
        self.custom_position_widget.setLayout(self.custom_position_layout)
        self.custom_position_widget.hide()
        layout.addWidget(self.custom_position_widget)

        # 分隔线
        layout.addSpacing(30)
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        layout.addWidget(separator)
        layout.addSpacing(30)

        # 水印模板管理
        layout.addWidget(QLabel("水印模板："))
        
        # 模板名称输入框和保存按钮
        template_name_layout = QHBoxLayout()
        self.template_name_edit = QLineEdit()
        self.template_name_edit.setPlaceholderText("模板名称")
        template_name_layout.addWidget(self.template_name_edit)
        self.btn_save_template = QPushButton("保存")
        self.btn_save_template.setFixedWidth(60)
        self.btn_save_template.clicked.connect(self.save_template)
        template_name_layout.addWidget(self.btn_save_template)
        layout.addLayout(template_name_layout)
        
        # 模板列表和操作按钮
        template_list_layout = QHBoxLayout()
        self.template_list_combo = QComboBox()
        self.refresh_template_list()
        template_list_layout.addWidget(self.template_list_combo)
        self.btn_load_template = QPushButton("加载")
        self.btn_load_template.setFixedWidth(60)
        self.btn_load_template.clicked.connect(self.load_template)
        template_list_layout.addWidget(self.btn_load_template)
        layout.addLayout(template_list_layout)
        
        # 删除模板按钮
        self.btn_delete_template = QPushButton("删除选中模板")
        self.btn_delete_template.clicked.connect(self.delete_template)
        layout.addWidget(self.btn_delete_template)

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

    def toggle_custom_position_inputs(self):
        # 当选择"自定义(0-1)"选项时显示坐标输入框，否则隐藏
        is_custom = self.watermark_position_combo.currentText() == "自定义(0-1)"
        self.custom_position_widget.setVisible(is_custom)
        # 如果切换到自定义位置，尝试从主窗口获取当前位置
        if is_custom and hasattr(self.parent, 'watermark_position') and isinstance(self.parent.watermark_position, tuple):
            x, y = self.parent.watermark_position
            self.x_position_input.setText(f"{x:.3f}")
            self.y_position_input.setText(f"{y:.3f}")
    
    def emit_watermark_settings(self):
        # 发射信号，传递水印内容、透明度、颜色、字号和位置
        text = self.watermark_text_edit.text()
        transparency = int(self.watermark_transparency_input.text()) if self.watermark_transparency_input.text().isdigit() else 0
        font_size = int(self.font_size_input.text()) if self.font_size_input.text().isdigit() else 24
        
        position = self.watermark_position_combo.currentText()
        signal_position = position
        # 如果选择了自定义位置且输入了有效的坐标值
        if position == "自定义(0-1)":
            try:
                x = float(self.x_position_input.text())
                y = float(self.y_position_input.text())
                # 验证坐标在0-1范围内
                if 0 <= x <= 1 and 0 <= y <= 1:
                    # 直接设置到主窗口
                    if hasattr(self.parent, 'watermark_position'):
                        self.parent.watermark_position = (x, y)
            except ValueError:
                # 如果输入无效，使用默认行为
                pass
        
        # 始终使用字符串类型发射信号
        self.watermark_settings_changed.emit(text, transparency, self.selected_color, font_size, signal_position)
        
    def refresh_template_list(self):
        """刷新模板列表"""
        self.template_list_combo.clear()
        templates = get_available_templates()
        self.template_list_combo.addItems(templates)
        
    def save_template(self):
        """保存当前水印设置为模板"""
        template_name = self.template_name_edit.text().strip()
        if not template_name:
            QMessageBox.warning(self, "警告", "请输入模板名称！")
            return
            
        # 获取当前水印设置
        settings = {
            'text': self.watermark_text_edit.text(),
            'transparency': int(self.watermark_transparency_input.text()) if self.watermark_transparency_input.text().isdigit() else 0,
            'color': self.selected_color,
            'font_size': int(self.font_size_input.text()) if self.font_size_input.text().isdigit() else 24
        }
        
        # 优先获取主窗口中的精确位置坐标（如果存在）
        if hasattr(self.parent, 'watermark_position'):
            settings['position'] = self.parent.watermark_position
        else:
            # 否则使用下拉菜单中的预设位置
            settings['position'] = self.watermark_position_combo.currentText()
        
        if save_watermark_template(template_name, settings):
            QMessageBox.information(self, "成功", f"模板 '{template_name}' 保存成功！")
            self.template_name_edit.clear()
            self.refresh_template_list()
            self.templates_changed.emit()
        else:
            QMessageBox.warning(self, "失败", f"模板 '{template_name}' 保存失败！")
            
    def load_template(self):
        """加载选中的水印模板"""
        template_name = self.template_list_combo.currentText()
        if not template_name:
            QMessageBox.warning(self, "警告", "请选择要加载的模板！")
            return
            
        settings = load_watermark_template(template_name)
        if settings:
            # 应用模板设置
            self.watermark_text_edit.setText(settings.get('text', ''))
            self.watermark_transparency_input.setText(str(settings.get('transparency', 50)))
            self.watermark_transparency_slider.setValue(settings.get('transparency', 50))
            self.selected_color = settings.get('color', '#FFFFFF')
            self.color_picker_button.setStyleSheet(f"background-color: {self.selected_color};")
            self.font_size_input.setText(str(settings.get('font_size', 24)))
            
            # 处理位置信息
            position = settings.get('position', '中央')
            
            # 检查位置是否为精确坐标（列表或元组）
            if (isinstance(position, (list, tuple)) and len(position) == 2):
                # 如果是列表，转换为元组
                if isinstance(position, list):
                    position = tuple(position)
                # 直接设置到主窗口的watermark_position属性
                if hasattr(self.parent, 'watermark_position'):
                    self.parent.watermark_position = position
                
                # 设置下拉菜单为自定义选项
                custom_index = self.watermark_position_combo.findText("自定义(0-1)")
                if custom_index >= 0:
                    self.watermark_position_combo.setCurrentIndex(custom_index)
                    # 显示自定义位置输入框
                    self.custom_position_widget.setVisible(True)
                    # 设置坐标输入框的值
                    x, y = position
                    self.x_position_input.setText(f"{x:.3f}")
                    self.y_position_input.setText(f"{y:.3f}")
            else:
                # 否则处理为预设位置字符串
                position_index = self.watermark_position_combo.findText(position)
                if position_index >= 0:
                    self.watermark_position_combo.setCurrentIndex(position_index)
            
            # 发射信号更新主窗口
            self.emit_watermark_settings()
        else:
            QMessageBox.warning(self, "失败", f"模板 '{template_name}' 加载失败！")
            
    def delete_template(self):
        """删除选中的水印模板"""
        template_name = self.template_list_combo.currentText()
        if not template_name:
            QMessageBox.warning(self, "警告", "请选择要删除的模板！")
            return
            
        reply = QMessageBox.question(
            self, "确认删除", f"确定要删除模板 '{template_name}' 吗？",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            if delete_watermark_template(template_name):
                QMessageBox.information(self, "成功", f"模板 '{template_name}' 删除成功！")
                self.refresh_template_list()
                self.templates_changed.emit()
            else:
                QMessageBox.warning(self, "失败", f"模板 '{template_name}' 删除失败！")
