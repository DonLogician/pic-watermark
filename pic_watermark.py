#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
图片水印工具 - 主程序入口
"""
import os
import sys
import argparse
from src.watermark_tools import (
    get_image_exif_data,
    get_photo_datetime,
    add_watermark_to_image,
    check_file_exists,
    check_supported_format,
    check_watermark_suffix,
    process_directory,
)


def show_usage():
    """
    显示程序使用方式
    """
    print("图片水印工具使用方式:")
    print(
        f"  python {os.path.basename(sys.argv[0])} <文件或目录路径> [-p position] [-s font_size] [-c color]"
    )
    print("\n可选参数:")
    print("  -p position    设置水印位置: top-left(默认), center, bottom-right")
    print("  -s font_size   设置水印字体大小(默认: 24)")
    print("  -c color       设置水印颜色，如 red 或 #FF0000(默认: 白色)")
    print("\n功能说明:")
    print("  - 如果提供单个图片文件路径，将为该图片添加水印并保存")
    print("  - 如果提供目录路径，将批量处理目录中的所有支持的图片文件")
    print("  - 支持的图片格式: jpg, jpeg, png")
    print("  - 处理后的图片将保存到与原目录同名的'原目录名_watermark'文件夹中")


def process_single_file(input_file, position=None, font_size=None, color=None):
    """
    处理单个图片文件

    Args:
        input_file: 输入文件路径
        position: 水印位置
        font_size: 字体大小
        color: 水印颜色
    """
    # 检查文件是否存在
    if not check_file_exists(input_file):
        return False

    # 检查文件名是否已经以_watermark结尾
    if check_watermark_suffix(input_file):
        return False

    # 检查文件格式是否支持
    if not check_supported_format(input_file):
        return False

    # 获取EXIF数据
    exif_data = get_image_exif_data(input_file)

    # 获取拍摄日期
    photo_date = get_photo_datetime(exif_data)

    if not photo_date:
        print(f"警告: 无法从图片 '{input_file}' 中提取拍摄日期，使用当前日期作为替代")
        from datetime import datetime

        photo_date = datetime.now().strftime("%Y-%m-%d")

    # 准备输出文件路径 - 在输入文件所在目录下创建同名_watermark子目录
    file_dir = os.path.dirname(input_file)
    dir_name = os.path.basename(file_dir) if file_dir else os.path.basename(os.getcwd())
    output_dir = os.path.join(file_dir, f"{dir_name}_watermark")

    # 创建输出目录（如果不存在）
    if not os.path.exists(output_dir):
        try:
            os.makedirs(output_dir)
        except Exception as e:
            print(f"创建输出目录时出错: {e}")
            return False

    # 构建输出文件路径 - 在文件名后添加_watermark后缀
    file_name = os.path.basename(input_file)
    base_name, extension = os.path.splitext(file_name)
    output_file_name = f"{base_name}_watermark{extension}"
    output_file = os.path.join(output_dir, output_file_name)

    # 添加水印，传递自定义参数
    return add_watermark_to_image(
        input_file, photo_date, output_file, position, font_size, color
    )


def main():
    """
    主函数 - 程序入口点
    """
    # 创建命令行参数解析器
    parser = argparse.ArgumentParser(description="图片水印工具")
    parser.add_argument("input_path", help="输入文件或目录路径")
    parser.add_argument(
        "-p",
        "--position",
        choices=["top-left", "center", "bottom-right"],
        default="top-left",
        help="水印位置 (默认: top-left)",
    )
    parser.add_argument(
        "-s", "--font-size", type=int, default=24, help="字体大小 (默认: 24)"
    )
    parser.add_argument("-c", "--color", default="white", help="水印颜色 (默认: white)")

    # 解析命令行参数
    args = parser.parse_args()

    # 获取输入路径和自定义参数
    input_path = args.input_path
    position = args.position
    font_size = args.font_size
    color = args.color

    # 检查输入路径是否存在
    if not os.path.exists(input_path):
        print(f"错误: 路径 '{input_path}' 不存在")
        return

    # 判断是文件还是目录
    if os.path.isfile(input_path):
        # 处理单个文件
        process_single_file(input_path, position, font_size, color)
    else:
        # 处理目录中的所有文件
        success_count = process_directory(input_path, position, font_size, color)
        print(f"批量处理完成，成功处理了 {success_count} 个文件")


if __name__ == "__main__":
    import sys

    if len(sys.argv) == 1:
        # 无参数时启动GUI
        from src.gui.main_window import MainWindow
        from PyQt5.QtWidgets import QApplication

        app = QApplication(sys.argv)
        window = MainWindow()
        window.show()
        sys.exit(app.exec_())
    else:
        # 有参数时走命令行逻辑
        main()
