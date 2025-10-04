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
)
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import QSize, Qt

# 引入拆分后的sidebar类
from src.gui.sidebars.main_sidebar import MainSidebar
from src.gui.sidebars.export_settings_sidebar import ExportSettingsSidebar
from src.gui.sidebars.watermark_settings_sidebar import WatermarkSettingsSidebar


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
        super().__init__()
        self.setWindowTitle("图片水印工具")
        self.resize(1200, 900)

        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)

        # 左侧 sidebar
        self.main_sidebar = MainSidebar(self)
        # 替换list_widget为DraggableListWidget
        self.main_sidebar.list_widget.setParent(None)
        self.list_widget = DraggableListWidget(self)
        self.list_widget.setIconSize(QSize(128, 128))
        self.list_widget.setMinimumHeight(400)
        self.main_sidebar.layout().insertWidget(3, self.list_widget)
        self.main_sidebar.list_widget = self.list_widget
        main_layout.addWidget(self.main_sidebar)

        # 信号连接
        self.main_sidebar.btn_select_images.clicked.connect(self.select_images)
        self.main_sidebar.btn_add_images.clicked.connect(self.add_images_dialog)
        self.main_sidebar.btn_select_folder.clicked.connect(self.select_folder)
        self.list_widget.itemSelectionChanged.connect(self.show_preview)

        # 中间预览区（上下两部分）
        preview_frame = QWidget()
        preview_layout = QVBoxLayout(preview_frame)
        self.preview_label_original = QLabel("原图预览区")
        self.preview_label_original.setAlignment(Qt.AlignCenter)
        self.preview_label_original.setStyleSheet(
            "background:#eee;border:1px solid #ccc;"
        )
        self.preview_label_original.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Expanding
        )
        preview_layout.addWidget(self.preview_label_original)
        self.preview_label_watermarked = QLabel("水印预览区")
        self.preview_label_watermarked.setAlignment(Qt.AlignCenter)
        self.preview_label_watermarked.setStyleSheet(
            "background:#f5f5f5;border:1px solid #ccc;"
        )
        self.preview_label_watermarked.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Expanding
        )
        preview_layout.addWidget(self.preview_label_watermarked)
        main_layout.addWidget(preview_frame)

        # 右侧 sidebar
        self.sidebar_right = QFrame()
        self.sidebar_right.setFrameShape(QFrame.StyledPanel)
        self.sidebar_right.setFixedWidth(300)
        sidebar_right_layout = QVBoxLayout(self.sidebar_right)
        self.btn_export_settings = QPushButton("导出设置")
        self.btn_export_settings.setStyleSheet("font-size:16px;")
        self.btn_export_settings.clicked.connect(self.show_export_settings_sidebar)
        sidebar_right_layout.addWidget(self.btn_export_settings)
        self.btn_watermark_settings = QPushButton("水印设置")
        self.btn_watermark_settings.setStyleSheet("font-size:16px;")
        sidebar_right_layout.addWidget(self.btn_watermark_settings)
        sidebar_right_layout.addStretch()
        main_layout.addWidget(self.sidebar_right)

        # 导出设置sidebar（初始隐藏）
        self.export_settings_sidebar = ExportSettingsSidebar(self)
        self.export_settings_sidebar.hide()
        main_layout.addWidget(self.export_settings_sidebar)
        # 绑定导出设置sidebar的返回按钮
        self.export_settings_sidebar.btn_back.clicked.connect(self.show_main_sidebar)

        # 导出按钮，主窗口右下角始终显示
        self.export_btn = QPushButton("导出", self)
        self.export_btn.setFixedSize(120, 40)
        self.export_btn.setStyleSheet("font-size:18px;")
        self.export_btn.clicked.connect(self.export_images)
        self.export_btn.show()
        self._move_export_btn()

        # 连接导出设置信号
        self.export_settings_sidebar.export_settings_changed.connect(
            self.handle_export_settings_change
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
                    self.export_settings_sidebar.export_path_edit.clear()
                    self.export_path = ""
                else:
                    self.export_path = export_path

        # 更新其他导出设置
        self.export_format = format
        self.export_prefix = prefix
        self.export_suffix = suffix
        self.export_naming_rule = (
            self.export_settings_sidebar.naming_rule_combo.currentIndex()
        )
        print(
            f"导出设置更新: 格式={format}, 前缀={prefix}, 后缀={suffix}, 路径={export_path}"
        )

    def show_watermark_settings_sidebar(self):
        # 切换到水印设置sidebar
        self.sidebar_right.hide()
        self.sidebar_watermark_settings.show()

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
        self.export_settings_sidebar.show()

    def show_main_sidebar(self):
        # 返回主sidebar
        self.export_settings_sidebar.hide()
        # self.watermark_settings_sidebar.hide()
        self.sidebar_right.show()

    # ...existing code...

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, "export_btn") and self.export_btn:
            self._move_export_btn()

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
        if self.export_path in img_dirs and not (self.export_prefix or self.export_suffix):
            QMessageBox.warning(self, "警告", "导出路径不能与图片所在文件夹相同！")
            return

        count = batch_export_images(
            self.image_paths,
            output_format=self.export_format,
            output_dir=self.export_path,
            prefix=self.export_prefix,
            suffix=self.export_suffix,
            naming_rule=self.export_naming_rule
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
            self.preview_label_original.clear()
            self.preview_label_original.setText("原图预览区")
            self.preview_label_watermarked.clear()
            self.preview_label_watermarked.setText("水印预览区")
            return
        img_path = self.image_paths[selected]
        # 原图预览
        pixmap = QPixmap(img_path)
        if not pixmap.isNull():
            w = self.preview_label_original.width()
            h = self.preview_label_original.height()
            scaled = pixmap.scaled(w, h, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.preview_label_original.setPixmap(scaled)
        else:
            self.preview_label_original.setText("无法加载图片")

        # 水印预览，文件存储到tmp文件夹
        try:
            from src.watermark_tools.watermark_processor import add_watermark_to_image

            watermark_text = "预览水印"
            tmp_dir = os.path.join(os.getcwd(), "tmp")
            if not os.path.exists(tmp_dir):
                os.makedirs(tmp_dir)
            import uuid

            tmp_path = os.path.join(tmp_dir, f"preview_{uuid.uuid4().hex}.png")
            success = add_watermark_to_image(img_path, watermark_text, tmp_path)
            if success:
                pixmap_wm = QPixmap(tmp_path)
                if not pixmap_wm.isNull():
                    w = self.preview_label_watermarked.width()
                    h = self.preview_label_watermarked.height()
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
