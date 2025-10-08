import os
from PIL import Image, ImageDraw, ImageFont
from .config import DEFAULT_FONT_SIZE, DEFAULT_WATERMARK_POSITION, DEFAULT_WATERMARK_COLOR


import re
import os

def add_watermark_to_image(image_path, watermark_text, output_path, position=None, font_size=None, color=None, transparency=None, extension=None):
    """
    在图片上添加水印
    
    Args:
        image_path: 输入图片路径
        watermark_text: 水印文本
        output_path: 输出图片路径
        position: 水印位置，可选值: top-left, center, bottom-right 或 (rel_x, rel_y) 相对坐标元组
        font_size: 字体大小
        color: 水印颜色
        transparency: 水印透明度 (0-100)，100代表完全透明
        extension: 导出格式扩展名（如 'jpg', 'png'），优先使用此参数
        
    Returns:
        bool: 是否成功添加水印
    """
    try:
        # 打开图片
        image = Image.open(image_path).convert('RGBA')
        width, height = image.size
        
        # 设置字体大小，使用传入的值或默认值
        font_size_val = font_size if font_size is not None else DEFAULT_FONT_SIZE
        
        # 设置字体，尝试使用系统字体或默认字体
        try:
            # 尝试使用中文字体 - 根据操作系统尝试不同的字体路径
            if os.name == 'nt':  # Windows
                font = ImageFont.truetype("simhei.ttf", font_size_val)
            else:  # macOS/Linux
                font = ImageFont.truetype("WenQuanYi Micro Hei", font_size_val)
        except IOError:
            try:
                # 尝试其他常见中文字体
                font = ImageFont.truetype("Arial Unicode MS", font_size_val)
            except IOError:
                # 如果没有指定字体，使用默认字体
                font = ImageFont.load_default()
        
        # 设置水印颜色，使用传入的值或默认值
        color_val = color if color is not None else DEFAULT_WATERMARK_COLOR
        
        # 处理颜色格式，支持十六进制颜色码转RGB
        if isinstance(color_val, str) and color_val.startswith('#'):
            # 移除#号
            color_hex = color_val.lstrip('#')
            # 将十六进制颜色码转换为RGB元组
            try:
                r = int(color_hex[0:2], 16)
                g = int(color_hex[2:4], 16)
                b = int(color_hex[4:6], 16)
                color_val = (r, g, b)
            except ValueError:
                # 如果转换失败，使用默认颜色
                color_val = DEFAULT_WATERMARK_COLOR
        
        # 确保color_val是RGB元组（不含alpha通道）
        if isinstance(color_val, tuple) and len(color_val) == 4:
            color_val = color_val[:3]  # 只保留RGB部分
        
        # 创建临时draw对象来计算文本尺寸
        temp_img = Image.new('RGBA', (1, 1), (0, 0, 0, 0))
        temp_draw = ImageDraw.Draw(temp_img)
        # 获取文本尺寸 - 使用textbbox替代textsize
        bbox = temp_draw.textbbox((0, 0), watermark_text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        # 设置水印位置
        margin = 10  # 边距
        if isinstance(position, tuple) and len(position) == 2 and all(isinstance(p, float) for p in position):
            # 如果是相对坐标元组 (rel_x, rel_y)，计算实际像素位置
            rel_x, rel_y = position
            # 确保坐标在有效范围内 (0-1)
            rel_x = max(0, min(1, rel_x))
            rel_y = max(0, min(1, rel_y))
            # 计算实际像素位置（考虑文本大小，使文本中心位于指定坐标）
            x = int(rel_x * width - text_width / 2)
            y = int(rel_y * height - text_height / 2)
            # 确保位置在图片范围内
            x = max(0, min(x, width - text_width))
            y = max(0, min(y, height - text_height))
            position_val = (x, y)
        elif position is None or (isinstance(position, str) and position.lower() == 'top-left'):
            # 左上角
            position_val = (margin, margin)
        elif isinstance(position, str) and position.lower() == 'top-right':
            # 右上角
            position_val = (width - text_width - margin, margin)
        elif isinstance(position, str) and position.lower() == 'center':
            # 中央位置
            position_val = ((width - text_width) // 2, (height - text_height) // 2)
        elif isinstance(position, str) and position.lower() == 'bottom-left':
            # 左下角
            position_val = (margin, height - text_height - margin)
        elif isinstance(position, str) and position.lower() == 'bottom-right':
            # 右下角
            position_val = (width - text_width - margin, height - text_height - margin)
        else:
            # 默认左上角
            position_val = DEFAULT_WATERMARK_POSITION
        
        # 1. 创建一个和原图一样大的透明图层（rgba全为0）
        watermark_layer = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        
        # 2. 在透明图层上，只以rgb绘制水印文字
        draw_watermark = ImageDraw.Draw(watermark_layer)
        draw_watermark.text(position_val, watermark_text, font=font, fill=color_val)
        
        # 3. 调整水印图层的不透明度
        if transparency is not None:
            # 确保透明度在有效范围内
            transparency_val = max(0, min(100, transparency))
            # 计算透明度因子（100代表完全透明，0代表完全不透明）
            alpha_factor = (100 - transparency_val) / 100.0
            
            # 创建一个新的图层来保存调整后的透明度
            adjusted_watermark = Image.new('RGBA', (width, height), (0, 0, 0, 0))
            for x in range(width):
                for y in range(height):
                    r, g, b, a = watermark_layer.getpixel((x, y))
                    # 如果该像素不是透明的（即有文字的部分）
                    if a > 0:
                        # 调整透明度
                        new_alpha = int(a * alpha_factor)
                        # 保持RGB值不变，只调整alpha通道
                        adjusted_watermark.putpixel((x, y), (r, g, b, new_alpha))
            
            watermark_layer = adjusted_watermark
        
        # 4. 将水印图层与原图合并
        result = Image.alpha_composite(image, watermark_layer)
        
        # 保存处理后的图片
        # 优先使用传入的extension参数，如果没有则从文件路径获取
        if extension:
            output_format = extension.lower()
        else:
            # 从文件路径获取扩展名并转换为小写
            _, output_format = os.path.splitext(output_path)
            output_format = output_format.lower()
            # 去除可能的点号前缀
            if output_format.startswith('.'):
                output_format = output_format[1:]
        
        # 检查是否为JPEG格式，如果是则转换为RGB模式
        if output_format in ['jpg', 'jpeg']:
            # JPEG不支持透明度，需要转换为RGB模式
            result = result.convert('RGB')
            result.save(output_path, 'JPEG')
        elif output_format == 'png':
            # PNG支持透明度，保持RGBA模式
            result.save(output_path, 'PNG')
        else:
            # 其他格式，使用默认保存方式
            result.save(output_path)
        
        print(f"已成功添加水印并保存到: {output_path}")
        return True
    except Exception as e:
        print(f"添加水印时出错: {e}")
        return False