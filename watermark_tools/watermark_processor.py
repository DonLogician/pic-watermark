import os
from PIL import Image, ImageDraw, ImageFont
from .config import DEFAULT_FONT_SIZE, DEFAULT_WATERMARK_POSITION, DEFAULT_WATERMARK_COLOR


def add_watermark_to_image(image_path, watermark_text, output_path):
    """
    在图片左上角添加水印
    
    Args:
        image_path: 输入图片路径
        watermark_text: 水印文本
        output_path: 输出图片路径
        
    Returns:
        bool: 是否成功添加水印
    """
    try:
        # 打开图片
        image = Image.open(image_path).convert('RGBA')
        
        # 创建一个可以在图像上绘图的对象
        draw = ImageDraw.Draw(image)
        
        # 设置字体，尝试使用系统字体或默认字体
        try:
            # 尝试使用中文字体
            font = ImageFont.truetype("simhei.ttf", DEFAULT_FONT_SIZE)
        except IOError:
            # 如果没有指定字体，使用默认字体
            font = ImageFont.load_default()
        
        # 设置水印位置和颜色
        position = DEFAULT_WATERMARK_POSITION
        color = DEFAULT_WATERMARK_COLOR
        
        # 添加水印文本
        draw.text(position, watermark_text, font=font, fill=color)
        
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