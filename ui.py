from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
                               QPushButton, QComboBox, QProgressBar, QSizePolicy, QSlider, QStyle)
from PySide6.QtCore import Qt, Signal, QUrl, QTime, QTimer
from PySide6.QtGui import QDropEvent, QDragEnterEvent, QKeyEvent, QIcon
from PySide6.QtMultimedia import QMediaPlayer
from PySide6.QtMultimediaWidgets import QVideoWidget


class VideoToGifConverterUI(QMainWindow):
    import_video_signal = Signal(str)
    start_conversion_signal = Signal(str, str, int, int)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("动图转换器")
        self.setGeometry(100, 100, 600, 600)
        self.setWindowIcon(QIcon("vid2gif.ico"))

        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)

        # Drag and drop area / Video player
        self.drag_drop_label = QLabel("拖拽视频文件到这里")
        self.drag_drop_label.setAlignment(Qt.AlignCenter)
        self.drag_drop_label.setStyleSheet("border: 2px dashed gray; padding: 20px;")
        self.drag_drop_label.setAcceptDrops(True)
        self.drag_drop_label.mousePressEvent = self.drag_drop_clicked

        self.video_widget = QVideoWidget()
        self.video_widget.hide()

        self.stacked_widget = QWidget()
        self.stacked_layout = QVBoxLayout(self.stacked_widget)
        self.stacked_layout.addWidget(self.drag_drop_label)
        self.stacked_layout.addWidget(self.video_widget)

        self.stacked_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout.addWidget(self.stacked_widget, 1)  # Set stretch factor to 1

        # Player controls
        controls_layout = QHBoxLayout()
        self.play_pause_button = QPushButton()
        self.play_pause_button.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.play_pause_button.setFixedSize(40, 40)
        self.progress_slider = QSlider(Qt.Horizontal)
        self.time_label = QLabel("00:00 / 00:00")
        controls_layout.addWidget(self.play_pause_button)
        controls_layout.addWidget(self.progress_slider)
        controls_layout.addWidget(self.time_label)
        layout.addLayout(controls_layout)

        # Video info
        info_layout = QHBoxLayout()
        self.fps_label = QLabel("帧率: ")
        self.resolution_label = QLabel("分辨率: ")
        info_layout.addWidget(self.fps_label)
        info_layout.addWidget(self.resolution_label)
        info_widget = QWidget()
        info_widget.setLayout(info_layout)
        info_widget.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        layout.addWidget(info_widget)

        # Output settings
        settings_layout = QHBoxLayout()
        self.fps_combo = QComboBox()
        self.fps_combo.addItems(["10", "15", "20", "25", "30", "45", "60"])
        self.resolution_combo = QComboBox()
        self.resolution_combo.addItems(
            ["640x360", "854x480", "960x540", "1280x720", "1920x1080", "2560x1440", "3840x2160"])
        settings_layout.addWidget(QLabel("输出帧率:"))
        settings_layout.addWidget(self.fps_combo)
        settings_layout.addWidget(QLabel("输出分辨率:"))
        settings_layout.addWidget(self.resolution_combo)
        settings_widget = QWidget()
        settings_widget.setLayout(settings_layout)
        layout.addWidget(settings_widget)

        # Output path
        path_layout = QHBoxLayout()
        self.path_edit = QLineEdit()
        self.path_button = QPushButton("选择保存位置")
        path_layout.addWidget(self.path_edit)
        path_layout.addWidget(self.path_button)
        path_widget = QWidget()
        path_widget.setLayout(path_layout)
        layout.addWidget(path_widget)

        # 进度条
        progress_layout = QHBoxLayout()
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        self.progress_label = QLabel("就绪")
        progress_layout.addWidget(self.progress_bar)
        progress_layout.addWidget(self.progress_label)
        progress_widget = QWidget()
        progress_widget.setLayout(progress_layout)
        layout.addWidget(progress_widget)

        # 添加用于动画的计时器
        self.animation_timer = QTimer(self)
        self.animation_timer.timeout.connect(self.update_progress_animation)
        self.animation_value = 0

        # 控制按钮
        button_layout = QHBoxLayout()
        self.import_button = QPushButton("导入")
        self.convert_button = QPushButton("开始转换")
        button_layout.addWidget(self.import_button)
        button_layout.addWidget(self.convert_button)
        button_widget = QWidget()
        button_widget.setLayout(button_layout)
        layout.addWidget(button_widget)

        # Set up media player
        self.media_player = QMediaPlayer()
        self.media_player.setVideoOutput(self.video_widget)

        # 播放器控制
        self.play_pause_button.clicked.connect(self.toggle_play_pause)
        self.media_player.playbackStateChanged.connect(self.update_play_pause_button)
        self.progress_slider.sliderPressed.connect(self.slider_pressed)
        self.progress_slider.sliderReleased.connect(self.slider_released)
        self.progress_slider.sliderMoved.connect(self.set_position)
        self.media_player.positionChanged.connect(self.position_changed)
        self.media_player.durationChanged.connect(self.duration_changed)

        # Customize slider behavior
        self.progress_slider.setPageStep(0)

        # Enable keyboard control
        self.setFocusPolicy(Qt.StrongFocus)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        for url in event.mimeData().urls():
            self.import_video_signal.emit(url.toLocalFile())
            break

    def update_video_info(self, fps, resolution):
        self.fps_label.setText(f"帧率: {fps:.2f}")
        self.resolution_label.setText(f"分辨率: {resolution}")

    def set_default_fps(self, fps):
        index = self.fps_combo.findText(str(int(fps)))
        if index >= 0:
            self.fps_combo.setCurrentIndex(index)
        else:
            self.fps_combo.addItem(str(int(fps)))
            self.fps_combo.setCurrentIndex(self.fps_combo.count() - 1)

    def set_default_resolution(self, resolution):
        index = self.resolution_combo.findText(resolution)
        if index >= 0:
            self.resolution_combo.setCurrentIndex(index)
        else:
            self.resolution_combo.addItem(resolution)
            self.resolution_combo.setCurrentIndex(self.resolution_combo.count() - 1)

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key_Space:
            self.toggle_play_pause()
        elif event.key() == Qt.Key_Left:
            self.seek_backward()
        elif event.key() == Qt.Key_Right:
            self.seek_forward()
        else:
            super().keyPressEvent(event)

    def toggle_play_pause(self):
        if self.media_player.playbackState() == QMediaPlayer.PlayingState:
            self.media_player.pause()
        else:
            self.media_player.play()

    def update_play_pause_button(self, state):
        if state == QMediaPlayer.PlayingState:
            self.play_pause_button.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))
        else:
            self.play_pause_button.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))

    def slider_pressed(self):
        self.media_player.pause()

    def slider_released(self):
        self.set_position(self.progress_slider.value())
        self.media_player.play()

    def set_position(self, position):
        self.media_player.setPosition(position)

    def position_changed(self, position):
        if not self.progress_slider.isSliderDown():
            self.progress_slider.setValue(position)
        self.update_time_label(position, self.media_player.duration())

    def duration_changed(self, duration):
        self.progress_slider.setRange(0, duration)
        self.update_time_label(self.media_player.position(), duration)

    def update_time_label(self, position, duration):
        position_time = QTime(0, 0).addMSecs(position)
        duration_time = QTime(0, 0).addMSecs(duration)
        time_format = "mm:ss"
        self.time_label.setText(f"{position_time.toString(time_format)} / {duration_time.toString(time_format)}")

    def seek_backward(self):
        current_position = self.media_player.position()
        new_position = max(0, current_position - 500)
        self.media_player.setPosition(new_position)

    def seek_forward(self):
        current_position = self.media_player.position()
        duration = self.media_player.duration()
        new_position = min(duration, current_position + 500)
        self.media_player.setPosition(new_position)

    def load_video(self, file_path):
        self.media_player.setSource(QUrl.fromLocalFile(file_path))
        self.play_pause_button.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.drag_drop_label.hide()
        self.video_widget.show()

    def start_progress_animation(self):
        self.progress_bar.setValue(0)
        self.progress_label.setText("转换中...")
        self.animation_timer.start(50)

    def stop_progress_animation(self):
        self.animation_timer.stop()
        self.progress_bar.setValue(100)
        self.progress_label.setText("转换完成")

    def update_progress_animation(self):
        self.animation_value = (self.animation_value + 5) % 100  # 循环前进，步长为5
        self.progress_bar.setValue(self.animation_value)

    def reset_progress(self):
        self.animation_timer.stop()
        self.progress_bar.setValue(0)
        self.progress_label.setText("就绪")

    def enable_convert_button(self, enable):
        self.convert_button.setEnabled(enable)

    def drag_drop_clicked(self, event):
        self.import_button.click()

    def update_path_edit(self, path):
        self.path_edit.setText(path)

    def get_output_path(self):
        return self.path_edit.text().replace("输出文件：", "").strip()
