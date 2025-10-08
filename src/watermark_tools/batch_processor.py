# 批量导出图片列表
def batch_export_images(
    image_paths,
    position=None,
    font_size=None,
    color=None,
    watermark_text=None,
    opacity=None,
    output_format="JPEG",
    output_dir=None,
    prefix="",
    suffix="",
    naming_rule=0
):
    if not image_paths:
        print("未选择图片")
        return 0
    # 如果用户指定了导出目录，则使用，否则保持原有逻辑
    if output_dir:
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
    else:
        first_dir = os.path.dirname(image_paths[0]) if image_paths else os.getcwd()
        output_dir = create_output_directory(first_dir)
        if not output_dir:
            return 0
    success_count = 0
    for file_path in image_paths:
        if check_supported_format(file_path):
            # 生成自定义文件名
            file_name = os.path.basename(file_path)
            base_name, extension = os.path.splitext(file_name)
            ext_map = {"JPEG": ".jpeg", "PNG": ".png"}
            out_ext = ext_map.get(output_format.upper(), extension)
            if naming_rule == 1 and prefix:
                output_file_name = f"{prefix}{base_name}{out_ext}"
            elif naming_rule == 2 and suffix:
                output_file_name = f"{base_name}{suffix}{out_ext}"
            else:
                output_file_name = f"{base_name}{out_ext}"
            output_file = os.path.join(output_dir, output_file_name)
            if process_single_file(
                file_path,
                output_file,
                position,
                font_size,
                color,
                output_format,
                watermark_text=watermark_text,
                transparency=transparency
            ):
                success_count += 1
    print(f"批量导出完成，成功处理了 {success_count} 个文件，输出目录: {output_dir}")
    return success_count


import os
import sys
from .config import SUPPORTED_FORMATS
from .file_handler import (
    check_file_exists,
    check_supported_format,
    check_watermark_suffix,
)
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


def process_directory(input_dir, position=None, font_size=None, color=None):
    """
    处理目录中的所有支持的图片文件

    Args:
        input_dir: 输入目录路径
        position: 水印位置
        font_size: 字体大小
        color: 水印颜色

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
        files = [
            f
            for f in os.listdir(input_dir)
            if os.path.isfile(os.path.join(input_dir, f))
        ]

        for file in files:
            # 构建完整的文件路径
            file_path = os.path.join(input_dir, file)

            # 检查文件格式是否支持
            if not check_supported_format(file_path):
                continue

            # 处理单个文件，传递自定义参数
            if process_single_file(
                file_path,
                output_dir,
                input_dir,
                position,
                font_size,
                color,
                output_format="JPEG",
            ):
                success_count += 1
    except Exception as e:
        print(f"遍历目录文件时出错: {e}")

    return success_count


def process_single_file(
    file_path,
    output_file,
    position=None,
    font_size=None,
    color=None,
    output_format="JPEG",
    watermark_text=None,
    transparency=None
):
    """
    处理单个图片文件

    Args:
        file_path: 输入文件路径
        output_file: 输出文件完整路径
        position: 水印位置
        font_size: 字体大小
        color: 水印颜色

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
            print(
                f"警告: 无法从图片 '{file_path}' 中提取拍摄日期，使用当前日期作为替代"
            )
            from datetime import datetime

            photo_date = datetime.now().strftime("%Y-%m-%d")

        # 如果提供了自定义水印文本，则使用它，否则使用日期
        final_watermark_text = watermark_text if watermark_text else photo_date
        
        # 添加水印，传递所有自定义参数
        # 将output_format转换为小写的扩展名格式
        extension = output_format.lower() if output_format else None
        return add_watermark_to_image(
            file_path, 
            final_watermark_text, 
            output_file, 
            position, 
            font_size, 
            color,
            transparency=transparency,
            extension=extension
        )
    except Exception as e:
        print(f"处理文件 '{file_path}' 时出错: {e}")
        return False
