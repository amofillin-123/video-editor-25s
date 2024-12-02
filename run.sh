#!/bin/bash

# 显示标题
echo "================================"
echo "     25秒自动剪辑工具 v1.0      "
echo "================================"

# 检查input目录是否存在
if [ ! -d "input" ]; then
    mkdir input
    echo "已创建input目录"
fi

# 检查output目录是否存在
if [ ! -d "output" ]; then
    mkdir output
    echo "已创建output目录"
fi

# 列出input目录中的视频文件
echo "\n可用的视频文件："
ls -1 input/*.{mp4,MP4,mov,MOV,avi,AVI} 2>/dev/null

# 提示用户输入文件名
echo "\n请输入要处理的视频文件名（包括扩展名）："
read filename

# 检查文件是否存在
if [ ! -f "input/$filename" ]; then
    echo "错误：文件 'input/$filename' 不存在！"
    echo "请将视频文件放在input目录中后重试。"
    exit 1
fi

# 运行Python脚本
echo "\n开始处理视频..."
python main.py --input "$filename"
