#!/usr/bin/env python3
import sys
import os
from video_editor import VideoEditor
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.console import Console
from rich import print as rprint

def process_video(input_path):
    """处理视频文件"""
    if not os.path.exists(input_path):
        rprint(f"[red]错误：文件不存在: {input_path}[/red]")
        return False

    # 检查文件扩展名
    valid_extensions = {'.mp4', '.mov', '.avi'}
    if not os.path.splitext(input_path)[1].lower() in valid_extensions:
        rprint(f"[red]错误：不支持的文件格式。支持的格式：{', '.join(valid_extensions)}[/red]")
        return False

    # 设置输出路径（下载文件夹）
    output_filename = f"edited_{os.path.basename(input_path)}"
    output_path = os.path.join(os.path.expanduser("~/Downloads"), output_filename)

    console = Console()
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TimeElapsedColumn(),
            console=console
        ) as progress:
            task = progress.add_task("[cyan]处理视频中...", total=None)
            
            # 创建编辑器实例并处理视频
            editor = VideoEditor(input_path, output_path)
            editor.create_final_video()
            
            progress.update(task, completed=True)
        
        rprint(f"[green]✓ 处理完成！[/green]")
        rprint(f"[blue]输出文件：{output_path}[/blue]")
        return True

    except Exception as e:
        rprint(f"[red]处理失败：{str(e)}[/red]")
        return False

def main():
    """主函数"""
    # 显示欢迎信息
    rprint("[yellow]25秒自动剪辑工具 - 命令行版本[/yellow]")
    rprint("[yellow]支持直接拖拽视频文件到终端窗口[/yellow]")
    
    if len(sys.argv) < 2:
        rprint("[red]请提供视频文件路径（直接拖拽文件到终端）[/red]")
        rprint("使用方法：")
        rprint("  python cli.py <视频文件路径>")
        rprint("  或直接拖拽视频文件到终端窗口")
        return

    input_path = sys.argv[1].strip()
    # 处理 macOS 中拖拽文件时可能带有的引号
    if input_path.startswith('"') and input_path.endswith('"'):
        input_path = input_path[1:-1]
    
    process_video(input_path)

if __name__ == "__main__":
    main()
