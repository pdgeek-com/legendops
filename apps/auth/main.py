import os
from pathlib import Path
from dotenv import load_dotenv
import json

# Load environment variables from infra/.env
env_path = Path("infra/.env")
load_dotenv(dotenv_path=env_path)

# Set variables from .env
RESOURCE_GROUP = os.getenv("RESOURCE_GROUP")
LOCATION = os.getenv("LOCATION")
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_DB = os.getenv("POSTGRES_DB")
AZURE_SUBSCRIPTION_ID = os.getenv("AZURE_SUBSCRIPTION_ID")
AZURE_TAG_PROJECT = os.getenv("AZURE_TAG_PROJECT")
AZURE_TAG_ENVIRONMENT = os.getenv("AZURE_TAG_ENVIRONMENT")
AZURE_TAG_OWNER = os.getenv("AZURE_TAG_OWNER")
AZURE_TAG_COSTCENTER = os.getenv("AZURE_TAG_COSTCENTER")

# Ensure required DB directories and schema.sql files exist
print("🔍 Checking database directories and scaffolding missing schemas...")
db_dirs = ["auth_db", "billing_db", "portal_db", "catalog_db"]
base_db_path = Path("db")

for db_name in db_dirs:
    db_path = base_db_path / db_name
    db_path.mkdir(parents=True, exist_ok=True)
    schema_path = db_path / "schema.sql"
    config_path = db_path / "config.json"

    if not schema_path.exists():
        schema_path.write_text(f"-- Schema for {db_name}\nCREATE SCHEMA IF NOT EXISTS {db_name};")
        print(f"  🏗️ Scaffolded {schema_path}")
    else:
        print(f"  ✅ Found {schema_path}")

    if not config_path.exists():
        config_content = {
            "db_name": db_name,
            "user": POSTGRES_USER,
            "password": POSTGRES_PASSWORD,
            "host": "localhost",
            "port": 5432
        }
        with open(config_path, "w") as f:
            json.dump(config_content, f, indent=2)
        print(f"  🏗️ Created config template for {db_name}")
    else:
        print(f"  ✅ Found config for {db_name}")

# Scaffold basic app folders for microservices
print("\n🔧 Scaffolding app service folders...")
app_services = ["web", "auth", "billing", "catalog"]
base_app_path = Path("apps")

for app in app_services:
    app_path = base_app_path / app
    app_path.mkdir(parents=True, exist_ok=True)
    main_path = app_path / "main.py"
    requirements_path = app_path / "requirements.txt"
    bicep_path = Path("infra") / f"{app}.bicep"

    if not main_path.exists():
        main_path.write_text(f"""from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return 'Hello from {app}!'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
""")
        print(f"  🚀 Scaffolded {main_path}")
    else:
        print(f"  ✅ Found {main_path}")

    if not requirements_path.exists():
        requirements_path.write_text("flask\n")
        print(f"  📦 Created {requirements_path}")

    if not bicep_path.exists():
        bicep_path.write_text(f"""// {app} Bicep module
resource {app} 'Microsoft.Web/containerApps@2022-03-01' = {{
  name: '{app}-app'
  location: '{LOCATION}'
  tags: {{
    Project: '{AZURE_TAG_PROJECT}'
    Environment: '{AZURE_TAG_ENVIRONMENT}'
    Owner: '{AZURE_TAG_OWNER}'
    CostCenter: '{AZURE_TAG_COSTCENTER}'
  }}
  properties: {{
    kubeEnvironmentId: '' // Provide environment
    configuration: {{
      ingress: {{ external: true, targetPort: 5000 }}
    }}
    template: {{
      containers: [{{
        name: '{app}'
        image: 'ghcr.io/pdgeek-com/legendops/{app}:latest'
      }}]
    }}
  }}
}}
""")
        print(f"  🧱 Generated {bicep_path}")

print("\n✅ All database, app, and web service scaffolding is complete.")