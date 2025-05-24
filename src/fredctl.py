import argparse
import subprocess
import os
from datetime import datetime

LOG_PATH = 'logs/fredctl-log.txt'

def log(msg):
    print(msg)
    with open(LOG_PATH, 'a') as f:
        f.write(f"{datetime.now().isoformat()} - {msg}\n")

def run_script(script_name):
    if not os.path.exists(script_name):
        log(f"⚠️ Script {script_name} not found.")
        return
    log(f"▶️ Running {script_name} ...")
    subprocess.run(['python3', script_name])

def main():
    parser = argparse.ArgumentParser(description="Fred AI Ops Controller")
    parser.add_argument('--audit', action='store_true', help="Run ops-assist.py audit")
    parser.add_argument('--delete-junk', action='store_true', help="List junk projects (manual deletion recommended)")
    parser.add_argument('--assign-roles', action='store_true', help="Assign roles based on IAM policy")
    parser.add_argument('--sync-drive', action='store_true', help="Sync logs or config with Google Drive (future)")
    args = parser.parse_args()

    if args.audit:
        run_script('ops-assist.py')
    elif args.delete_junk:
        log("🚨 Dry-run only: To delete junk projects, manually execute gcloud CLI commands")
    elif args.assign_roles:
        log("🚧 Role assignment feature not yet implemented")
    elif args.sync_drive:
        log("🚧 Drive sync not yet implemented")
    else:
        parser.print_help()

if __name__ == "__main__":
    os.makedirs('logs', exist_ok=True)
    log("💡 fredctl.py started")
    main()