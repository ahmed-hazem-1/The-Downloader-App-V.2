import requests
from urllib.parse import urlparse, parse_qs, unquote
import os
import time
from PyQt5.QtCore import pyqtSignal, QThread
import UI_Pages_PY.Downloading_UI_Page as DP
import Utils.utils as UT


def Get_File_Info(url):
    """
    Get the file name, file type and file size from the url
    """
    response = requests.head(url, allow_redirects=True, verify=False)  # request the link to get the header

    if response.status_code != 200:
        response = requests.get(url, stream=True, verify=False)

    # Get the file name
    if 'Content-Disposition' in response.headers:
        content_disposition = response.headers['Content-Disposition']
        file_name = content_disposition.split('filename=')[1].strip('"')
    else:
        parsed_url = urlparse(url)
        file_name = os.path.basename(parsed_url.path)
        file_name = unquote(file_name)  # Decode any URL-encoded characters

    # Get the file size
    file_size = UT.size_convertor(int(response.headers.get('Content-Length', 0)))

    # Get the file type
    file_type = response.headers.get('Content-Type', 'Unknown')

    return file_name, file_size, file_type


# ui_helpers.py
def Set_File_Info(ui, file_name, file_size, file_type):
    """
    Set the file name, file type, and file size on any UI
    """
    if hasattr(ui, 'file_name_label'):
        ui.file_name_label.setText(file_name)
    if hasattr(ui, 'file_size_label'):
        ui.file_size_label.setText(file_size)
    if hasattr(ui, 'file_type_label'):
        ui.file_type_label.setText(file_type)


def Download_File(url, path, worker=None, resume_byte_pos=0):
    """
    Download the file from the URL and save it to the specified path.
    The worker is used to check for pause/resume/cancellation.
    Supports resuming downloads using resume_byte_pos.
    """
    headers = {}
    if resume_byte_pos > 0:
        headers['Range'] = f'bytes={resume_byte_pos}-'

    response = requests.get(url, stream=True, headers=headers, verify=False)
    total_size = int(response.headers.get('Content-Length', 0)) + resume_byte_pos
    downloaded_size = resume_byte_pos

    # Open the file in append mode if resuming
    mode = 'ab' if resume_byte_pos > 0 else 'wb'
    file_path = os.path.join(path)

    with open(file_path, mode) as file:
        for chunk in response.iter_content(chunk_size=1024):
            # Check for cancellation
            if worker and worker.is_canceled:
                break  # Exit if canceled

            # Check for pause
            while worker.is_paused:
                time.sleep(0.1)  # Sleep for a while until resumed

            if chunk:
                file.write(chunk)
                downloaded_size += len(chunk)
                print(f"Downloaded: {downloaded_size} / {total_size}")
                if total_size > 0 and worker:
                    worker.progress.emit(downloaded_size, total_size)  # Emit progress


class DownloadWorker(QThread):
    progress = pyqtSignal(int, int)  # Emit both file_size and total_size
    finished = pyqtSignal()
    canceled = pyqtSignal()  # Add a signal for cancellation

    def __init__(self, url, path, parent=None):
        super().__init__(parent)
        self.url = url
        self.path = path
        self.is_canceled = False  # Initialize cancellation flag
        self.is_paused = False  # Initialize pause flag
        self.downloaded_size = 0  # Store downloaded size for resuming

    def run(self):
        try:
            # Check if the file already exists and get its size (resume case)
            if os.path.exists(self.path):
                self.downloaded_size = os.path.getsize(self.path)

            # Pass the worker instance and resume byte position to the Download_File function
            Download_File(self.url, self.path, self, self.downloaded_size)

            if not self.is_canceled:
                self.finished.emit()  # Notify that the download is complete
            else:
                self.canceled.emit()  # Notify that the download was canceled
        except Exception as e:
            print(f"An error occurred: {e}")
            self.finished.emit()

    def Cancel_Download(self):
        self.is_canceled = True  # Set the flag to cancel the download

    def Pause_Download(self):
        self.is_paused = True  # Set the flag to pause the download

    def Resume_Download(self):
        self.is_paused = False  # Clear the pause flag
        # The run method will continue from where it paused, no need to restart the download process
