<div align="center">
  <h1 align="center">
    <img src="img/vid2gif-icon.png" width="150" alt="video to GIF Converter icon."/>
    <br/>
    动图转换器
  </h1>
<h3><i>基于FFmpeg的视频动图转换器</i></h3>
</div>

## 使用

点击导入或拖入视频源文件，选择目标动图分辨率和帧率，然后点击`开始转换`。

程序可以多开运行，进行多个视频的同时转换，或同一个视频不同清晰度的转换。

## 开发

使用Nuitka打包

- Windows:
```commandline
python -m nuitka --standalone --onefile --plugin-enable=pyside6 --include-package=PySide6 --include-package=PySide6.QtMultimedia --include-package=PySide6.QtMultimediaWidgets --include-qt-plugins=multimedia --windows-icon-from-ico=vid2gif.ico --include-qt-plugins=sensible,qwindows,styles --windows-console-mode=disable --windows-file-version=<version> --output-dir=out --assume-yes-for-downloads vid2gif.py
```

- macOS:
```shell
python -m nuitka --follow-imports \
       --standalone \
       --enable-plugin=pyside6 \
       --include-data-dir=.=. \
       --macos-create-app-bundle \
       --macos-app-icon=vid2gif.icns \
       --include-package=PySide6 \
       --output-dir=out \
       vid2gif.py
```
