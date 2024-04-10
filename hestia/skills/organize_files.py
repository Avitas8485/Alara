import os
from shutil import move
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

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
    os.makedirs(os.path.join(root_dir, dir_name), exist_ok=True)

def organize_files():
    for file_name in os.listdir(root_dir):
        file_path = os.path.join(root_dir, file_name)
        if os.path.isfile(file_path) and not file_name.startswith('.') and not file_name == os.path.basename(__file__):
            file_ext = os.path.splitext(file_path)[1]
            for dir_name, extensions in file_types.items():
                if file_ext in extensions:
                    move(file_path, os.path.join(root_dir, dir_name, file_name))
                    break
            else:
                # If the file extension is not in the dictionary, move it to the 'others' directory
                move(file_path, os.path.join(root_dir, 'others', file_name))

class MyHandler(FileSystemEventHandler):
    def on_modified(self, event):
        organize_files()
        

if __name__ == "__main__":
    event_handler = MyHandler()
    observer = Observer()
    observer.schedule(event_handler, root_dir, recursive=True)
    observer.start()
    try:
        while True:
            pass
    except KeyboardInterrupt:
        observer.stop()
    observer.join()