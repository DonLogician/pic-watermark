# pic-watermark
assignment for the LLM Assited SE course

## 功能介绍
这是一个使用Python编写的命令行程序，用于给照片添加水印。程序会从图片的EXIF信息中提取拍摄时间，选取年月日作为水印，并绘制在图片左上角。

## 基本功能
- 处理当前工作目录下名为test.jpg的图片文件
- 提取图片EXIF信息中的拍摄时间
- 使用年月日（YYYY-MM-DD格式）作为水印文本
- 在图片左上角添加白色水印（字体大小14）
- 处理后的图片以原有文件名+_watermark保存

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
4. 将需要处理的图片命名为test.jpg，放在程序所在目录
5. 运行程序：`python pic_watermark.py`
6. 处理后的图片将保存为test_watermark.jpg
