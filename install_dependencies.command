#!/bin/bash
cd "$(dirname "$0")"

echo "===== 开始安装依赖 ====="

# 确保pip是最新的
echo "更新pip..."
python -m pip install --upgrade pip

# 安装所需的包
echo "安装必要的包..."
pip install moviepy==1.0.3
pip install opencv-python==4.8.1.78
pip install numpy==1.24.3
pip install customtkinter==5.2.2
pip install imageio-ffmpeg

echo "===== 依赖安装完成 ====="
echo "按任意键退出..."
read -n 1
