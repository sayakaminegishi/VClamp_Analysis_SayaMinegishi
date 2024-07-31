import os
def get_base_filename(pathname):
    path = pathname
    filename = os.path.basename(path) #gets the file name portion only, discarding rest of directory path
    return filename
