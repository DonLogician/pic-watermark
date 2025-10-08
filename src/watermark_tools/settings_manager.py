import os
import json
import shutil
from src.watermark_tools.config import (
    DEFAULT_WATERMARK_TEXT,
    DEFAULT_WATERMARK_TRANSPARENCY,
    DEFAULT_WATERMARK_COLOR,
    DEFAULT_FONT_SIZE,
    DEFAULT_WATERMARK_POSITION
)

# 当前工作目录
CURRENT_DIR = os.getcwd()
# 模板文件夹路径
TEMPLATES_DIR = os.path.join(CURRENT_DIR, 'templates')
# 上次设置文件路径
LAST_SETTINGS_FILE = os.path.join(CURRENT_DIR, '.last_settings.json')


def init_user_settings():
    """初始化用户设置目录"""
    if not os.path.exists(TEMPLATES_DIR):
        os.makedirs(TEMPLATES_DIR)


def save_watermark_template(name, settings):
    """
    保存水印设置为模板
    
    参数:
    name: 模板名称
    settings: 水印设置字典，包含text, transparency, color, font_size, position等字段
    
    返回:
    bool: 保存是否成功
    """
    try:
        init_user_settings()
        template_file = os.path.join(TEMPLATES_DIR, f'{name}.json')
        with open(template_file, 'w', encoding='utf-8') as f:
            json.dump(settings, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"保存模板失败: {e}")
        return False


def load_watermark_template(name):
    """
    加载水印模板
    
    参数:
    name: 模板名称
    
    返回:
    dict或None: 模板设置字典，加载失败则返回None
    """
    try:
        template_file = os.path.join(TEMPLATES_DIR, f'{name}.json')
        if not os.path.exists(template_file):
            return None
        with open(template_file, 'r', encoding='utf-8') as f:
            settings = json.load(f)
        return settings
    except Exception as e:
        print(f"加载模板失败: {e}")
        return None


def delete_watermark_template(name):
    """
    删除水印模板
    
    参数:
    name: 模板名称
    
    返回:
    bool: 删除是否成功
    """
    try:
        template_file = os.path.join(TEMPLATES_DIR, f'{name}.json')
        if os.path.exists(template_file):
            os.remove(template_file)
            return True
        return False
    except Exception as e:
        print(f"删除模板失败: {e}")
        return False


def get_available_templates():
    """
    获取所有可用的水印模板列表
    
    返回:
    list: 模板名称列表
    """
    try:
        init_user_settings()
        templates = []
        if os.path.exists(TEMPLATES_DIR):
            for file in os.listdir(TEMPLATES_DIR):
                if file.endswith('.json'):
                    templates.append(file[:-5])  # 移除.json扩展名
        return sorted(templates)
    except Exception as e:
        print(f"获取模板列表失败: {e}")
        return []


def save_last_settings(settings):
    """
    保存上次的设置，用于程序下次启动时自动加载
    
    参数:
    settings: 要保存的设置字典
    
    返回:
    bool: 保存是否成功
    """
    try:
        init_user_settings()
        # JSON默认会将元组转换为列表，所以不需要额外处理
        with open(LAST_SETTINGS_FILE, 'w', encoding='utf-8') as f:
            json.dump(settings, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"保存上次设置失败: {e}")
        return False


def load_last_settings():
    """
    加载上次的设置
    
    返回:
    dict: 上次的设置字典，如果不存在则返回默认设置
    """
    try:
        if os.path.exists(LAST_SETTINGS_FILE):
            with open(LAST_SETTINGS_FILE, 'r', encoding='utf-8') as f:
                settings = json.load(f)
            
            # 处理保存的设置键名，确保与main_window.py中的closeEvent方法一致
            # 兼容旧版本设置文件
            if 'watermark_text' in settings:
                # 旧版本的键名格式，转换为新版本的格式
                return {
                    'text': settings.get('watermark_text', DEFAULT_WATERMARK_TEXT),
                    'transparency': settings.get('watermark_transparency', DEFAULT_WATERMARK_TRANSPARENCY),
                    'color': settings.get('watermark_color', DEFAULT_WATERMARK_COLOR),
                    'font_size': settings.get('watermark_font_size', DEFAULT_FONT_SIZE),
                    'position': settings.get('watermark_position', DEFAULT_WATERMARK_POSITION)
                }
            return settings
        else:
            # 返回默认设置，使用与main_window.py一致的键名
            return {
                'text': DEFAULT_WATERMARK_TEXT,
                'transparency': DEFAULT_WATERMARK_TRANSPARENCY,
                'color': DEFAULT_WATERMARK_COLOR,
                'font_size': DEFAULT_FONT_SIZE,
                'position': DEFAULT_WATERMARK_POSITION
            }
    except Exception as e:
        print(f"加载上次设置失败: {e}")
        # 加载失败时返回默认设置
        return {
            'text': DEFAULT_WATERMARK_TEXT,
            'transparency': DEFAULT_WATERMARK_TRANSPARENCY,
            'color': DEFAULT_WATERMARK_COLOR,
            'font_size': DEFAULT_FONT_SIZE,
            'position': DEFAULT_WATERMARK_POSITION
        }


# 为了保持向后兼容性，提供别名函数
load_last_watermark_settings = load_last_settings
save_current_watermark_settings = save_last_settings