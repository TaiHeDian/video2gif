<h2 align="center">动图转换器</h2>

## 使用

转换视频为动图

## 依赖

- FFmpeg

## 开发

使用Nuitka打包

```cmd
nuitka --standalone --onefile --plugin-enable=pyside6 --windows-console-mode=disable vid2gif.py
```
