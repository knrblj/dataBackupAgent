import os
import uuid
import time
import urllib.parse
import requests
from datetime import datetime, timedelta

ZOHO_API_BASE_URL = "https://www.zohoapis.com/workdrive/api/v1"
ZOHO_UPLOAD_URL = "https://upload.zoho.com/workdrive-api/v1/stream/upload"
ZOHO_PROGRESS_URL = "https://www.zohoapis.com/workdrive/uploadprogress"

class WorkDriveUtil:
    def __init__(self, access_token,workdrive_folder_id,user_zuid):
        self.access_token = access_token
        self.workdrive_folder_id = workdrive_folder_id
        self.user_zuid = user_zuid

    def upload_large_file_stream(self, file_path):
        if not self.workdrive_folder_id:
            raise Exception("Folder ID not set. Please set the folder ID during initialization.")
        
        file_name = os.path.basename(file_path)
        encoded_file_name = urllib.parse.quote(file_name)

        upload_id = f"{uuid.uuid4()}"
        file_size = os.path.getsize(file_path)

        stream_headers = {
            "Authorization": f"Zoho-oauthtoken {self.access_token}",
            "Content-Type": "application/octet-stream",
            "x-filename": encoded_file_name,
            "x-parent_id": self.workdrive_folder_id,
            "upload-id": upload_id,
            "x-streammode": "1"
        }

        print(f"[INFO] Uploading '{file_name}' ({file_size / (1024 * 1024):.2f} MB) to WorkDrive...")

        with open(file_path, "rb") as f:
            upload_resp = requests.post(ZOHO_UPLOAD_URL, headers=stream_headers, data=f)

        if upload_resp.status_code != 200:
            print(f"[ERROR] Upload failed: {upload_resp.status_code}")
            print(upload_resp.text)
            return None
        
        for attempt in range(10):
            time.sleep(5)
            progress_resp = requests.get(
                ZOHO_PROGRESS_URL,
                headers={"Authorization": f"Zoho-oauthtoken {self.access_token}"},
                params={"uploadid": f"upload_{self.user_zuid}_{upload_id}"}
            )

            try:
                progress_data = progress_resp.json()
                status_code = progress_data["AUDIT_INFO"]["statusCode"]
            except Exception:
                print(f"[ERROR] Failed to parse progress response: {progress_resp.text}")
                break

            print(f"[INFO] Attempt {attempt + 1}: Upload status = {status_code}")

            if status_code == "D201":
                print("[SUCCESS] File uploaded successfully.")
                return progress_data["AUDIT_INFO"]
            elif status_code == "D9217":
                print("[INFO] Still in progress...")
                continue
            else:
                print(f"[ERROR] Upload failed or interrupted. Status: {status_code}")
                break

            print("[TIMEOUT] Upload status not confirmed after retries.")
            return None
        
    def get_files_in_folder(self):
        url = f"https://www.zohoapis.com/workdrive/api/v1/files/{self.workdrive_folder_id}/files"
        headers = {
            "Authorization": f"Zoho-oauthtoken {self.access_token}"
        }

        all_files = []
        next_url = url

        while next_url:
            response = requests.get(next_url, headers=headers)
            if response.status_code != 200:
                print(f"Failed to fetch files: {response.status_code} - {response.text}")
                break

            data = response.json()
            all_files.extend(data.get("data", []))
            next_url = data.get("meta", {}).get("next", None)

        return all_files

    def filter_old_files(self, files, days_old):
        cutoff = datetime.now() - timedelta(days=days_old)
        old_files = []

        for file in files:
            if file["attributes"].get("is_folder", False):
                continue  # Skip folders

            created_ms = int(file["attributes"]["created_time_in_millisecond"])
            created_dt = datetime.fromtimestamp(created_ms / 1000)

            if created_dt < cutoff:
                old_files.append({
                    "id": file["id"],
                    "name": file["attributes"]["name"],
                    "created": created_dt.strftime("%Y-%m-%d %H:%M:%S")
                })

        return old_files

    def delete_file(self, file_id):
        url = f"https://www.zohoapis.com/workdrive/api/v1/files/{file_id}"
        
        headers = {
            "Authorization": f"Zoho-oauthtoken {self.access_token}",
            "Content-Type": "application/json"
        }
        payload = {
            "data": {
                "attributes": {
                    "status": "51"
                },
                "type": "files"
            }
        }

        response = requests.patch(url, headers=headers, json=payload)
        return response.status_code in [200, 204]

