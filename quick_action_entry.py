#!/usr/bin/env python3
import sys
import os
from video_editor import VideoEditor
from rich.console import Console
from rich import print as rprint

def process_video(input_path):
    """处理视频文件"""
    if not os.path.exists(input_path):
        print(f"错误：文件不存在: {input_path}")
        return False

    # 检查文件扩展名
    valid_extensions = {'.mp4', '.mov', '.avi'}
    if not os.path.splitext(input_path)[1].lower() in valid_extensions:
        print(f"错误：不支持的文件格式。支持的格式：{', '.join(valid_extensions)}")
        return False

    # 设置输出路径（下载文件夹）
    output_filename = f"edited_{os.path.basename(input_path)}"
    output_path = os.path.join(os.path.expanduser("~/Downloads"), output_filename)

    try:
        # 创建编辑器实例并处理视频
        editor = VideoEditor(input_path, output_path)
        editor.create_final_video()
        print(f"✓ 处理完成！输出文件：{output_path}")
        return True

    except Exception as e:
        print(f"处理失败：{str(e)}")
        return False

if __name__ == "__main__":
    if len(sys.argv) > 1:
        input_path = sys.argv[1]
        process_video(input_path)
