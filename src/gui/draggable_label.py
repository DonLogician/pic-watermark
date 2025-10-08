from PyQt5.QtWidgets import QLabel
from PyQt5.QtCore import Qt, QPoint

class DraggableWatermarkLabel(QLabel):
    """
    支持拖拽功能的水印预览标签类
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.dragging = False
        self.drag_start_position = QPoint()
        self.watermark_offset = QPoint()
        self.setAlignment(Qt.AlignCenter)
        self.setCursor(Qt.OpenHandCursor)
        
    def mousePressEvent(self, event):
        """
        鼠标按下事件，开始拖拽
        """
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.drag_start_position = event.pos()
            self.setCursor(Qt.ClosedHandCursor)
        super().mousePressEvent(event)
    
    def mouseMoveEvent(self, event):
        """
        鼠标移动事件，处理拖拽
        """
        if not self.dragging:
            super().mouseMoveEvent(event)
            return
        
        # 计算拖拽偏移量
        delta = event.pos() - self.drag_start_position
        
        # 如果标签有图片（水印预览）且父窗口是MainWindow
        if hasattr(self.parent, 'watermark_position') and hasattr(self.parent, 'image_paths') and self.parent.image_paths:
            # 确保当前有选中的图片
            selected = self.parent.list_widget.currentRow()
            if selected < 0 or selected >= len(self.parent.image_paths):
                super().mouseMoveEvent(event)
                return
            
            # 计算实际图片上的相对位置
            from PIL import Image
            img_path = self.parent.image_paths[selected]
            try:
                image = Image.open(img_path)
                img_width, img_height = image.size
                
                # 获取标签的尺寸和图片在标签中的缩放比例
                label_width = self.width()
                label_height = self.height()
                
                # 计算图片在标签中的实际显示区域（考虑保持比例）
                scale = min(label_width / img_width, label_height / img_height)
                display_width = int(img_width * scale)
                display_height = int(img_height * scale)
                display_x = (label_width - display_width) // 2
                display_y = (label_height - display_height) // 2
                
                # 检查鼠标是否在图片显示区域内
                mouse_x, mouse_y = event.pos().x(), event.pos().y()
                if (display_x <= mouse_x < display_x + display_width and 
                    display_y <= mouse_y < display_y + display_height):
                    
                    # 计算在原始图片上的相对位置
                    rel_x = (mouse_x - display_x) / display_width
                    rel_y = (mouse_y - display_y) / display_height
                    
                    # 设置精确的坐标位置
                    self.parent.watermark_position = (rel_x, rel_y)
                    print(f"水印位置已调整: {self.parent.watermark_position}")
                    
                    # 实时更新预览（可选，为了性能可以不更新）
                    # self.parent.show_preview()
            except Exception as e:
                print(f"计算水印位置时出错: {e}")
        
        super().mouseMoveEvent(event)
    
    def mouseReleaseEvent(self, event):
        """
        鼠标释放事件，结束拖拽
        """
        if event.button() == Qt.LeftButton and self.dragging:
            self.dragging = False
            self.setCursor(Qt.OpenHandCursor)
            # 鼠标释放后更新预览
            if hasattr(self.parent, 'show_preview'):
                self.parent.show_preview()
        super().mouseReleaseEvent(event)