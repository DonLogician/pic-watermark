import os
from .config import SUPPORTED_FORMATS


def check_file_exists(file_path):
    """
    检查文件是否存在
    
    Args:
        file_path: 文件路径
        
    Returns:
        bool: 文件是否存在
    """
    if not os.path.exists(file_path):
        print(f"错误: 文件 '{file_path}' 不存在")
        return False
    return True


def check_watermark_suffix(file_path):
    """
    检查文件名是否已经以_watermark结尾
    
    Args:
        file_path: 文件路径
        
    Returns:
        bool: 如果文件名已经以_watermark结尾则返回True，否则返回False
    """
    base_name, _ = os.path.splitext(file_path)
    # 检查基础文件名是否以_watermark结尾
    if base_name.lower().endswith('_watermark'):
        print(f"警告: 文件 '{file_path}' 已以_watermark结尾，跳过处理")
        return True
    return False


def check_supported_format(file_path):
    """
    检查文件格式是否支持
    
    Args:
        file_path: 文件路径
        
    Returns:
        bool: 文件格式是否支持
    """
    _, extension = os.path.splitext(file_path)
    extension = extension.lower()
    
    if extension not in SUPPORTED_FORMATS:
        print(f"错误: 不支持的文件格式 '{extension}'。目前仅支持: {', '.join(SUPPORTED_FORMATS)}")
        return False
    return True