# deploy.py
import os
import subprocess
from pathlib import Path

# Load environment variables from .env
from dotenv import load_dotenv
load_dotenv()

# Config
ENVIRONMENT = os.getenv("ENVIRONMENT", "dev")
LOCATION = os.getenv("LOCATION", "eastus")
RESOURCE_GROUP = f"legendops-{ENVIRONMENT}"
BICEP_FILE = "infra/main.bicep"

# Step 1: Create Resource Group
def create_resource_group():
    print(f"\n🔧 Creating resource group: {RESOURCE_GROUP} in {LOCATION}...")
    subprocess.run([
        "az", "group", "create",
        "--name", RESOURCE_GROUP,
        "--location", LOCATION
    ], check=True)

# Step 2: Deploy Bicep Template
def deploy_bicep():
    print(f"\n🚀 Deploying Bicep template: {BICEP_FILE}...")
    subprocess.run([
        "az", "deployment", "group", "create",
        "--resource-group", RESOURCE_GROUP,
        "--template-file", BICEP_FILE,
        "--parameters",
        f"environment={ENVIRONMENT}",
        f"location={LOCATION}",
        f"resourcePrefix=legendops"
    ], check=True)

# Step 3: GitHub push (optional)
def git_push():
    print("\n📦 Pushing changes to GitHub...")
    subprocess.run(["git", "add", "."], check=True)
    subprocess.run(["git", "commit", "-m", "Automated deploy + Bicep push"], check=False)
    subprocess.run(["git", "push", "origin", "main"], check=True)

# Main Runner
def main():
    create_resource_group()
    deploy_bicep()
    # Uncomment to auto-push
    # git_push()

if __name__ == "__main__":
    main()
