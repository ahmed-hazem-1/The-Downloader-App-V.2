# downloading_page.py
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QDialog, QLabel, QProgressBar, QLineEdit, QFileDialog
from PyQt5.uic import loadUiType
import os

DownloadingPage_UI, _ = loadUiType(os.path.join(os.path.dirname(__file__), "../UIs/Downloading_page.ui"))

class DownloadingPage(QDialog, DownloadingPage_UI):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        # Initialize UI elements
        self.file_name_label = self.findChild(QLabel, 'FileName_2')
        self.file_size_label = self.findChild(QLabel, 'FileSize_2')
        self.file_type_label = self.findChild(QLabel, 'FileType')
        self.ProgressBar = self.findChild(QProgressBar, 'ProgressBar')  # Changed to 'ProgressBar'
        print("DownloadingPage initialized successfully.")
        self.Handle_Buttons()
        self.file_name_label.setText("No file selected")
        self.file_size_label.setText("0 MB")
        self.file_type_label.setText("Unknown")

    def Handle_Buttons(self):
        self.CloseButton.clicked.connect(self.close)
        self.CloseButton.clicked.connect(self.Cancel_Download)  # Connect the cancel button to the method

    def Cancel_Download(self):
        if hasattr(self, 'worker') and self.worker.isRunning():
            self.worker.Cancel_Download()  # Call the Cancel_Download method in the worker

    @pyqtSlot(int, int)
    def progress(self, file_size, total_size):
        if total_size > 0:
            percentage = (file_size / total_size) * 100
            print(f"Progress: {percentage:.2f}%")
            self.ProgressBar.setValue(int(percentage))
            self.file_size_label.setText(f"{file_size / (1024 * 1024):.2f} MB of {total_size / (1024 * 1024):.2f} MB")
        else:
            self.ProgressBar.setValue(0)
            self.file_size_label.setText("0 MB")

    def update_Downloading_info(self, file_name, file_size, file_type):
        self.file_name_label.setText(file_name)
        self.file_size_label.setText(file_size)
        self.file_type_label.setText(file_type)