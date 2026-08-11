
import zipfile
import os

def create_zip_exclude_folders(zip_filename, source_folder, exclude_folders):
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(source_folder):
            # Exclude directories
            dirs[:] = [d for d in dirs if d not in exclude_folders and not d.startswith('.')]
            
            for file in files:
                if file.startswith('.') or file.endswith('.zip') or file.endswith('.pyc'):
                    continue
                    
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, source_folder)
                
                print(f"Adding {arcname}")
                zipf.write(file_path, arcname)

if __name__ == '__main__':
    source = r"d:\Desktop Projects 2025\bot_management_system"
    output = r"d:\Desktop Projects 2025\bot_management_system\deploy_manual.zip"
    excludes = ['django_env', 'venv', 'env', '.elasticbeanstalk', '.git', '__pycache__', 'media', 'staticfiles', '.vs', '.idea', 'node_modules']
    
    print(f"Creating {output}...")
    create_zip_exclude_folders(output, source, excludes)
    print("Done!")
    print(f"Size: {os.path.getsize(output) / (1024*1024):.2f} MB")
