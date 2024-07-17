#gets the file path from user via a popup dialogue. repeatedly asks input if it is mistyped.
# Created by Sayaka (Saya) Minegishi with the help of chatgpt
#last modified: June 19 2024
from PyQt5.QtWidgets import QApplication, QFileDialog, QMessageBox
import os


def get_file_path():
    options = QFileDialog.Options()
    while True:
        # Open the file dialog and allow the user to select only one file
        file_path, _ = QFileDialog.getOpenFileName(None, "Select a file", "", "ABF Files (*.abf);;All Files (*)", options=options)
        
        # Check if a file path was selected
        if file_path:
            # Additional validation can be done here if needed
            return file_path
        else:
            # Show an error message if no file was selected and re-prompt the user
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setText("No file selected. Please select a file.")
            msg.setWindowTitle("Warning")
            msg.exec_()


#to select multiple files
def get_file_paths():
    options = QFileDialog.Options()
    file_paths, _ = QFileDialog.getOpenFileNames(None, "Select files", "", "ABF Files (*.abf);;All Files (*)", options=options)

    print(f"Selected files: {file_paths}")

    # Check if a file path was selected
    if file_paths:
        # Sort the selected file paths alphabetically
        sorted_file_paths = sorted(file_paths)
        
        
        return file_paths
    else:
        # Show an error message if no file was selected and re-prompt the user
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setText("No file selected. Please select a file.")
        msg.setWindowTitle("Warning")
        msg.exec_()

#function that gives only the file name portion (with .abf extension)
def get_only_filename(filepath):
    # Get only the file names (part after the last /)
    filename = os.path.basename(filepath)
    return filename




