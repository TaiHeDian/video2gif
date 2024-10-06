from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QLineEdit, QPushButton, QFileDialog, QComboBox, QProgressBar, 
                               QSizePolicy, QSlider, QStyle)
from PySide6.QtCore import Qt, Signal, QUrl, QTime
from PySide6.QtGui import QDropEvent, QDragEnterEvent
from PySide6.QtMultimedia import QMediaPlayer
from PySide6.QtMultimediaWidgets import QVideoWidget

class VideoToGifConverterUI(QMainWindow):
    import_video_signal = Signal(str)
    start_conversion_signal = Signal(str, str, int, int)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Video to GIF Converter")
        self.setGeometry(100, 100, 800, 600)

        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)

        # Drag and drop area / Video player
        self.drag_drop_label = QLabel("拖拽视频文件到这里或点击导入")
        self.drag_drop_label.setAlignment(Qt.AlignCenter)
        self.drag_drop_label.setStyleSheet("border: 2px dashed gray; padding: 20px;")
        self.drag_drop_label.setAcceptDrops(True)

        self.video_widget = QVideoWidget()
        self.video_widget.hide()  # Initially hide the video widget

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
        self.fps_combo.addItems(["10", "15", "20", "25", "30"])
        self.resolution_combo = QComboBox()
        self.resolution_combo.addItems(["640x360", "854x480", "1280x720", "1920x1080"])
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
        self.path_button = QPushButton("选择路径")
        path_layout.addWidget(self.path_edit)
        path_layout.addWidget(self.path_button)
        path_widget = QWidget()
        path_widget.setLayout(path_layout)
        layout.addWidget(path_widget)

        # Progress bar
        self.progress_bar = QProgressBar()
        layout.addWidget(self.progress_bar)

        # Control buttons
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

        # Connect signals
        self.play_pause_button.clicked.connect(self.toggle_play_pause)
        self.progress_slider.sliderMoved.connect(self.set_position)
        self.media_player.positionChanged.connect(self.position_changed)
        self.media_player.durationChanged.connect(self.duration_changed)
        self.drag_drop_label.mousePressEvent = self.drag_drop_clicked

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

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def enable_convert_button(self, enable):
        self.convert_button.setEnabled(enable)

    def toggle_play_pause(self):
        if self.media_player.playbackState() == QMediaPlayer.PlayingState:
            self.media_player.pause()
            self.play_pause_button.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        else:
            self.media_player.play()
            self.play_pause_button.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))

    def set_position(self, position):
        self.media_player.setPosition(position)

    def position_changed(self, position):
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

    def load_video(self, file_path):
        self.media_player.setSource(QUrl.fromLocalFile(file_path))
        self.play_pause_button.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.drag_drop_label.hide()
        self.video_widget.show()

    def drag_drop_clicked(self, event):
        self.import_button.click()