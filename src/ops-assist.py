import os
import json
from datetime import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build

SERVICE_ACCOUNT_FILE = 'creds/ai-ops.json'
SCOPES = ['https://www.googleapis.com/auth/cloud-platform']
LOG_PATH = 'logs/audit-log.txt'
POLICY_PATH = 'policies/dynamic_iam_policy.json'

def log(message):
    print(message)
    with open(LOG_PATH, 'a') as f:
        f.write(f"{datetime.now().isoformat()} - {message}\n")

# Create logs directory if missing
os.makedirs('logs', exist_ok=True)
log("\n🚀 Starting Fred AI Ops Audit...")

# Authenticate
credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES
)
crm = build('cloudresourcemanager', 'v1', credentials=credentials)

# Load policy (optional)
policy_data = {}
if os.path.exists(POLICY_PATH):
    with open(POLICY_PATH) as f:
        policy_data = json.load(f)
        log(f"✅ Loaded IAM policy: {POLICY_PATH} with {len(policy_data.get('projects', []))} definitions")
else:
    log("⚠️ No policy file found — skipping enforcement")

# Pull projects
log("🔍 Fetching project list...")
projects = crm.projects().list().execute().get('projects', [])
log(f"📊 Total projects found: {len(projects)}")

# Audit
junk = []
for project in projects:
    name = project.get('name', '')
    pid = project['projectId']
    if 'Untitled' in name or name.startswith('Copy of'):
        junk.append(pid)
        log(f"❌ Junk Project: {pid} ({name})")
    else:
        log(f"✅ Project: {pid} ({name})")

log(f"🧹 Total junk projects: {len(junk)}")
log("✅ Audit complete. No changes made.")