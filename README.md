# pic-watermark
assignment for the LLM Assited SE course

## 功能介绍
这是一个使用Python编写的图片水印工具，支持GUI界面和命令行两种操作方式。程序可以批量为图片添加自定义水印，包括文字内容、位置、大小、颜色和透明度等参数设置。

## 基本功能
- 支持GUI界面操作，直观易用
- 支持命令行模式快速处理
- 批量处理目录中的所有支持格式图片
- 自定义水印文本内容
- 支持调整水印位置、字体大小、颜色和透明度
- 处理后的图片将保存在指定的输出目录中

## 扩展功能
- 拖拽操作：支持拖拽图片到界面进行添加
- 实时预览：调整水印参数时可实时查看效果
- 水印位置自定义：支持预设位置和自定义坐标
- 导出格式选择：支持多种图片格式导出

## 项目结构
```
pic-watermark/
├── pic_watermark.py      # 入口文件
├── requirements.txt      # 项目依赖
├── README.md             # 项目说明
└── src/
    ├── gui/              # 图形界面相关代码
    │   ├── main_window.py        # 主窗口
    │   ├── draggable_label.py    # 可拖拽标签组件
    │   └── sidebars/             # 侧边栏组件
    └── watermark_tools/  # 水印处理核心功能
        ├── config.py           # 配置常量
        ├── watermark_processor.py  # 水印处理逻辑
        ├── batch_processor.py  # 批量处理功能
        ├── file_handler.py     # 文件处理工具
        ├── settings_manager.py # 设置管理
        └── exif_utils.py       # EXIF信息处理
```

## 依赖库
- PyQt5 (用于GUI界面)
- Pillow (用于图像处理和EXIF信息提取)

## 使用方法

### 方法一：使用可执行文件（推荐，无需安装Python环境）
1. 从GitHub仓库的Releases页面下载最新版本的`pic_watermark.exe`文件
2. 双击运行该可执行文件
3. 在打开的GUI界面中使用各项功能

### 方法二：通过Python环境运行
1. 确保已安装Python 3.9或更高版本
2. 安装依赖库：`pip install -r requirements.txt`
3. 运行程序：`python pic_watermark.py`

## GUI界面使用指南
1. **添加图片**：
   - 点击"添加图片"按钮选择单个或多个图片
   - 或直接拖拽图片文件到左侧列表区域

2. **设置水印**：
   - 点击"水印设置"按钮打开水印设置面板
   - 在右侧水印设置面板中，输入自定义水印文本
   - 调整透明度滑块设置水印透明度
   - 点击颜色选择器设置水印颜色
   - 调整字体大小数字框设置水印文字大小
   - 在位置下拉菜单中选择预设位置，或选择"自定义"后输入具体坐标

3. **预览效果**：
   - 所有设置将实时反映在中间的预览区域
   - 可拖动预览区域中的水印标签调整位置

4. **导出设置**：
   - 点击"导出设置"按钮打开导出设置面板
   - 选择导出格式（PNG、JPG等）
   - 设置输出目录

5. **开始处理**：
   - 确认所有设置后，点击"导出"按钮

## 命令行模式
```
python pic_watermark.py <输入路径> [-p position] [-s font_size] [-c color] [-t text] [-a opacity]
```

**必填参数：**
- `输入路径`：单个图片文件路径或包含图片的目录路径

**可选参数：**
- `-p, --position`：水印位置，可选值：top-left（默认）、center、bottom-right
- `-s, --font-size`：字体大小，默认值：24
- `-c, --color`：水印颜色，支持颜色名称或十六进制值，默认值：white
- `-t, --text`：水印文本内容，默认值："默认水印"
- `-a, --opacity`：水印透明度（0-100），默认值：50

## 使用示例

### 命令行模式示例

#### 处理单个文件（使用默认参数）
```
python pic_watermark.py test.jpg
```

#### 处理单个文件（自定义参数）
```
python pic_watermark.py test.jpg -p center -s 36 -c red -t "我的水印" -a 70
```

#### 批量处理目录中的所有图片
```
python pic_watermark.py pics_folder -p bottom-right -s 20 -c #0000FF
```

## 输出说明
- 处理后的图片将保存在指定的输出目录中
- 批量处理时，所有处理后的图片将保存在同一输出目录中
- 输出文件名格式为：原文件名_watermark.原扩展名
