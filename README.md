# 🚀 dataBackupAgent

A Python-based backup automation tool to:

- Zip and back up multiple folders
- Upload the backup to Zoho WorkDrive (optional)
- Upload the backup to a remote server via SSH (optional)
- Automatically delete old backups based on a retention policy
- Schedule daily backups with cron

---

## 📦 Features

- 📁 Backup multiple folders into a single `.zip` file
- ☁️ Optional upload to [Zoho WorkDrive](https://www.zoho.com/workdrive/)
- 🖥️ Optional upload to remote server via SSH/SFTP
- ♻️ Retention policy to delete old backups automatically
- ⏱️ Schedule daily backups with cron (default: 11:00 AM)

---

## 📁 Project Structure

```
your-project/
├── __init__.py             # Main script (entry point)
├── config.json             # Configuration file
├── zipper.py               # Zips multiple folders
├── workdrive_util.py       # Handles WorkDrive uploads
├── auth.py                 # Generates Zoho access token
├── config_loader.py        # Loads and validates config
├── SSHDeployer.py          # SSH-based remote upload and cleanup
├── setup_cron.sh           # Registers a cron job for daily backup
├── backup.log              # Log file output
├── requirements.txt        # Python dependencies
```

---

## ⚙️ Configuration

Edit `config.json` to set up folders, credentials, and behavior:

```json
{
  "folders_to_backup": [
    "/path/to/folder1",
    "/path/to/folder2"
  ],
  "workdrive": {
    "is_enabled": true,
    "workdrive_folder_id": "YOUR_WORKDRIVE_FOLDER_ID",
    "user_zuid": "YOUR_USER_ZUID",
    "zoho_secrets": {
      "client_id": "YOUR_CLIENT_ID",
      "client_secret": "YOUR_CLIENT_SECRET",
      "refresh_token": "YOUR_REFRESH_TOKEN"
    }
  },
  "ssh_creds": {
    "is_enabled": true,
    "host_name": "your.server.com",
    "port": 22,
    "user_name": "your_username",
    "password": "your_password"
  },
  "delete_old_files": true,
  "retention_period": 5
}
```

> 📌 Disable any section by setting `"is_enabled": false`.

---

## 📋 Requirements

Install dependencies using:

```bash
python3 -m pip install -r requirements.txt
```

**requirements.txt:**
```
requests==2.31.0
paramiko==2.12.0
```

## 🚀 Running Manually

```bash
python3 __init__.py
```

---

## ⏰ Schedule Daily Backup (11:00 AM)

Register a cron job using:

```bash
chmod +x setup_cron.sh
./setup_cron.sh
```

> 🕒 This will set up a cron job that runs your script every day at 11:00 AM and logs output to `backup.log`.


## ✅ Output

- A `.zip` backup file containing all specified folders
- Upload to Zoho WorkDrive (if enabled)
- Upload to remote server (`kb_backup/` directory)
- Old backups cleaned up based on retention policy
- All logs written to `backup.log`

---

## 👨‍💻 Author

Built by **Balaji Koneru**  

---

## 📬 Feedback & Ideas

Feel free to submit suggestions, issues, or contributions.  
This project is built with security, reliability, and automation in mind.
