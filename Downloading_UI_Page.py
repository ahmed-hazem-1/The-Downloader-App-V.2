# downloading_page.py
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QDialog, QLabel, QProgressBar, QLineEdit, QFileDialog, QMessageBox
from PyQt5.uic import loadUiType
import os

import file_downloader

DownloadingPage_UI, _ = loadUiType(os.path.join(os.path.dirname(__file__), "../UIs/Downloading_page.ui"))


class DownloadingPage(QDialog, DownloadingPage_UI):
    def __init__(self, parent=None, url=None, save_path=None):
        super().__init__(parent)
        self.url = url
        self.save_path = save_path
        self.setupUi(self)
        self.Handle_Buttons()
        # Initialize UI elements
        self.file_name_label = self.findChild(QLabel, 'FileName_2')
        self.file_size_label = self.findChild(QLabel, 'FileSize_2')
        self.file_type_label = self.findChild(QLabel, 'FileType')
        self.ProgressBar = self.findChild(QProgressBar, 'ProgressBar')  # Changed to 'ProgressBar'
        print("DownloadingPage initialized successfully.")
        self.file_name_label.setText("No file selected")
        self.file_size_label.setText("0 MB")
        self.file_type_label.setText("Unknown")

        # Initialize worker thread
        self.worker = file_downloader.DownloadWorker(self.url, self.save_path)
        self.worker.progress.connect(self.progress)  # Connect progress signal
        self.worker.finished.connect(self.on_download_finished)  # Connect finished signal
        self.worker.canceled.connect(self.Cancel_Download)  # Connect canceled signal

        # Start the worker thread
        self.worker.start()

    def Handle_Buttons(self):
        self.CloseButton_2.clicked.connect(self.Pause_Resume_Download)  # Connect the pause button to the method
        self.CloseButton.clicked.connect(self.Cancel_Download)  # Connect the cancel button to the method
        self.CloseButton.clicked.connect(self.close)

    def Cancel_Download(self):
        if hasattr(self, 'worker') and self.worker.isRunning():
            self.worker.Cancel_Download()  # Call the Cancel_Download method on the worker instance

    def on_download_finished(self):
        if hasattr(self, 'download_thread') and self.worker.isFinished():
            QMessageBox.information(self, "Download Complete", "The file has been downloaded successfully.")
        # else:
        #     QMessageBox.critical(self, "Download Failed", "The file could not be downloaded.")

    def Pause_Resume_Download(self):
        if hasattr(self, 'worker') and self.worker.isRunning():
            if self.worker.is_paused:
                self.worker.Resume_Download()  # Resume download
                self.CloseButton_2.setText("Pause")  # Update button text to "Pause"
            else:
                self.worker.Pause_Download()  # Pause download
                self.CloseButton_2.setText("Resume")  # Update button text to "Resume"

    @pyqtSlot(int, int)
    def progress(self, file_size, total_size):
        if total_size > 0:
            percentage = (file_size / total_size) * 100
            # print(f"Progress: {percentage:.2f}%")
            self.ProgressBar.setValue(int(percentage))
            self.file_size_label.setText(f"{file_size / (1024 * 1024):.2f} MB of {total_size / (1024 * 1024):.2f} MB")
        else:
            self.ProgressBar.setValue(0)
            self.file_size_label.setText("0 MB")

    def update_Downloading_info(self, file_name, file_size, file_type):
        self.file_name_label.setText(file_name)
        self.file_size_label.setText(file_size)
        self.file_type_label.setText(file_type)
