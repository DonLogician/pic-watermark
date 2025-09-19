#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
图片水印工具 - 主程序入口
"""
from watermark_tools import (
    get_image_exif_data,
    get_photo_datetime,
    add_watermark_to_image,
    check_file_exists,
    check_supported_format,
    prepare_output_path
)


def main():
    """
    主函数 - 程序入口点
    """
    # 输入文件路径
    input_file = "test.jpg"
    
    # 检查文件是否存在
    if not check_file_exists(input_file):
        return
    
    # 检查文件格式是否支持
    if not check_supported_format(input_file):
        return
    
    # 获取EXIF数据
    exif_data = get_image_exif_data(input_file)
    
    # 获取拍摄日期
    photo_date = get_photo_datetime(exif_data)
    
    if not photo_date:
        print("警告: 无法从图片中提取拍摄日期，使用当前日期作为替代")
        from datetime import datetime
        photo_date = datetime.now().strftime("%Y-%m-%d")
    
    # 准备输出文件路径
    output_file = prepare_output_path(input_file)
    
    # 添加水印
    add_watermark_to_image(input_file, photo_date, output_file)


if __name__ == "__main__":
    main()