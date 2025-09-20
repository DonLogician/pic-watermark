import os
from PIL import Image, ExifTags


def get_image_exif_data(image_path):
    """
    从图片中提取EXIF信息
    
    Args:
        image_path: 图片文件路径
        
    Returns:
        dict: 包含EXIF信息的字典
    """
    try:
        image = Image.open(image_path)
        exif_data = {}
        # 尝试获取EXIF数据
        if hasattr(image, '_getexif'):
            exif = image._getexif()
            if exif:
                for tag, value in exif.items():
                    tag_name = ExifTags.TAGS.get(tag, tag)
                    exif_data[tag_name] = value
        return exif_data
    except Exception as e:
        print(f"获取EXIF信息时出错: {e}")
        return {}


def get_photo_datetime(exif_data):
    """
    从EXIF数据中提取拍摄日期时间
    
    Args:
        exif_data: 包含EXIF信息的字典
        
    Returns:
        str: 格式化的日期字符串 (YYYY-MM-DD)，如果无法提取则返回None
    """
    # 常见的日期时间标签
    datetime_tags = ['DateTimeOriginal', 'DateTime', 'DateTimeDigitized']
    
    for tag in datetime_tags:
        if tag in exif_data:
            datetime_str = exif_data[tag]
            # 通常EXIF日期格式为 'YYYY:MM:DD HH:MM:SS'
            if isinstance(datetime_str, str) and ':' in datetime_str:
                # 提取年月日部分
                try:
                    date_part = datetime_str.split(' ')[0]
                    # 将格式从YYYY:MM:DD转换为YYYY-MM-DD
                    return date_part.replace(':', '-')
                except Exception as e:
                    print(f"解析日期时间时出错: {e}")
    
    return None