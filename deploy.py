import os
import subprocess
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from infra/.env
env_path = Path("infra/.env")
load_dotenv(dotenv_path=env_path)

# Ensure Azure CLI is logged in
print("🔐 Verifying Azure CLI login...")
subprocess.run(["az", "account", "show"], check=True)

# Set variables from .env
RESOURCE_GROUP = os.getenv("RESOURCE_GROUP")
LOCATION = os.getenv("LOCATION")
SUBSCRIPTION_ID = os.getenv("AZURE_SUBSCRIPTION_ID")

# Ensure correct subscription
print(f"📌 Setting subscription to {SUBSCRIPTION_ID}")
subprocess.run(["az", "account", "set", "--subscription", SUBSCRIPTION_ID], check=True)

# Create resource group if it doesn't exist
print(f"📁 Creating resource group: {RESOURCE_GROUP}")
subprocess.run([
    "az", "group", "create",
    "--name", RESOURCE_GROUP,
    "--location", LOCATION
], check=True)

# Deploy the Bicep infrastructure
print("🚀 Deploying infrastructure with Bicep...")
subprocess.run([
    "az", "deployment", "group", "create",
    "--resource-group", RESOURCE_GROUP,
    "--template-file", "infra/main.bicep",
    "--parameters", f"@infra/.env"
], check=True)

print("✅ Azure infrastructure deployed successfully.")