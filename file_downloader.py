import requests
from urllib.parse import urlparse, parse_qs, unquote
import os

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


import requests
import os

def Download_File(url, path, worker=None):
    """
    Download the file from the URL and save it to the specified path.
    The worker is used to check for cancellation.
    """
    response = requests.get(url, stream=True, verify=False)
    file_path = os.path.join(path)
    total_size = int(response.headers.get('Content-Length', 0))
    downloaded_size = 0

    with open(file_path, 'wb') as file:
        for chunk in response.iter_content(chunk_size=1024):
            if worker and worker.is_canceled:
                return  # Exit if canceled

            if chunk:
                file.write(chunk)
                downloaded_size += len(chunk)
                if total_size > 0:
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

    def run(self):
        try:
            # Pass the worker instance to the Download_File function
            Download_File(self.url, self.path, self)

            if not self.is_canceled:
                self.finished.emit()  # Notify that the download is complete
            else:
                self.canceled.emit()  # Notify that the download was canceled
        except Exception as e:
            print(f"An error occurred: {e}")
            self.finished.emit()

    def Cancel_Download(self):
        self.is_canceled = True  # Set the flag to cancel the download

