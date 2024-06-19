#gets the file path from user via a popup dialogue. repeatedly asks input if it is mistyped.
# Created using chatgpt
#last modified: June 19 2024
from PyQt5.QtWidgets import QApplication, QFileDialog, QMessageBox

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