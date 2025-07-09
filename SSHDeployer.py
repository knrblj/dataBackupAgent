import paramiko
import os
from datetime import datetime, timezone


class SSHDeployer:
    def __init__(self, host, port, username, password=None, key_path=None):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.key_path = key_path
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    def connect(self):
        if self.key_path:
            self.ssh.connect(hostname=self.host, username=self.username, key_filename=self.key_path)
        else:
            self.ssh.connect(hostname=self.host, port=self.port, username=self.username, password=self.password)
        self.sftp = self.ssh.open_sftp()

    def get_remote_time(self):
        stdin, stdout, stderr = self.ssh.exec_command("date +%s")
        remote_ts = int(stdout.read().decode().strip())
        return datetime.fromtimestamp(remote_ts, timezone.utc)

    def create_remote_dir(self, dirname):
        home_dir = self.sftp.normalize('.')
        target_dir = f"{home_dir}/{dirname}"
        try:
            self.sftp.listdir(target_dir)
            print(f"Directory already exists: {target_dir}")
        except IOError:
            self.sftp.mkdir(target_dir)
            print(f"Directory created: {target_dir}")
        return target_dir

    def upload_file(self, local_file, remote_dir):
        basename = os.path.basename(local_file)
        remote_path = f"{remote_dir}/{basename}"
        self.sftp.put(local_file, remote_path)
        print(f"Uploaded: {local_file} → {remote_path}")

    def cleanup_old_files(self, remote_dir, days=5):
        now = self.get_remote_time()
        cutoff_seconds = days * 86400

        for filename in self.sftp.listdir(remote_dir):
            file_path = f"{remote_dir}/{filename}"
            attr = self.sftp.stat(file_path)
            file_time = datetime.fromtimestamp(attr.st_mtime, timezone.utc)
            age_seconds = (now - file_time).total_seconds()

            if age_seconds > cutoff_seconds:
                self.sftp.remove(file_path)
                print(f"Deleted old file: {file_path}")

    def close(self):
        self.sftp.close()
        self.ssh.close()

"""

REMOTE_DIR = "my_uploads"
LOCAL_FILE = "example.txt"  # replace this with your file
DAYS = 5

deployer = SSHDeployer(
    host="your.remote.host",
    username="youruser",
    password="yourpass"  # or use key_path="~/.ssh/id_rsa"
)

deployer.connect()

remote_path = deployer.create_remote_dir(REMOTE_DIR)
deployer.upload_file(LOCAL_FILE, remote_path)
deployer.cleanup_old_files(remote_path, days=DAYS)

deployer.close()

"""