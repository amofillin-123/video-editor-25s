#!/bin/bash
cd "$(dirname "$0")"

echo "===== 开始安装 FFMPEG ====="

# 使用conda安装ffmpeg
echo "正在通过conda安装ffmpeg..."
conda install -y ffmpeg

echo "===== 安装完成 ====="
echo "FFMPEG 版本信息："
ffmpeg -version

echo "按任意键退出..."
read -n 1
