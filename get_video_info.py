import subprocess
import os
import re
from typing import Dict, Optional

def get_video_info(video_path) -> Optional[Dict]:
    ffmpeg_path = './ffmpeg'
    if not os.path.exists(ffmpeg_path):
        print(f"Error: {ffmpeg_path} not found.")
        return None

    cmd = [ffmpeg_path, '-i', video_path]

    try:
        result = subprocess.run(cmd, capture_output=True, universal_newlines=True, 
                                encoding='utf-8', errors='replace', check=False)
        output = result.stderr

        info = {}

        # 提取分辨率
        resolution_match = re.search(r'Stream #0:0.*: Video:.* (\d+)x(\d+)', output)
        if resolution_match:
            width, height = resolution_match.groups()
            info['width'] = int(width)
            info['height'] = int(height)
        else:
            print("Warning: Could not extract resolution.")

        # 提取帧率
        framerate_match = re.search(r'(\d+(?:\.\d+)?)\s*fps', output)
        if framerate_match:
            info['frame_rate'] = float(framerate_match.group(1))
        else:
            # 尝试从 avg_frame_rate 提取
            avg_framerate_match = re.search(r'avg_frame_rate=(\d+)/(\d+)', output)
            if avg_framerate_match:
                num, den = map(int, avg_framerate_match.groups())
                info['frame_rate'] = round(num / den, 2) if den != 0 else None
            else:
                print("Warning: Could not extract frame rate.")

        return info if info else None

    except subprocess.CalledProcessError as e:
        print(f"Error running FFmpeg: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None

# 使用示例
if __name__ == "__main__":
    video_file = './test/input.mp4'  # 替换为实际的视频文件路径
    video_info = get_video_info(video_file)
    if video_info:
        print("Video Information:")
        for key, value in video_info.items():
            print(f"{key}: {value}")
    else:
        print("Failed to get video information.")
