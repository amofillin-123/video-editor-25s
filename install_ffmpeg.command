#!/bin/bash
cd "$(dirname "$0")"

echo "===== 开始安装 FFMPEG ====="

# 检查是否已安装 Homebrew
if ! command -v brew &> /dev/null; then
    echo "正在安装 Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
else
    echo "Homebrew 已安装"
fi

# 安装或更新 ffmpeg
echo "正在安装/更新 FFMPEG..."
brew install ffmpeg

echo "===== FFMPEG 安装完成 ====="
echo "FFMPEG 版本信息："
ffmpeg -version

echo "按任意键退出..."
read -n 1
