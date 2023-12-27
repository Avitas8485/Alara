import os
from shutil import move
from pathlib import Path

root_dir = Path(os.path.expanduser('~')) / 'Downloads'

# Create a dictionary to map file extensions to their respective directories
file_types = {
    'docs': ('.docx', '.doc',  '.txt', '.pdf', '.xls', '.ppt', '.xlsx', '.pptx'),
    'images': ('.jpg', '.jpeg', '.png', '.svg', '.tif', '.tiff', '.gif'),
    'softwares': ('.exe', '.dmg', '.pkg'),
    'others': ()
}

# Create directories if they don't exist
for dir_name in file_types.keys():
    (root_dir / dir_name).mkdir(parents=True, exist_ok=True)

# Move files to the respective folders, overwriting if needed
for file_name in os.listdir(root_dir):
    file_path = root_dir / file_name
    if file_path.is_file() and not file_name.startswith('.') and not file_name == __file__:
        file_ext = file_path.suffix
        for dir_name, extensions in file_types.items():
            if file_ext in extensions:
                move(str(file_path), str(root_dir / dir_name / file_name))
                break
        else:
            # If the file extension is not in the dictionary, move it to the 'others' directory
            move(str(file_path), str(root_dir / 'others' / file_name))