import sys
import os
from PySide6.QtWidgets import QApplication, QFileDialog, QMessageBox
from PySide6.QtCore import QThread, Signal
import ffmpeg
from ui import VideoToGifConverterUI

class ConversionThread(QThread):
    progress_update = Signal(int)
    error = Signal(str)

    def __init__(self, input_video, output_path, fps, width):
        super().__init__()
        self.input_video = input_video
        self.output_path = output_path
        self.fps = fps
        self.width = width

    def run(self):
        try:
            input_stream = ffmpeg.input(self.input_video)
            filtered = (
                input_stream
                .filter('fps', fps=self.fps)
                .filter('scale', width=self.width, height=-1)
            )
            split = filtered.split()
            palette = split[0].filter('palettegen')
            output = ffmpeg.filter([split[1], palette], 'paletteuse')
            out = ffmpeg.output(output, self.output_path)
            ffmpeg.run(out, capture_stdout=True, capture_stderr=True, overwrite_output=True)
            self.progress_update.emit(100)
        except ffmpeg.Error as e:
            self.error.emit(f"FFmpeg error: {e.stderr.decode()}")

class VideoToGifConverter:
    def __init__(self):
        self.ui = VideoToGifConverterUI()
        self.input_video = None
        self.conversion_thread = None

        # Connect signals
        self.ui.import_button.clicked.connect(self.import_video)
        self.ui.convert_button.clicked.connect(self.start_conversion)
        self.ui.path_button.clicked.connect(self.choose_output_path)
        self.ui.import_video_signal.connect(self.handle_dropped_video)
        self.ui.start_conversion_signal.connect(self.start_conversion)

    def import_video(self):
        file_dialog = QFileDialog()
        self.input_video, _ = file_dialog.getOpenFileName(self.ui, "选择视频文件", "", "Video Files (*.mp4 *.avi *.mov)")
        if self.input_video:
            self.update_video_info()
            self.set_default_output_path()
            self.ui.load_video(self.input_video)

    def handle_dropped_video(self, file_path):
        self.input_video = file_path
        self.update_video_info()
        self.set_default_output_path()
        self.ui.load_video(self.input_video)

    def update_video_info(self):
        if self.input_video:
            try:
                probe = ffmpeg.probe(self.input_video)
                video_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'video'), None)
                if video_stream:
                    fps = eval(video_stream['r_frame_rate'])
                    width = video_stream['width']
                    height = video_stream['height']
                    self.ui.update_video_info(fps, f"{width}x{height}")
                    self.ui.set_default_fps(fps)
                    self.ui.set_default_resolution(f"{width}x{height}")
            except ffmpeg.Error as e:
                self.show_error_message(f"无法读取视频信息: {str(e)}")

    def set_default_output_path(self):
        if self.input_video:
            input_dir = os.path.dirname(self.input_video)
            self.ui.path_edit.setText(input_dir)

    def choose_output_path(self):
        folder_path = QFileDialog.getExistingDirectory(self.ui, "选择输出文件夹")
        if folder_path:
            self.ui.path_edit.setText(folder_path)

    def start_conversion(self):
        if not self.input_video or not self.ui.path_edit.text():
            self.show_error_message("请选择输入视频和输出路径")
            return

        output_path = os.path.join(self.ui.path_edit.text(), os.path.splitext(os.path.basename(self.input_video))[0] + ".gif")
        fps = int(self.ui.fps_combo.currentText())
        width = int(self.ui.resolution_combo.currentText().split('x')[0])

        self.conversion_thread = ConversionThread(self.input_video, output_path, fps, width)
        self.conversion_thread.progress_update.connect(self.ui.update_progress)
        self.conversion_thread.finished.connect(self.conversion_finished)
        self.conversion_thread.error.connect(self.show_error_message)
        self.conversion_thread.start()

        self.ui.enable_convert_button(False)

    def conversion_finished(self):
        self.ui.update_progress(100)
        self.ui.enable_convert_button(True)
        QMessageBox.information(self.ui, "转换完成", "GIF 转换已完成！")

    def show_error_message(self, message):
        QMessageBox.critical(self.ui, "错误", message)

    def run(self):
        self.ui.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    converter = VideoToGifConverter()
    converter.run()
    sys.exit(app.exec())