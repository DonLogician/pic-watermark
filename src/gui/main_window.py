import sys
import os
from PyQt5.QtWidgets import (
    QFrame,
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QFileDialog,
    QLabel,
    QSizePolicy,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QDesktopWidget
)
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import QSize, Qt

# 引入拆分后的sidebar类
from src.gui.sidebars.main_sidebar import MainSidebar
from src.gui.sidebars.export_settings_sidebar import ExportSettingsSidebar
from src.gui.sidebars.watermark_settings_sidebar import WatermarkSettingsSidebar
from src.watermark_tools.config import DEFAULT_EXPORT_FORMAT, DEFAULT_WATERMARK_COLOR, DEFAULT_WATERMARK_TEXT, DEFAULT_WATERMARK_TRANSPARENCY, DEFAULT_FONT_SIZE


# 保证DraggableListWidget可用
class DraggableListWidget(QListWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            files = []
            exts = (".jpg", ".jpeg", ".png", ".bmp", ".tiff")
            for url in event.mimeData().urls():
                path = url.toLocalFile()
                if os.path.isfile(path) and path.lower().endswith(exts):
                    files.append(path)
            if files:
                self.main_window.add_images(files)
            event.acceptProposedAction()
        else:
            event.ignore()


class MainWindow(QMainWindow):
    def _move_export_btn(self):
        # 将导出按钮定位到主窗口右下角，保持20px边距
        btn_w = self.export_btn.width()
        btn_h = self.export_btn.height()
        win_w = self.width()
        win_h = self.height()
        margin = 20
        x = win_w - btn_w - margin
        y = win_h - btn_h - margin
        self.export_btn.move(x, y)

    def select_images(self):
        files, _ = QFileDialog.getOpenFileNames(
            self, "选择图片", "", "图片文件 (*.jpg *.jpeg *.png *.bmp *.tiff)"
        )
        if files:
            self.list_widget.clear()
            self.image_paths = []
            self.add_images(files)

    def select_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "选择文件夹", "")
        if folder:
            exts = (".jpg", ".jpeg", ".png", ".bmp", ".tiff")
            files = [
                os.path.join(folder, f)
                for f in os.listdir(folder)
                if f.lower().endswith(exts)
            ]
            self.list_widget.clear()
            self.image_paths = []
            self.add_images(files)

    def __init__(self):
        self.image_paths = []
        self.export_path = ""  # 确保初始化
        self.export_naming_rule = 0
        self.export_format = DEFAULT_EXPORT_FORMAT
        # 初始化水印设置
        self.watermark_text = DEFAULT_WATERMARK_TEXT
        self.watermark_transparency = DEFAULT_WATERMARK_TRANSPARENCY
        self.watermark_color = DEFAULT_WATERMARK_COLOR
        self.watermark_font_size = DEFAULT_FONT_SIZE  # 从配置中导入的默认字号
        self.watermark_position = "center"  # 默认中央位置
        super().__init__()
        self.setWindowTitle("图片水印工具")
        
        # 获取屏幕尺寸并设置窗口大小为屏幕的70%×70%
        desktop = QDesktopWidget()
        screen_width = desktop.screenGeometry().width()
        screen_height = desktop.screenGeometry().height()
        
        # 设置窗口宽度和高度为屏幕尺寸的70%
        window_width = int(screen_width * 0.7)
        window_height = int(screen_height * 0.7)
        
        # 设置窗口的最大尺寸为屏幕尺寸的90%，避免窗口无限制扩大
        max_width = int(screen_width * 0.9)
        max_height = int(screen_height * 0.9)
        
        self.resize(window_width, window_height)
        self.setMaximumSize(max_width, max_height)

        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)

        # 左侧 sidebar
        self.sidebar_main = MainSidebar(self)
        self.sidebar_main.list_widget.setParent(None)
        self.list_widget = DraggableListWidget(self)
        self.list_widget.setIconSize(QSize(128, 128))
        self.list_widget.setMinimumHeight(400)
        self.sidebar_main.layout().insertWidget(3, self.list_widget)
        self.sidebar_main.list_widget = self.list_widget
        main_layout.addWidget(self.sidebar_main)

        # 信号连接
        self.sidebar_main.btn_select_images.clicked.connect(self.select_images)
        self.sidebar_main.btn_add_images.clicked.connect(self.add_images_dialog)
        self.sidebar_main.btn_select_folder.clicked.connect(self.select_folder)
        self.list_widget.itemSelectionChanged.connect(self.show_preview)

        # 中间预览区（填充中间空间）
        preview_frame = QWidget()
        # 设置预览框架的尺寸策略，使其填充可用空间
        preview_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        preview_frame.setStyleSheet("background:#f5f5f5;border:1px solid #ccc;")
        
        # 创建预览布局
        preview_layout = QVBoxLayout(preview_frame)
        preview_layout.setContentsMargins(20, 20, 20, 20)  # 与左右sidebar保持距离
        
        # 水印预览标签
        self.preview_label_watermarked = QLabel("水印预览区")
        self.preview_label_watermarked.setAlignment(Qt.AlignCenter)
        
        # 在初始化时设置预览区的固定大小
        # 左侧sidebar宽度
        left_sidebar_width = 300
        # 右侧sidebar宽度
        right_sidebar_width = 300
        # 预留的间隔大小
        margin = 20
        
        # 计算预览区宽度：窗口宽度 - 左侧sidebar宽度 - 右侧sidebar宽度 - 左右边距
        preview_width = window_width - left_sidebar_width - right_sidebar_width - (margin * 2)
        # 计算预览区高度：窗口高度 - 上下边距
        preview_height = window_height - (margin * 2)
        
        # 确保预览区尺寸为正数
        if preview_width > 100 and preview_height > 100:
            self.preview_label_watermarked.setFixedSize(preview_width, preview_height)
        
        preview_layout.addWidget(self.preview_label_watermarked)
        
        main_layout.addWidget(preview_frame)

        # 右侧 sidebar
        self.sidebar_right = QFrame()
        self.sidebar_right.setFrameShape(QFrame.StyledPanel)
        self.sidebar_right.setFixedWidth(300)
        sidebar_right_layout = QVBoxLayout(self.sidebar_right)
        self.btn_export_settings = QPushButton("导出设置")
        self.btn_export_settings.setStyleSheet("font-size:16px;")
        sidebar_right_layout.addWidget(self.btn_export_settings)
        self.btn_watermark_settings = QPushButton("水印设置")
        self.btn_watermark_settings.setStyleSheet("font-size:16px;")
        sidebar_right_layout.addWidget(self.btn_watermark_settings)
        sidebar_right_layout.addStretch()
        main_layout.addWidget(self.sidebar_right)

        # 导出设置sidebar（初始隐藏）
        self.sidebar_export_settings = ExportSettingsSidebar(self)
        self.sidebar_export_settings.hide()
        main_layout.addWidget(self.sidebar_export_settings)
        self.btn_export_settings.clicked.connect(self.show_export_settings_sidebar)
        self.sidebar_export_settings.btn_back.clicked.connect(self.show_main_sidebar)

        # 水印设置sidebar（初始隐藏）
        self.sidebar_watermark_settings = WatermarkSettingsSidebar(self)
        self.sidebar_watermark_settings.hide()
        main_layout.addWidget(self.sidebar_watermark_settings)
        self.btn_watermark_settings.clicked.connect(self.show_watermark_settings_sidebar)
        self.sidebar_watermark_settings.btn_back.clicked.connect(self.show_main_sidebar)

        # 导出按钮，主窗口右下角始终显示
        self.export_btn = QPushButton("导出", self)
        self.export_btn.setFixedSize(120, 40)
        self.export_btn.setStyleSheet("font-size:18px;")
        self.export_btn.clicked.connect(self.export_images)
        self.export_btn.show()
        self._move_export_btn()

        # 连接导出设置信号
        self.sidebar_export_settings.export_settings_changed.connect(
            self.handle_export_settings_change
        )
        # 连接水印设置信号
        self.sidebar_watermark_settings.watermark_settings_changed.connect(
            self.handle_watermark_settings_change
        )

    def handle_export_settings_change(self, format, prefix, suffix, export_path):
        # 检查导出路径是否与已上传图片的目录冲突
        if export_path:
            # 如果存在前缀或后缀命名规则，则跳过路径冲突检查
            if prefix or suffix:
                self.export_path = export_path
                print("路径冲突检查跳过，因为存在前缀或后缀命名规则。")
            else:
                img_dirs = set(os.path.dirname(p) for p in self.image_paths)
                if export_path in img_dirs:
                    from PyQt5.QtWidgets import QMessageBox

                    QMessageBox.warning(
                        self,
                        "导出路径冲突",
                        "导出路径不能与原图所在文件夹相同，否则可能覆盖原图！",
                    )
                    # 清空冲突路径
                    self.sidebar_export_settings.export_path_edit.clear()
                    self.export_path = ""
                else:
                    self.export_path = export_path

        # 更新其他导出设置
        self.export_format = format
        self.export_prefix = prefix
        self.export_suffix = suffix
        self.export_naming_rule = (
            self.sidebar_export_settings.naming_rule_combo.currentIndex()
        )
        print(
            f"导出设置更新: 格式={format}, 前缀={prefix}, 后缀={suffix}, 路径={export_path}"
        )

    def handle_watermark_settings_change(self, text, transparency, color, font_size, position):
        # 处理水印设置的变化
        if text:
            self.watermark_text = text
        self.watermark_transparency = transparency
        self.watermark_color = color
        self.watermark_font_size = font_size
        # 将中文位置转换为英文位置参数
        position_map = {
            "中央": "center",
            "左上角": "top-left",
            "右上角": "top-right",
            "左下角": "bottom-left",
            "右下角": "bottom-right"
        }
        self.watermark_position = position_map.get(position, "center")
        print(f"水印设置更新: 内容={self.watermark_text}, 透明度={transparency}, 颜色={color}, 字号={font_size}, 位置={position}")
        # 实时更新预览
        self.show_preview()

    def select_export_path(self):
        folder = QFileDialog.getExistingDirectory(self, "选择导出文件夹", "")
        if folder:
            self.export_path_edit.setText(folder)
            self.export_path = folder
            self.check_export_path_conflict()

    def check_export_path_conflict(self):
        # 检查导出路径是否与图片所在文件夹冲突
        if (
            not self.export_path
            or not hasattr(self, "image_paths")
            or not self.image_paths
        ):
            return

        # 如果存在前缀或后缀命名规则，则跳过路径冲突检查
        if self.export_prefix or self.export_suffix:
            print("路径冲突检查跳过，因为存在前缀或后缀命名规则。")
            return

        from PyQt5.QtWidgets import QMessageBox

        img_dirs = set(os.path.dirname(p) for p in self.image_paths)
        if self.export_path in img_dirs:
            QMessageBox.warning(
                self,
                "导出路径冲突",
                "导出路径不能与原图所在文件夹相同，否则可能覆盖原图！",
            )

    def show_export_settings_sidebar(self):
        # 切换到导出设置sidebar
        self.sidebar_right.hide()
        self.sidebar_export_settings.show()

    def show_watermark_settings_sidebar(self):
        # 切换到水印设置sidebar
        self.sidebar_right.hide()
        self.sidebar_watermark_settings.show()

    def show_main_sidebar(self):
        # 返回主sidebar
        self.sidebar_export_settings.hide()
        self.sidebar_watermark_settings.hide()
        self.sidebar_right.show()

    # ...existing code...

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, "export_btn") and self.export_btn:
            self._move_export_btn()
        
        # 仅移动导出按钮，不更新预览区大小，避免触发循环

    def export_images(self):
        from PyQt5.QtWidgets import QMessageBox
        from src.watermark_tools.batch_processor import batch_export_images

        if not self.image_paths:
            QMessageBox.warning(self, "警告", "未选择任何图片！")
            return
        if not self.export_path:
            QMessageBox.warning(self, "警告", "未选择导出路径！")
            return

        img_dirs = set(os.path.dirname(p) for p in self.image_paths)
        if self.export_path in img_dirs and not (
            self.export_prefix or self.export_suffix
        ):
            QMessageBox.warning(self, "警告", "导出路径不能与图片所在文件夹相同！")
            return

        count = batch_export_images(
            self.image_paths,
            output_format=self.export_format,
            output_dir=self.export_path,
            prefix=self.export_prefix,
            suffix=self.export_suffix,
            naming_rule=self.export_naming_rule,
            watermark_text=self.watermark_text,
            transparency=self.watermark_transparency,
            color=self.watermark_color,
            position=self.watermark_position,
            font_size=self.watermark_font_size
        )
        if count:
            QMessageBox.information(self, "成功", f"成功导出 {count} 张图片！")
        else:
            QMessageBox.warning(self, "失败", "导出失败，请检查设置！")

    def add_images(self, files):
        # 不清除已选图片，追加
        for file in files:
            if file not in self.image_paths:
                self.image_paths.append(file)
                item = QListWidgetItem(os.path.basename(file))
                pixmap = QPixmap(file)
                if not pixmap.isNull():
                    icon = QIcon(
                        pixmap.scaled(
                            QSize(128, 128), Qt.KeepAspectRatio, Qt.SmoothTransformation
                        )
                    )
                    item.setIcon(icon)
                self.list_widget.addItem(item)
        self.check_export_path_conflict()

    def add_images_dialog(self):
        files, _ = QFileDialog.getOpenFileNames(
            self, "添加图片", "", "图片文件 (*.jpg *.jpeg *.png *.bmp *.tiff)"
        )
        if files:
            self.add_images(files)

    def show_preview(self):
        selected = self.list_widget.currentRow()
        if selected < 0 or selected >= len(self.image_paths):
            self.preview_label_watermarked.clear()
            self.preview_label_watermarked.setText("水印预览区")
            return
        img_path = self.image_paths[selected]

        # 水印预览，文件存储到tmp文件夹
        try:
            from src.watermark_tools.watermark_processor import add_watermark_to_image

            # watermark_text = "预览水印"
            tmp_dir = os.path.join(os.getcwd(), "tmp")
            if not os.path.exists(tmp_dir):
                os.makedirs(tmp_dir)
            import uuid

            tmp_path = os.path.join(tmp_dir, f"preview_{uuid.uuid4().hex}.png")
            # 传递所有水印设置参数，包括透明度和导出格式
            success = add_watermark_to_image(
                img_path, 
                self.watermark_text, 
                tmp_path,
                position=self.watermark_position,
                font_size=self.watermark_font_size,
                color=self.watermark_color,
                transparency=self.watermark_transparency,
                extension=self.export_format.lower()
            )
            if success:
                pixmap_wm = QPixmap(tmp_path)
                if not pixmap_wm.isNull():
                    # 使用固定的预览区域尺寸进行图片缩放
                    w = self.preview_label_watermarked.width()
                    h = self.preview_label_watermarked.height()
                    
                    # 确保图片按比例缩放并完全适应预览区域
                    scaled_wm = pixmap_wm.scaled(
                        w, h, Qt.KeepAspectRatio, Qt.SmoothTransformation
                    )
                    self.preview_label_watermarked.setPixmap(scaled_wm)
                else:
                    self.preview_label_watermarked.setText("无法加载水印图片")
            else:
                self.preview_label_watermarked.setText("水印生成失败")
        except Exception as e:
            self.preview_label_watermarked.setText(f"水印预览出错: {e}")

    def closeEvent(self, event):
        clear_tmp_folder()
        super().closeEvent(event)


# 拖拽支持的自定义QListWidget
class DraggableListWidget(QListWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            files = []
            exts = (".jpg", ".jpeg", ".png", ".bmp", ".tiff")
            for url in event.mimeData().urls():
                path = url.toLocalFile()
                if os.path.isfile(path) and path.lower().endswith(exts):
                    files.append(path)
            if files:
                self.main_window.add_images(files)
            event.acceptProposedAction()
        else:
            event.ignore()


def clear_tmp_folder():
    tmp_dir = os.path.join(os.getcwd(), "tmp")
    if os.path.exists(tmp_dir):
        import shutil
        try:
            shutil.rmtree(tmp_dir)
        except Exception:
            pass
