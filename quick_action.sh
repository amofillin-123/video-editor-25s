#!/bin/bash

# 获取 Python 和脚本的完整路径
PYTHON_PATH=$(which python3)
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
MAIN_SCRIPT="$SCRIPT_DIR/main.py"

# 处理输入文件
for f in "$@"
do
    # 运行 Python 脚本
    "$PYTHON_PATH" "$MAIN_SCRIPT" "$f"
done
