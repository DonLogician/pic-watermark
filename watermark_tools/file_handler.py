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


def prepare_output_path(input_file_path):
    """
    准备输出文件路径
    
    Args:
        input_file_path: 输入文件路径
        
    Returns:
        str: 输出文件路径
    """
    base_name, extension = os.path.splitext(input_file_path)
    output_file = f"{base_name}_watermark{extension}"
    return output_file