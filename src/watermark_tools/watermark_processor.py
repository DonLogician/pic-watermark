import os
from PIL import Image, ImageDraw, ImageFont
from .config import DEFAULT_FONT_SIZE, DEFAULT_WATERMARK_POSITION, DEFAULT_WATERMARK_COLOR


def add_watermark_to_image(image_path, watermark_text, output_path, position=None, font_size=None, color=None):
    """
    在图片上添加水印
    
    Args:
        image_path: 输入图片路径
        watermark_text: 水印文本
        output_path: 输出图片路径
        position: 水印位置，可选值: top-left, center, bottom-right
        font_size: 字体大小
        color: 水印颜色
        
    Returns:
        bool: 是否成功添加水印
    """
    try:
        # 打开图片
        image = Image.open(image_path).convert('RGBA')
        width, height = image.size
        
        # 创建一个可以在图像上绘图的对象
        draw = ImageDraw.Draw(image)
        
        # 设置字体大小，使用传入的值或默认值
        font_size_val = font_size if font_size is not None else DEFAULT_FONT_SIZE
        
        # 设置字体，尝试使用系统字体或默认字体
        try:
            # 尝试使用中文字体
            font = ImageFont.truetype("simhei.ttf", font_size_val)
        except IOError:
            # 如果没有指定字体，使用默认字体
            font = ImageFont.load_default()
        
        # 设置水印颜色，使用传入的值或默认值
        color_val = color if color is not None else DEFAULT_WATERMARK_COLOR
        
        # 设置水印位置
        if position is None or position.lower() == 'top-left':
            # 左上角
            position_val = DEFAULT_WATERMARK_POSITION
        elif position.lower() == 'center':
            # 中央位置
            # 获取文本尺寸 - 使用textbbox替代textsize
            bbox = draw.textbbox((0, 0), watermark_text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            position_val = ((width - text_width) // 2, (height - text_height) // 2)
        elif position.lower() == 'bottom-right':
            # 右下角
            # 获取文本尺寸 - 使用textbbox替代textsize
            bbox = draw.textbbox((0, 0), watermark_text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            position_val = (width - text_width - 10, height - text_height - 10)
        else:
            # 默认左上角
            position_val = DEFAULT_WATERMARK_POSITION
        
        # 添加水印文本
        draw.text(position_val, watermark_text, font=font, fill=color_val)
        
        # 保存处理后的图片
        # 获取输出文件扩展名并转换为小写
        _, extension = os.path.splitext(output_path)
        extension = extension.lower()
        
        # 检查是否为JPEG格式，如果是则转换为RGB模式
        if extension in ['.jpg', '.jpeg']:
            # JPEG不支持透明度，需要转换为RGB模式
            image = image.convert('RGB')
            image.save(output_path, 'JPEG')
        elif extension == '.png':
            # PNG支持透明度，保持RGBA模式
            image.save(output_path, 'PNG')
        else:
            # 其他格式，使用默认保存方式
            image.save(output_path)
        
        print(f"已成功添加水印并保存到: {output_path}")
        return True
    except Exception as e:
        print(f"添加水印时出错: {e}")
        return False