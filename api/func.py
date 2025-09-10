import os

# 目标目录路径
dir_path = "images/camera1/25-9-7"

# 方法 1.1：获取目录下所有文件和文件夹名称
all_items = os.listdir(dir_path)
print("所有文件和文件夹：", all_items)