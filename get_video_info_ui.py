import tkinter as tk
from tkinter import filedialog, messagebox

from get_video_info import get_video_info


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
                    width = info.get('width', 'Not found')
                    height = info.get('height', 'Not found')
                    frame_rate = info.get('frame_rate', 'Not found')
                    total_frames = info.get('total_frames', 'Not found')
                    self.info_label.config(text=f"分辨率: {width}x{height}\n帧率: {frame_rate} fps\n总帧数：: {total_frames}")
                else:
                    self.info_label.config(text="无法获取视频信息！")
            except Exception as e:
                messagebox.showerror("错误！", str(e))


if __name__ == "__main__":
    root = tk.Tk()
    gui = VideoInfoGUI(root)
    root.mainloop()
