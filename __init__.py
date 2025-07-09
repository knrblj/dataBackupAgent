import os
from zipper import backup_folders_into_one_zip
from config_loader import load_config
from auth import generate_access_token
from workdrive_util import WorkDriveUtil
import SSHDeployer

if __name__ == "__main__":
    config = load_config()
    if not config:
        print("Failed to load configuration.")
        exit(1)
    
    # Code to backup folders into a single zip file
    folders_to_backup = config.get("folders_to_backup", [])
    if not folders_to_backup:
        print("No folders to backup specified in the configuration.")
        exit(1)
    
    try:
        final_zip_path = backup_folders_into_one_zip(folders_to_backup)
        print("Backup completed successfully." + f" Backup file created at: {final_zip_path}")
    except Exception as e:
        print(f"An error occurred during backup: {e}")
        exit(1)

    pushToWorkDrive = True
    workDriveConfig = config.get("workdrive", {})
    if not workDriveConfig or workDriveConfig.get("is_enabled", False) is not True:
        pushToWorkDrive = False

    
    pushToRemoteServer = True
    sshConfig = config.get("ssh_creds", {})
    if not sshConfig or sshConfig.get("is_enabled", False) is not True:
        pushToRemoteServer = False

    if pushToWorkDrive:
        zoho_config = workDriveConfig.get("zoho_secrets", {})

        access_token = None

        if not zoho_config:
            print("No Zoho configuration found in the configuration file.")
        else:
            try:
                access_token = generate_access_token(zoho_config)
            except Exception as e:
                print(f"An error occurred while generating access token: {e}")

        if not access_token:
            print("Failed to generate access token.")
        else:
            client = WorkDriveUtil(access_token, workDriveConfig.get("workdrive_folder_id", None),workDriveConfig.get("user_zuid", None))
            try:
                upload_info = client.upload_large_file_stream(final_zip_path)
                upload_info["resource"]["name"]
                upload_info["uploadId"]
                print(f"File successfully uploaded with file name {upload_info['resource']['name']} and upload ID {upload_info['uploadId']}.")
                
                delete_old_files = config.get("delete_old_files", True)
                if delete_old_files:
                    retention_period = config.get("retention_period", 5)
                    try:
                        files = client.get_files_in_folder()
                        old_files = client.filter_old_files(files, retention_period)
                        
                        for file in old_files:
                            client.delete_file(file["id"])
                            print(f"Deleted old file: {file['name']} (ID: {file['id']})")

                    except Exception as e:
                        print(f"An error occurred while deleting old files: {e}")

            except Exception as e:
                print(f"An error occurred while uploading file: {e}")

    
    if pushToRemoteServer:
        host = sshConfig.get("host_name", "")
        username = sshConfig.get("user_name", "")
        password = sshConfig.get("password", "")
        port = sshConfig.get("port", 22)

        try:
            deployer = SSHDeployer.SSHDeployer(
                host=host,
                port=port,
                username=username,
                password=password
            )

            deployer.connect()

            remote_dir = deployer.create_remote_dir("kb_backup")
            deployer.upload_file(final_zip_path, remote_dir)

            retention_period = config.get("retention_period", 5)
            deployer.cleanup_old_files(remote_dir, days=retention_period)
        except Exception as e:
            print(f"An error occurred while deploying to remote server: {e}")
        finally:
            deployer.close()
            print("SSH connection closed.")
    
    os.remove(final_zip_path)
