# main.py is the main file that contains the main application logic.
import os
import sys

from PyQt5 import uic
from PyQt5.uic import loadUiType
from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog, QMessageBox, QLabel, QLineEdit, QPushButton

import pafy
import UI_Pages_PY.Downloading_UI_Page as DPage

import file_downloader

FORM_CLASS, _ = loadUiType(os.path.join(os.path.dirname(__file__), "UIs", "main.ui"))


def is_playlist(url):
    try:
        playlist = pafy.get_playlist(url)
        return True  # If no error, then it's a playlist
    except ValueError:
        return False  # If there's a ValueError, it's not a playlist


class MainApp(QMainWindow, FORM_CLASS):
    def __init__(self, parent=None):
        super(MainApp, self).__init__(parent)
        self.setupUi(self)  # Move this line before self.Handle_Buttons()
        # uic.loadUi(FORM_CLASS, self)
        self.file_name_label = self.findChild(QLabel, 'FileName2')
        self.file_size_label = self.findChild(QLabel, 'FileSize')
        self.file_type_label = self.findChild(QLabel, 'FileType')
        self.url_entre_box = self.findChild(QLineEdit, 'lineEdit')
        self.file_path = self.findChild(QLineEdit, 'SaveLocation')
        self.cancel_button = self.findChild(QPushButton, 'pushButton_2')
        self.BrowseButton = self.findChild(QPushButton, 'BrowseButton')
        print("DownloadingPage initialized successfully.")
        self.Handle_Buttons()
        self.Fixed_UI()

    def Fixed_UI(self):
        self.setWindowTitle("The Downloader")
        self.setFixedSize(900, 720)

    def Browse_Button_File(self):
        initial_filename = self.file_name_label.text() if self.file_name_label.text() else "untitled"
        file_path, _ = QFileDialog.getSaveFileName(self, "Save File", initial_filename, "All Files (*)")
        if file_path:
            self.full_save_path = file_path
            self.file_path.setText(os.path.basename(file_path))

    def Handle_Buttons(self):
        self.BrowseButton.clicked.connect(self.Browse_Button_File)
        self.DownloadButton.clicked.connect(self.Download_File)
        self.lineEdit.textChanged.connect(self.update_file_info)
        self.cancel_button.clicked.connect(self.close)

    def Cancel_Download(self):
        if hasattr(self, 'download_thread') and self.download_thread is not None and self.download_thread.isRunning():
            self.download_thread.Cancel_Download()  # Cancel the ongoing download
            self.download_thread.wait()  # Wait for the thread to stop
            self.download_thread = None  # Reset the thread reference

    # def update_file_info(self):
    #     url = self.lineEdit.text()
    #     if not url:
    #         self.FileSize.setText("Size: Unknown")
    #         self.MimeType.setText("Type: Unknown")
    #         return
    #     if "youtube.com" in url or "youtu.be" in url:
    #         if is_playlist(url):
    #             self.hide()
    #             self.youtube_playlist = YP.YPlaylist()
    #             self.youtube_playlist.show()
    #             self.youtube_playlist.lineEdit3.setText(url)
    #
    #         else:
    #             self.hide()
    #             self.youtube_video = YVideo()
    #             self.youtube_video.show()
    #             self.youtube_video.lineEdit2.setText(url)
    #             QTimer.singleShot(100, lambda: self.youtube_video.get_video_info(url))  # Delay the call to get_video_info
    #
    #
    #     else:
    #         # Fetch file info
    #         mime_type, File_size = DownloadFile.get_info(url)
    #
    #         # Update the UI with the file info
    #         self.FileType.setText(f" {mime_type}")
    #         self.FileSize.setText(f" {File_size}")
    #         self.SaveLocation.setText(f" {extract_filename_from_url(url)}")

    def update_file_info(self):
        url = self.lineEdit.text()
        if "youtube.com" in url or "youtu.be" in url:
            pass
            # if is_playlist(url):
            #     self.hide()
            #     self.youtube_playlist = YP.YPlaylist()
            #     self.youtube_playlist.show()
            #     self.youtube_playlist.lineEdit3.setText(url)
            #
            # else:
            #     self.hide()
            #     self.youtube_video = YVideo()
            #     self.youtube_video.show()
            #     self.youtube_video.lineEdit2.setText(url)
            #     QTimer.singleShot(100, lambda: self.youtube_video.get_video_info(url))

        else:
            file_downloader.Get_File_Info(url)
            temp_name, temp_size, temp_type = file_downloader.Get_File_Info(url)
            file_downloader.Set_File_Info(self, temp_name, temp_size, temp_type)

    def Download_File(self):
        url = self.lineEdit.text()
        if not url:
            self.show_error_message("Please enter a valid URL.")
            return

        file_path = self.full_save_path
        downloading_page_2 = DPage.DownloadingPage(self)

        # Initialize the downloading page with the current file info
        file_downloader.Set_File_Info(self, self.file_name_label.text(), self.file_size_label.text(),
                                      self.file_type_label.text())
        downloading_page_2.show()
        downloading_page_2.update_Downloading_info(self.file_name_label.text(),
                                                   self.file_size_label.text(),
                                                   self.file_type_label.text())

        # Create a new DownloadWorker instance and start the download
        self.download_thread = file_downloader.DownloadWorker(url, file_path)  # Store the DownloadWorker instance
        self.download_thread.progress.connect(
            downloading_page_2.progress)  # Connect the progress signal to the progress slot
        self.download_thread.finished.connect(self.on_download_finished)  # Connect the finished signal to the handler
        self.download_thread.canceled.connect(self.on_download_canceled)  # Connect the canceled signal to the handler
        self.download_thread.start()

    def on_download_finished(self):
        if hasattr(self, 'download_thread') and self.download_thread.isFinished():
            QMessageBox.information(self, "Download Complete", "The file has been downloaded successfully.")
        else:
            QMessageBox.critical(self, "Download Failed", "The file could not be downloaded.")

    def on_download_canceled(self):
        QMessageBox.information(self, "Download Canceled", "The download has been canceled.")


def main():
    app = QApplication(sys.argv)
    window = MainApp()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
