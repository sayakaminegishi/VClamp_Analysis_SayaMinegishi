#remove .abf extension from filename
#created Jun 19 2024 with chatgpt

import os

def remove_abf_extension(filename):
    name_without_extension = os.path.splitext(os.path.basename(filename))[0]
    return name_without_extension

# # Example usage:
# filename = "example_file.abf"
# new_filename = remove_abf_extension(filename)
# print(new_filename)  # Output: example_file