# -*- coding: utf-8 -*-
import sys
import os
import re
import time
import subprocess

from PySide6.QtWidgets import QApplication, QFileDialog, QMessageBox
from PySide6.QtCore import QThread, Signal

from ui import VideoToGifConverterUI
from get_video_info import get_video_info


class ConversionThread(QThread):
    progress_update = Signal(int)
    error = Signal(str)
    success = Signal()

    def __init__(self, input_video, output_path, fps, width, total_frames):
        super().__init__()
        self.input_video = input_video
        self.output_path = output_path
        self.fps = fps
        self.width = width
        self.total_frames = total_frames

    def run(self):
        try:
            ffmpeg_path = 'ffmpeg.exe'
            command = [
                ffmpeg_path,
                '-i', self.input_video,
                '-vf',
                f'fps={self.fps},scale={self.width}:-1:flags=lanczos,split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse',
                '-y',
                self.output_path
            ]
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE

            process = subprocess.Popen(command, startupinfo=startupinfo,
                                       stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                       text=True, encoding='utf-8', errors='replace',
                                       creationflags=subprocess.CREATE_NO_WINDOW)

            # 初始进度阶段（0-33%）
            for i in range(34):
                time.sleep(0.67)  # 模拟初始化过程
                self.progress_update.emit(i)

            last_update_time = time.time()
            for line in process.stderr:
                frame_match = re.search(r'frame=\s*(\d+)', line)
                if frame_match:
                    current_frame = int(frame_match.group(1))
                    progress = 33 + int((current_frame / self.total_frames) * 67)
                    self.progress_update.emit(min(progress, 99))  # 进度不得超过99%
                    # DEBUG 显示当前已转换的帧
                    print(current_frame, self.total_frames)

                # 检查进程是否仍在运行
                if process.poll() is not None:
                    break

                # 限制进度更新频率
                current_time = time.time()
                if current_time - last_update_time > 0.1:  # 每0.1秒最多更新一次
                    last_update_time = current_time

            # 等待进程完成
            process.wait()

            if process.returncode != 0:
                error_output = process.stderr.read()
                if "Output file is empty" not in error_output:  # 忽略这个特定的错误
                    self.error.emit(f"FFmpeg error: {error_output}")
                else:
                    self.success.emit()
            else:
                self.success.emit()

            # 确保进度到达100%
            self.progress_update.emit(100)

        except Exception as e:
            self.error.emit(f"Error: {str(e)}")


class VideoToGifConverter:
    def __init__(self):
        self.ui = VideoToGifConverterUI()
        self.input_video = None
        self.output_file = None
        self.conversion_thread = None

        # Connect signals
        self.ui.import_button.clicked.connect(self.import_video)
        self.ui.convert_button.clicked.connect(self.start_conversion)
        self.ui.path_button.clicked.connect(self.choose_output_file)
        self.ui.import_video_signal.connect(self.handle_dropped_video)
        self.ui.start_conversion_signal.connect(self.start_conversion)

    def import_video(self):
        file_dialog = QFileDialog()
        self.input_video, _ = file_dialog.getOpenFileName(self.ui, "选择视频文件", "",
                                                          "Video Files (*.mp4 *.avi *.mov)")
        if self.input_video:
            self.update_video_info()
            self.suggest_output_file()
            self.ui.load_video(self.input_video)

    def handle_dropped_video(self, file_path):
        self.input_video = file_path
        self.update_video_info()
        self.suggest_output_file()
        self.ui.load_video(self.input_video)

    def update_video_info(self):
        if self.input_video:
            video_info = get_video_info(self.input_video)
            fps = video_info['frame_rate']
            width = video_info['width']
            height = video_info['height']
            self.ui.update_video_info(fps, f"{width}x{height}")
            self.ui.set_default_fps(fps)
            self.ui.set_default_resolution(f"{width}x{height}")

    def suggest_output_file(self):
        if self.input_video:
            input_dir = os.path.dirname(self.input_video)
            input_name = os.path.splitext(os.path.basename(self.input_video))[0]
            suggested_output = os.path.join(input_dir, f"{input_name}.gif")
            self.ui.update_path_edit(suggested_output)
            self.output_file = suggested_output

    def choose_output_file(self):
        file_dialog = QFileDialog()
        self.output_file, _ = file_dialog.getSaveFileName(self.ui, "保存 GIF", self.output_file or "",
                                                          "GIF Files (*.gif);;All Files (*)")
        if self.output_file:
            self.ui.update_path_edit(self.output_file)

    def start_conversion(self):
        if not self.input_video or not self.output_file:
            self.show_error_message("请选择输入视频和输出文件")
            return

        fps = int(self.ui.fps_combo.currentText())
        width = int(self.ui.resolution_combo.currentText().split('x')[0])

        video_info = get_video_info(self.input_video)
        if not video_info or 'total_frames' not in video_info:
            self.show_error_message("无法获取视频信息")
            return

        total_frames = video_info['total_frames']

        self.conversion_thread = ConversionThread(self.input_video, self.output_file, fps, width, total_frames)
        self.conversion_thread.progress_update.connect(self.update_progress)
        self.conversion_thread.success.connect(self.conversion_successful)
        self.conversion_thread.finished.connect(self.conversion_finished)
        self.conversion_thread.error.connect(self.show_error_message)
        self.conversion_thread.start()

        self.disable_ui_elements()
        self.ui.progress_bar.setValue(0)
        self.ui.progress_label.setText("转换中... 0%")

    def update_progress(self, value):
        self.ui.progress_bar.setValue(value)
        self.ui.progress_label.setText(f"转换中... {value}%")

    def show_error_message(self, message):
        if "Output file is empty" not in message:  # 忽略这个特定的错误
            QMessageBox.critical(self.ui, "错误", message)

    def conversion_successful(self):
        self.ui.stop_progress_animation()
        QMessageBox.information(self.ui, "转换完成", "GIF 转换已完成！")

    def conversion_failed(self, error_message):
        self.ui.reset_progress()
        self.ui.enable_convert_button(True)
        self.show_error_message(f"转换失败: {error_message}")
        self.ui.progress_bar.setFormat("转换失败")

    def conversion_finished(self):
        self.ui.stop_progress_animation()
        self.enable_ui_elements()

    def disable_ui_elements(self):
        self.ui.enable_convert_button(False)
        self.ui.import_button.setEnabled(False)
        self.ui.path_button.setEnabled(False)
        self.ui.fps_combo.setEnabled(False)
        self.ui.resolution_combo.setEnabled(False)

    def enable_ui_elements(self):
        self.ui.enable_convert_button(True)
        self.ui.import_button.setEnabled(True)
        self.ui.path_button.setEnabled(True)
        self.ui.fps_combo.setEnabled(True)
        self.ui.resolution_combo.setEnabled(True)

    def run(self):
        self.ui.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    converter = VideoToGifConverter()
    converter.run()
    sys.exit(app.exec())
