import os
from pathlib import Path

def generate_tree(start_path, ignore_dirs=None, ignore_files=None):
    if ignore_dirs is None:
        ignore_dirs = {'.git', '__pycache__', 'venv', 'env', '.idea', '.vscode', 'node_modules', 'django_env', 'media', 'static'}
    if ignore_files is None:
        ignore_files = {'.DS_Store', 'db.sqlite3', '*.pyc'}

    start_path = Path(start_path)
    
    print(f"{start_path.name}/")
    
    def _tree(directory, prefix=""):
        # Get all files and directories
        try:
            entries = list(directory.iterdir())
        except PermissionError:
            return

        # Filter entries
        entries = sorted(entries, key=lambda e: (not e.is_dir(), e.name.lower()))
        entries = [e for e in entries if e.name not in ignore_dirs and e.name not in ignore_files]
        
        count = len(entries)
        
        for index, entry in enumerate(entries):
            connector = "└── " if index == count - 1 else "├── "
            
            print(f"{prefix}{connector}{entry.name}")
            
            if entry.is_dir():
                extension = "    " if index == count - 1 else "│   "
                _tree(entry, prefix + extension)

    _tree(start_path)

if __name__ == "__main__":
    current_dir = os.getcwd()
    print(f"Generating tree structure for: {current_dir}\n")
    generate_tree(current_dir)
