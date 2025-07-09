import os
import zipfile
import shutil
from datetime import datetime

BASE_BACKUP_TEMP_DIR = os.path.expanduser("~/kb_backups")
TIMESTAMP_FORMAT = "%Y%m%d_%H%M%S"

def create_dir(path):
    os.makedirs(path, exist_ok=True)
    return path


def is_hidden(path):
    return any(part.startswith('.') for part in path.split(os.sep) if part)


def zip_directory(source_dir, output_zip):
    with zipfile.ZipFile(output_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(source_dir):
            dirs[:] = [d for d in dirs if not is_hidden(os.path.join(root, d))]

            files = [f for f in files if not is_hidden(os.path.join(root, f))]

            if not files and not dirs:
                rel_path = os.path.relpath(root, source_dir) + '/'
                zipf.writestr(rel_path, '')

            for file in files:
                abs_path = os.path.join(root, file)
                rel_path = os.path.relpath(abs_path, source_dir)
                zipf.write(abs_path, arcname=rel_path)

def zip_folder(source_path, output_zip_path):
    with zipfile.ZipFile(output_zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(source_path):
            dirs[:] = [d for d in dirs if not is_hidden(os.path.join(root, d))]
            files = [f for f in files if not is_hidden(os.path.join(root, f))]

            if not files and not dirs:
                rel_path = os.path.relpath(root, source_path) + '/'
                zipf.writestr(rel_path, '')

            for file in files:
                abs_path = os.path.join(root, file)
                rel_path = os.path.relpath(abs_path, source_path)
                zipf.write(abs_path, arcname=rel_path)

def backup_folders_into_one_zip(folders):
    timestamp = datetime.now().strftime(TIMESTAMP_FORMAT)

    create_dir(BASE_BACKUP_TEMP_DIR)
    root_backup_dir = os.path.join(BASE_BACKUP_TEMP_DIR, f"LapBackup_{timestamp}")
    create_dir(root_backup_dir)

    valid_folders = 0

    for folder in folders:
        if not os.path.exists(folder) or not os.path.isdir(folder):
            print(f"[WARN] Skipping non-existent folder: {folder}")
            continue

        folder_name = os.path.basename(folder.rstrip("/"))
        zip_name = f"{folder_name}_{timestamp}.zip"
        zip_path = os.path.join(root_backup_dir, zip_name)

        try:
            zip_directory(folder, zip_path)
            print(f"[INFO] Zipped {folder} -> {zip_path}")
            valid_folders += 1
        except Exception as e:
            print(f"[ERROR] Failed to zip {folder}: {e}")

    if valid_folders == 0:
        print("[ERROR] No valid folders to backup. Aborting.")
        try:
            shutil.rmtree(root_backup_dir, ignore_errors=True)
        except Exception as cleanup_error:
            print(f"[WARN] Cleanup failed for {root_backup_dir}: {cleanup_error}")
        return None

    final_zip_path = os.path.join(BASE_BACKUP_TEMP_DIR, f"LapBackup_{timestamp}.zip")
    try:
        zip_folder(root_backup_dir, final_zip_path)
        print(f"[SUCCESS] Final backup: {final_zip_path}")
    except Exception as e:
        print(f"[ERROR] Failed to create final zip: {e}")
        final_zip_path = None

    shutil.rmtree(root_backup_dir, ignore_errors=True)
    return final_zip_path