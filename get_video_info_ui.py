import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess
import os
import re

def get_video_info(video_path):
    ffmpeg_path = os.path.join(os.getcwd(), 'ffmpeg.exe')
    if not os.path.exists(ffmpeg_path):
        raise FileNotFoundError(f"{ffmpeg_path} not found.")

    cmd = [ffmpeg_path, '-i', video_path]

    result = subprocess.run(cmd, capture_output=True, text=True)
    output = result.stderr

    info = {}

    resolution_match = re.search(r'Stream #0:0.*: Video:.* (\d+)x(\d+)', output)
    if resolution_match:
        width, height = resolution_match.groups()
        info['resolution'] = f"{width}x{height}"

    framerate_match = re.search(r'(\d+(?:\.\d+)?)\s*fps', output)
    if framerate_match:
        info['frame_rate'] = float(framerate_match.group(1))
    else:
        avg_framerate_match = re.search(r'avg_frame_rate=(\d+)/(\d+)', output)
        if avg_framerate_match:
            num, den = map(int, avg_framerate_match.groups())
            info['frame_rate'] = round(num / den, 2) if den != 0 else None

    return info

class VideoInfoGUI:
    def __init__(self, master):
        self.master = master
        master.title("视频信息")

        self.label = tk.Label(master, text="选择视频文件：")
        self.label.pack()

        self.select_button = tk.Button(master, text="浏览", command=self.select_file)
        self.select_button.pack()

        self.info_label = tk.Label(master, text="")
        self.info_label.pack()

    def select_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("视频文件", "*.mp4 *.avi *.mkv *.mov")])
        if file_path:
            try:
                info = get_video_info(file_path)
                if info:
                    resolution = info.get('resolution', 'Not found')
                    frame_rate = info.get('frame_rate', 'Not found')
                    self.info_label.config(text=f"分辨率: {resolution}\n帧率: {frame_rate} fps")
                else:
                    self.info_label.config(text="无法获取视频信息！")
            except Exception as e:
                messagebox.showerror("错误！", str(e))

if __name__ == "__main__":
    root = tk.Tk()
    gui = VideoInfoGUI(root)
    root.mainloop()