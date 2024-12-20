import os
import random
import subprocess
import json
import tempfile
import numpy as np
from scenedetect import detect, ContentDetector
import shutil

class VideoEditor:
    def __init__(self, input_path, output_path, target_duration=25):
        self.input_path = input_path
        self.output_path = output_path
        self.target_duration = target_duration
        self.temp_dir = tempfile.mkdtemp()
        self.progress_callback = None

    def _run_ffmpeg(self, command):
        """运行 ffmpeg 命令"""
        try:
            result = subprocess.run(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            if result.returncode != 0:
                print(f"FFmpeg 错误: {result.stderr}")
                return False
            return True
        except Exception as e:
            print(f"运行 FFmpeg 失败: {str(e)}")
            return False

    def _extract_video_segment(self, start, duration, output_path):
        """提取视频片段（保留音频）"""
        command = [
            'ffmpeg', '-y',
            '-i', self.input_path,
            '-ss', str(start),
            '-t', str(duration),
            '-c:v', 'copy',  # 直接复制视频流，不重新编码
            '-c:a', 'copy',  # 直接复制音频流，不重新编码
            output_path
        ]
        return self._run_ffmpeg(command)

    def _concat_videos(self, video_files, output_path):
        """合并视频文件"""
        list_file = os.path.join(self.temp_dir, 'file_list.txt')
        with open(list_file, 'w') as f:
            for video_file in video_files:
                f.write(f"file '{video_file}'\n")

        command = [
            'ffmpeg', '-y',
            '-f', 'concat',
            '-safe', '0',
            '-i', list_file,
            '-c', 'copy',  # 直接复制，不重新编码
            output_path
        ]
        return self._run_ffmpeg(command)

    def _detect_scenes(self):
        """使用 PySceneDetect 检测场景"""
        try:
            # 使用内容检测器，降低阈值以获得更自然的场景分割
            scenes = detect(self.input_path, ContentDetector(threshold=27, min_scene_len=15))
            # 转换为时间戳列表
            scene_list = []
            for scene in scenes:
                start_time = float(scene[0].get_seconds())
                end_time = float(scene[1].get_seconds())
                duration = end_time - start_time
                # 过滤掉太短的场景（小于1秒）
                if duration >= 1.0:
                    scene_list.append((start_time, end_time))
            return scene_list
        except Exception as e:
            print(f"场景检测失败: {str(e)}")
            return None

    def _select_scenes(self, scenes, total_duration):
        """智能选择场景，保留开头和结尾"""
        if not scenes or len(scenes) < 4:  # 至少需要4个场景
            return scenes

        # 计算每个场景的时长
        scene_durations = [(end - start, start, end) for start, end in scenes]
        
        # 保留开头的场景（1-2个）
        start_scenes = scene_durations[:2]
        start_duration = sum(duration for duration, _, _ in start_scenes)
        
        # 保留结尾的场景（1-2个）
        end_scenes = scene_durations[-2:]
        end_duration = sum(duration for duration, _, _ in end_scenes)
        
        # 中间场景
        middle_scenes = scene_durations[2:-2]
        
        # 计算中间部分需要的时长
        target_middle_duration = self.target_duration - (start_duration + end_duration)
        
        if target_middle_duration <= 0:
            # 如果开头和结尾已经超过目标时长，只保留它们的一部分
            selected_scenes = [(start, end) for _, start, end in (start_scenes + end_scenes)]
            # 确保不超过目标时长
            total_time = 0
            final_scenes = []
            for start, end in selected_scenes:
                duration = end - start
                if total_time + duration > self.target_duration:
                    # 如果加上这个场景会超时，就截断它
                    end = start + (self.target_duration - total_time)
                    final_scenes.append((start, end))
                    break
                final_scenes.append((start, end))
                total_time += duration
            return final_scenes
        
        # 随机选择中间场景，但优先选择较长的场景
        selected_middle_scenes = []
        current_duration = 0
        
        # 按时长排序中间场景，优先选择较长的场景
        available_scenes = sorted(middle_scenes, key=lambda x: x[0], reverse=True)
        while available_scenes and current_duration < target_middle_duration:
            duration, start, end = available_scenes.pop(0)
            
            if current_duration + duration <= target_middle_duration:
                selected_middle_scenes.append((start, end))
                current_duration += duration
            elif current_duration < target_middle_duration:
                # 如果这个场景太长，截取需要的部分
                needed_duration = target_middle_duration - current_duration
                selected_middle_scenes.append((start, start + needed_duration))
                current_duration = target_middle_duration
        
        # 按时间顺序合并所有选中的场景
        selected_scenes = (
            [(start, end) for _, start, end in start_scenes] +  # 开头场景
            sorted(selected_middle_scenes) +                    # 中间场景（保持时间顺序）
            [(start, end) for _, start, end in end_scenes]     # 结尾场景
        )
        
        return selected_scenes

    def process_video(self, progress_callback=None):
        """处理视频的主要方法"""
        self.progress_callback = progress_callback
        try:
            if self.progress_callback:
                self.progress_callback(0)  # 开始处理
                
            print(f"正在加载视频: {self.input_path}")
            
            # 获取视频信息
            probe_command = [
                'ffprobe',
                '-v', 'error',
                '-select_streams', 'v:0',
                '-show_entries', 'stream=duration',
                '-of', 'json',
                self.input_path
            ]
            
            result = subprocess.run(probe_command, capture_output=True, text=True)
            video_info = json.loads(result.stdout)
            total_duration = float(video_info['streams'][0]['duration'])
            
            print(f"视频总时长: {total_duration}秒")

            if total_duration < self.target_duration:
                print("错误：视频时长不足25秒")
                return False

            # 检测场景
            print("检测场景变化...")
            if self.progress_callback:
                self.progress_callback(20)  # 20% 进度
            
            scenes = self._detect_scenes()
            if not scenes:
                print("场景检测失败，使用备用方案...")
                return False

            # 选择场景
            print("选择场景...")
            if self.progress_callback:
                self.progress_callback(40)  # 40% 进度
                
            selected_scenes = self._select_scenes(scenes, total_duration)
            total_selected_duration = sum(end - start for start, end in selected_scenes)
            print(f"选中场景总时长: {total_selected_duration:.1f}秒")

            # 提取选中的场景（带音频）
            print("提取选中的场景...")
            if self.progress_callback:
                self.progress_callback(60)  # 60% 进度
            video_segments = []
            for i, (start, end) in enumerate(selected_scenes):
                segment_file = os.path.join(self.temp_dir, f"segment_{i}.mp4")
                if self._extract_video_segment(start, end - start, segment_file):
                    video_segments.append(segment_file)
                    print(f"提取场景: {start:.1f}s - {end:.1f}s {'(开头)' if i < 2 else '(结尾)' if i >= len(selected_scenes)-2 else '(中间)'}")

            if not video_segments:
                print("错误：无法提取有效场景")
                return False

            # 合并视频片段
            print("合并场景...")
            if self.progress_callback:
                self.progress_callback(80)  # 80% 进度

            # 确保输出路径有 .mp4 扩展名
            if not self.output_path.lower().endswith('.mp4'):
                self.output_path = f"{self.output_path}.mp4"

            if not self._concat_videos(video_segments, self.output_path):
                print("错误：合并视频片段失败")
                return False

            # 清理临时文件
            print("清理资源...")
            shutil.rmtree(self.temp_dir)
            
            print(f"处理完成，输出文件：{self.output_path}")
            if self.progress_callback:
                self.progress_callback(100)  # 完成
            return True

        except Exception as e:
            print(f"处理失败: {str(e)}")
            if os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)
            return False

    def create_final_video(self):
        """为了保持兼容性的包装方法"""
        return self.process_video()
