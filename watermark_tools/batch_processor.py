import os
import sys
from .config import SUPPORTED_FORMATS
from .file_handler import check_file_exists, check_supported_format, check_watermark_suffix
from .exif_utils import get_image_exif_data, get_photo_datetime
from .watermark_processor import add_watermark_to_image


def create_output_directory(input_dir):
    """
    创建输出目录
    
    Args:
        input_dir: 输入目录路径
        
    Returns:
        str: 输出目录路径
    """
    # 获取目录名
    dir_name = os.path.basename(input_dir)
    if not dir_name:
        # 如果输入是根目录，使用当前工作目录的名称
        dir_name = os.path.basename(os.getcwd())
        
    # 构建输出目录路径 - 在输入目录下创建_watermark文件夹
    output_dir = os.path.join(input_dir, f"{dir_name}_watermark")
    
    # 创建目录（如果不存在）
    if not os.path.exists(output_dir):
        try:
            os.makedirs(output_dir)
            print(f"已创建输出目录: {output_dir}")
        except Exception as e:
            print(f"创建输出目录时出错: {e}")
            return None
    
    return output_dir


def process_directory(input_dir):
    """
    处理目录中的所有支持的图片文件
    
    Args:
        input_dir: 输入目录路径
        
    Returns:
        int: 成功处理的文件数量
    """
    # 检查目录是否存在
    if not os.path.isdir(input_dir):
        print(f"错误: '{input_dir}' 不是一个有效的目录")
        return 0
    
    # 创建输出目录
    output_dir = create_output_directory(input_dir)
    if not output_dir:
        return 0
    
    # 只处理当前目录中的文件（不递归处理子目录）
    success_count = 0
    try:
        # 获取当前目录中的所有文件
        files = [f for f in os.listdir(input_dir) if os.path.isfile(os.path.join(input_dir, f))]
        
        for file in files:
            # 构建完整的文件路径
            file_path = os.path.join(input_dir, file)
            
            # 检查文件格式是否支持
            if not check_supported_format(file_path):
                continue
            
            # 处理单个文件
            if process_single_file(file_path, output_dir, input_dir):
                success_count += 1
    except Exception as e:
        print(f"遍历目录文件时出错: {e}")
    
    return success_count


def process_single_file(file_path, output_dir, input_dir):
    """
    处理单个图片文件
    
    Args:
        file_path: 输入文件路径
        output_dir: 输出目录路径
        input_dir: 输入目录路径
        
    Returns:
        bool: 是否成功处理
    """
    # 检查文件是否存在
    if not check_file_exists(file_path):
        return False
    
    # 检查文件名是否已经以_watermark结尾
    if check_watermark_suffix(file_path):
        return False
    
    try:
        # 获取EXIF数据
        exif_data = get_image_exif_data(file_path)
        
        # 获取拍摄日期
        photo_date = get_photo_datetime(exif_data)
        
        if not photo_date:
            print(f"警告: 无法从图片 '{file_path}' 中提取拍摄日期，使用当前日期作为替代")
            from datetime import datetime
            photo_date = datetime.now().strftime("%Y-%m-%d")
        
        # 构建输出文件路径 - 在文件名后添加_watermark后缀
        file_name = os.path.basename(file_path)
        base_name, extension = os.path.splitext(file_name)
        output_file_name = f"{base_name}_watermark{extension}"
        output_file = os.path.join(output_dir, output_file_name)
        
        # 添加水印
        return add_watermark_to_image(file_path, photo_date, output_file)
    except Exception as e:
        print(f"处理文件 '{file_path}' 时出错: {e}")
        return False