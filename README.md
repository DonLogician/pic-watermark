# pic-watermark
assignment for the LLM Assited SE course

## 功能介绍
这是一个使用Python编写的命令行程序，用于给照片添加水印。程序会从图片的EXIF信息中提取拍摄时间，选取年月日作为水印，并可以根据用户设置自定义水印的位置、大小和颜色。

## 基本功能
- 支持处理单个图片文件或批量处理目录中的所有支持格式图片
- 提取图片EXIF信息中的拍摄时间
- 使用年月日（YYYY-MM-DD格式）作为水印文本
- 支持自定义水印位置、字体大小和颜色
- 处理后的图片将保存在输入目录下的_watermark子目录中，文件名添加_watermark后缀

## 扩展功能
- 批量处理：一次性处理目录中的所有支持格式图片
- 自定义水印参数：
  - 水印位置：左上角、中央、右下角
  - 字体大小：可调整的整数大小
  - 水印颜色：支持颜色名称或十六进制颜色值

## 依赖库
- Pillow (用于图像处理和EXIF信息提取)

## 使用方法
1. 确保已安装Anaconda或Miniconda环境
2. 创建并激活conda环境：
   ```
   conda create -n pic-watermark python=3.9
   conda activate pic-watermark
   ```
3. 安装依赖库：`pip install -r requirements.txt`
4. 运行程序：`python pic_watermark.py <文件或目录路径> [可选参数]`

## 命令行参数
```
python pic_watermark.py <输入路径> [-p position] [-s font_size] [-c color]
```

**必填参数：**
- `输入路径`：单个图片文件路径或包含图片的目录路径

**可选参数：**
- `-p, --position`：水印位置，可选值：top-left（默认）、center、bottom-right
- `-s, --font-size`：字体大小，默认值：24
- `-c, --color`：水印颜色，支持颜色名称或十六进制值，默认值：white

## 使用示例

### 处理单个文件（使用默认参数）
```
python pic_watermark.py test.jpg
```

### 处理单个文件（自定义参数）
```
python pic_watermark.py test.jpg -p center -s 36 -c red
```

### 批量处理目录中的所有图片
```
python pic_watermark.py pics_folder -p bottom-right -s 20 -c #0000FF
```

## 输出说明
- 处理单个文件时，处理后的图片将保存在与输入文件相同目录下的`_watermark`子目录中
- 批量处理目录时，处理后的所有图片将保存在输入目录下的`_watermark`子目录中
- 输出文件名格式为：原文件名_watermark.原扩展名
