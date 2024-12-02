import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QLabel, QPushButton, QProgressBar, QFileDialog, QMessageBox)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QDragEnterEvent, QDropEvent
import os
from video_editor import VideoEditor

class VideoProcessThread(QThread):
    progress_updated = pyqtSignal(float)
    finished = pyqtSignal()
    error = pyqtSignal(str)

    def __init__(self, input_path, output_path):
        super().__init__()
        self.input_path = input_path
        self.output_path = output_path

    def run(self):
        try:
            editor = VideoEditor(self.input_path, self.output_path)
            editor.process_video(progress_callback=self.progress_updated.emit)
            self.finished.emit()
        except Exception as e:
            self.error.emit(str(e))

class DropArea(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_window = parent
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setText("拖放视频文件到这里\n或点击选择")
        self.setStyleSheet("""
            QLabel {
                background-color: #2b2b2b;
                border: 2px dashed #666666;
                border-radius: 5px;
                padding: 20px;
                color: #666666;
            }
        """)
        self.setMinimumHeight(150)
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            if file_path.lower().endswith(('.mp4', '.mov', '.avi', '.mkv')):
                # 使用 main_window 而不是 parent()
                if hasattr(self.main_window, 'process_video'):
                    self.main_window.process_video(file_path)
                break

class VideoEditorApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("25秒自动剪辑工具")
        self.setMinimumSize(500, 400)
        self.setup_ui()

    def setup_ui(self):
        # 主窗口部件和布局
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # 标题
        title = QLabel("25秒自动剪辑工具")
        title.setStyleSheet("color: white; font-size: 24px; font-weight: bold;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # 拖放区域 - 传入 self 作为 parent
        self.drop_area = DropArea(self)
        layout.addWidget(self.drop_area)

        # 选择文件按钮
        self.select_button = QPushButton("选择视频文件")
        self.select_button.clicked.connect(self.select_file)
        self.select_button.setStyleSheet("""
            QPushButton {
                background-color: #1f538d;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #2965a7;
            }
        """)
        layout.addWidget(self.select_button)

        # 状态标签
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: white;")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)

        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #2b2b2b;
                border-radius: 5px;
                text-align: center;
                color: white;
            }
            QProgressBar::chunk {
                background-color: #1f538d;
            }
        """)
        self.progress_bar.hide()
        layout.addWidget(self.progress_bar)

        # 设置窗口样式
        self.setStyleSheet("background-color: #242424;")

    def select_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择视频文件",
            "",
            "视频文件 (*.mp4 *.mov *.avi *.mkv);;所有文件 (*.*)"
        )
        if file_path:
            self.process_video(file_path)

    def process_video(self, input_path):
        try:
            # 检查文件类型
            if not input_path.lower().endswith(('.mp4', '.mov', '.avi', '.mkv')):
                QMessageBox.critical(self, "错误", "请选择有效的视频文件 (mp4, mov, avi, mkv)")
                return

            # 设置输出路径
            downloads_path = os.path.expanduser("~/Downloads")
            input_filename = os.path.basename(input_path)
            output_filename = f"edited_{input_filename}"
            output_path = os.path.join(downloads_path, output_filename)

            # 更新界面
            self.select_button.setEnabled(False)
            self.status_label.setText(f"正在处理: {input_filename}")
            self.progress_bar.setValue(0)
            self.progress_bar.show()

            # 创建并启动处理线程
            self.process_thread = VideoProcessThread(input_path, output_path)
            self.process_thread.progress_updated.connect(self.update_progress)
            self.process_thread.finished.connect(self.process_finished)
            self.process_thread.error.connect(self.process_error)
            self.process_thread.start()
        except Exception as e:
            QMessageBox.critical(self, "错误", f"处理视频时出错：{str(e)}")
            self.reset_ui()

    def update_progress(self, progress):
        self.progress_bar.setValue(int(progress * 100))

    def process_finished(self):
        self.reset_ui()
        QMessageBox.information(self, "完成", "视频处理完成！\n已保存到下载文件夹")

    def process_error(self, error_msg):
        self.reset_ui()
        QMessageBox.critical(self, "错误", f"处理视频时出错：{error_msg}")

    def reset_ui(self):
        self.select_button.setEnabled(True)
        self.status_label.setText("")
        self.progress_bar.hide()

def run():
    app = QApplication(sys.argv)
    window = VideoEditorApp()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    run()
