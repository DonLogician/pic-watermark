import sys
import os
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QListWidget,
    QFileDialog,
    QLabel,
    QListWidgetItem,
    QFrame,
    QSizePolicy,
    QComboBox,
    QLineEdit,
)
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import QSize, Qt


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
        super().__init__()
        self.setWindowTitle("图片水印工具")
        self.resize(1200, 900)
        # 移除多余的PyQt5控件导入，全部在文件顶部统一导入

        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)
        # 左侧 sidebar
        sidebar_left = QFrame()
        sidebar_left.setFrameShape(QFrame.StyledPanel)
        sidebar_left.setFixedWidth(300)
        sidebar_left_layout = QVBoxLayout(sidebar_left)
        self.btn_select_images = QPushButton("选择图片")
        self.btn_select_images.clicked.connect(self.select_images)
        sidebar_left_layout.addWidget(self.btn_select_images)
        self.btn_add_images = QPushButton("添加图片")
        self.btn_add_images.clicked.connect(self.add_images_dialog)
        sidebar_left_layout.addWidget(self.btn_add_images)
        self.btn_select_folder = QPushButton("选择文件夹")
        self.btn_select_folder.clicked.connect(self.select_folder)
        sidebar_left_layout.addWidget(self.btn_select_folder)
        self.list_widget = DraggableListWidget(self)
        self.list_widget.setIconSize(QSize(128, 128))
        self.list_widget.setMinimumHeight(400)
        self.list_widget.itemSelectionChanged.connect(self.show_preview)
        sidebar_left_layout.addWidget(self.list_widget)
        sidebar_left_layout.addStretch()
        main_layout.addWidget(sidebar_left)

        # 中间预览区（上下两部分）
        preview_frame = QFrame()
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

        # 右侧 sidebar（导出设置入口）
        self.sidebar_right = QFrame()
        self.sidebar_right.setFrameShape(QFrame.StyledPanel)
        self.sidebar_right.setFixedWidth(300)
        self.sidebar_right_layout = QVBoxLayout(self.sidebar_right)
        self.btn_export_settings = QPushButton("导出设置")
        self.btn_export_settings.setStyleSheet("font-size:16px;")
        self.btn_export_settings.clicked.connect(self.show_export_settings_sidebar)
        self.sidebar_right_layout.addSpacing(40)
        self.sidebar_right_layout.addWidget(self.btn_export_settings)
        # 导出按钮，主窗口右下角
        self.export_btn = QPushButton("导出", self)
        self.export_btn.setFixedSize(120, 40)
        self.export_btn.setStyleSheet("font-size:18px;")
        self.export_btn.clicked.connect(self.export_images)
        self.export_btn.show()
        self._move_export_btn()
        self.sidebar_right_layout.addStretch()
        main_layout.addWidget(self.sidebar_right)

        # 新sidebar（导出设置界面）
        self.sidebar_export_settings = QFrame()
        self.sidebar_export_settings.setFrameShape(QFrame.StyledPanel)
        self.sidebar_export_settings.setFixedWidth(300)
        self.sidebar_export_settings_layout = QVBoxLayout(self.sidebar_export_settings)
        # 返回按钮
        self.btn_back = QPushButton("返回")
        self.btn_back.setStyleSheet("font-size:16px;")
        self.btn_back.clicked.connect(self.show_main_sidebar)
        self.sidebar_export_settings_layout.addWidget(self.btn_back)
        self.sidebar_export_settings_layout.addSpacing(20)
        # 导出格式选择
        export_format_label = QLabel("导出格式：")
        export_format_label.setStyleSheet("font-size:16px;")
        self.sidebar_export_settings_layout.addWidget(export_format_label)
        self.format_combo = QComboBox()
        self.format_combo.addItems(["JPEG", "PNG"])
        self.format_combo.setCurrentIndex(0)
        self.sidebar_export_settings_layout.addWidget(self.format_combo)
        # 导出路径选择
        export_path_label = QLabel("导出路径：")
        export_path_label.setStyleSheet("font-size:16px;")
        self.sidebar_export_settings_layout.addWidget(export_path_label)
        path_layout = QHBoxLayout()
        self.export_path_edit = QLineEdit()
        self.export_path_edit.setPlaceholderText("请选择导出文件夹")
        self.export_path_edit.setReadOnly(True)
        path_layout.addWidget(self.export_path_edit)
        self.btn_select_export_path = QPushButton("选择")
        self.btn_select_export_path.setFixedWidth(60)
        self.btn_select_export_path.clicked.connect(self.select_export_path)
        path_layout.addWidget(self.btn_select_export_path)
        self.sidebar_export_settings_layout.addLayout(path_layout)
        self.export_path = ""
        self.sidebar_export_settings_layout.addSpacing(40)
        self.sidebar_export_settings_layout.addStretch()
        self.sidebar_export_settings.hide()
        main_layout.addWidget(self.sidebar_export_settings)

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

    def show_main_sidebar(self):
        # 返回主sidebar
        self.sidebar_export_settings.hide()
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
            QMessageBox.information(self, "提示", "请先导入图片！")
            return
        if not self.export_path:
            QMessageBox.warning(self, "导出路径未设置", "请先选择导出文件夹！")
            return
        img_dirs = set(os.path.dirname(p) for p in self.image_paths)
        if self.export_path in img_dirs:
            QMessageBox.warning(
                self,
                "导出路径冲突",
                "导出路径不能与原图所在文件夹相同，否则可能覆盖原图！",
            )
            return
        # 获取用户选择的输出格式
        format_str = self.format_combo.currentText()
        # 传递给批量导出
        count = batch_export_images(
            self.image_paths, output_format=format_str, output_dir=self.export_path
        )
        if count:
            QMessageBox.information(self, "导出完成", f"成功导出 {count} 张图片。")
        else:
            QMessageBox.warning(
                self, "导出失败", "图片导出失败，请检查图片格式或权限。"
            )

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
