import os
import uuid
import re
from dotenv import set_key, load_dotenv
from pathlib import Path
from getpass import getuser
import subprocess

infra_dir = Path("infra")
dotenv_path = infra_dir / ".env"

# Ensure .env exists
if not dotenv_path.exists():
    dotenv_path.write_text("")

load_dotenv(dotenv_path)

def update_env_value(path, key, value):
    if not os.getenv(key):
        set_key(str(path), key, value)
        print(f"🔧 Set {key} in .env")
    else:
        print(f"⚠️ {key} already exists in .env and was not overwritten")

def generate_password():
    return uuid.uuid4().hex[:16]

def set_default_env():
    defaults = {
        "RESOURCE_GROUP": "legendops-dev",
        "LOCATION": "eastus",
        "POSTGRES_USER": "legendops_user",
        "POSTGRES_PASSWORD": generate_password(),
        "POSTGRES_DB": "legendops",
        "KEYVAULT_NAME": "legendops-kv",
        "STORAGE_ACCOUNT": "legendopsstore",
        "LOG_ANALYTICS_WORKSPACE": "legendops-monitor",
        "AZURE_SUBSCRIPTION_ID": "",
        "AZURE_CLIENT_ID": "",
        "AZURE_TENANT_ID": "",
        "AZURE_TAG_PROJECT": "LegendOps",
        "AZURE_TAG_ENVIRONMENT": "Dev",
        "AZURE_TAG_OWNER": f"{getuser()}@pdgeek.com",
        "AZURE_TAG_COSTCENTER": "MSP-Infrastructure"
    }
    for key, value in defaults.items():
        update_env_value(dotenv_path, key, value)

def update_main_bicep():
    bicep_path = infra_dir / "main.bicep"
    if not bicep_path.exists():
        print("⚠️ main.bicep not found")
        return
    content = bicep_path.read_text()
    tag_block = """
param tags object = {
  Project: 'LegendOps'
  Environment: 'Dev'
  Owner: 'levi@pdgeek.com'
  CostCenter: 'MSP-Infrastructure'
}
"""
    if "param tags object" not in content:
        content = tag_block + "\n" + content
        bicep_path.write_text(content)
        print("🚀 main.bicep updated with new parameters")

def show_current_subscription():
    try:
        result = subprocess.run(["az", "account", "show", "--output", "json"], capture_output=True, text=True)
        if result.returncode == 0:
            print("\n📘 Current Azure Subscription:")
            print(result.stdout)
        else:
            print("⚠️ Unable to retrieve Azure subscription. Try 'az login'.")
    except FileNotFoundError:
        print("❌ Azure CLI not installed.")

def scaffold_gitignore():
    gitignore = Path(".gitignore")
    gitignore_content = """
# Python
__pycache__/
*.py[cod]
.venv/
*.env

# VS Code
.vscode/

# Logs
*.log
*.bak

# Docker
*.tar
.env.*

# Node
node_modules/
*.lock

# System
.DS_Store
Thumbs.db
"""
    if not gitignore.exists():
        gitignore.write_text(gitignore_content.strip())
        print("🛡️  .gitignore created")
    else:
        print("⚠️  .gitignore already exists")

def main():
    set_default_env()
    update_main_bicep()
    show_current_subscription()
    scaffold_gitignore()
    print("\n✅ Repo is now updated with base infrastructure config")
    print("📂 Check infra/.env and infra/*.bicep files")
    print("💡 Run 'git add .' and commit the changes")

if __name__ == "__main__":
    main()