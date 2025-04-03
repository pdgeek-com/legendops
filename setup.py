#!/usr/bin/env python3

import os
from pathlib import Path
from dotenv import load_dotenv
import json

# Load environment variables from infra/.env
env_path = Path("infra/.env")
if not env_path.exists():
    print("⚠️  No infra/.env found, creating a blank one.")
    env_path.write_text("")
load_dotenv(dotenv_path=env_path)

# Pull in environment values
RESOURCE_GROUP         = os.getenv("RESOURCE_GROUP", "legendops-dev")
LOCATION              = os.getenv("LOCATION", "eastus")
POSTGRES_USER         = os.getenv("POSTGRES_USER", "legendops_user")
POSTGRES_PASSWORD     = os.getenv("POSTGRES_PASSWORD", "ChangeMe123!")
POSTGRES_DB           = os.getenv("POSTGRES_DB", "legendops")
AZURE_SUBSCRIPTION_ID = os.getenv("AZURE_SUBSCRIPTION_ID", "")
AZURE_TAG_PROJECT     = os.getenv("AZURE_TAG_PROJECT", "LegendOps")
AZURE_TAG_ENVIRONMENT = os.getenv("AZURE_TAG_ENVIRONMENT", "Dev")
AZURE_TAG_OWNER       = os.getenv("AZURE_TAG_OWNER", "someone@domain.com")
AZURE_TAG_COSTCENTER  = os.getenv("AZURE_TAG_COSTCENTER", "MSP-Infrastructure")

# Define app versioning by environment
APP_VERSION = {
    "Dev":  "dev-latest",
    "Test": "test-latest",
    "Prod": "prod-latest"
}.get(AZURE_TAG_ENVIRONMENT, "dev-latest")

##################################################################
# 1. SCAFFOLD DB FOLDERS + SCHEMA.SQL
##################################################################

print("🔎 Checking database directories and scaffolding missing schemas...")
db_dirs = ["auth_db", "billing_db", "portal_db", "catalog_db"]
base_db_path = Path("db")

for db_name in db_dirs:
    db_path = base_db_path / db_name
    db_path.mkdir(parents=True, exist_ok=True)

    schema_path = db_path / "schema.sql"
    config_path = db_path / "config.json"

    if not schema_path.exists():
        schema_content = (
            f"-- Schema for {db_name}\n"
            f"CREATE SCHEMA IF NOT EXISTS {db_name};\n"
        )
        schema_path.write_text(schema_content)
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

##################################################################
# 2. SCAFFOLD BACKEND MICROSERVICES
##################################################################

print("\n🔧 Scaffolding app service folders...")
app_services = ["web", "auth", "billing", "catalog"]
base_app_path = Path("apps")

main_bicep_path = Path("infra/main.bicep")
if main_bicep_path.exists():
    main_bicep_lines = main_bicep_path.read_text().splitlines()
else:
    main_bicep_lines = []

for app in app_services:
    app_path = base_app_path / app
    app_path.mkdir(parents=True, exist_ok=True)
    main_path = app_path / "main.py"
    requirements_path = app_path / "requirements.txt"
    bicep_path = Path("infra") / f"{app}.bicep"

    # Python code for each service
    if not main_path.exists():
        main_py = f"""from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return 'Hello from {app}!'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
"""
        main_path.write_text(main_py)
        print(f"  🚀 Scaffolded {main_path}")
    else:
        print(f"  ✅ Found {main_path}")

    # Requirements
    if not requirements_path.exists():
        requirements_path.write_text("flask\n")
        print(f"  📦 Created {requirements_path}")

    # Bicep module for Azure Container Apps
    if not bicep_path.exists():
        container_bicep = f"""// {app} Bicep module
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
        image: 'ghcr.io/pdgeek-com/legendops/{app}:{APP_VERSION}'
      }}]
    }}
  }}
}}
"""
        bicep_path.write_text(container_bicep)
        print(f"  🧱 Generated {bicep_path}")

    module_include = f"module {app} './{app}.bicep' = {{ name: '{app}_module' }}"
    if module_include not in main_bicep_lines:
        main_bicep_lines.append(module_include)

##################################################################
# 3. SCAFFOLD REACT FRONTEND FOR AZURE STATIC WEB APPS
##################################################################

frontend_path = Path("frontend")
frontend_src = frontend_path / "src"
frontend_public = frontend_path / "public"
frontend_bicep_path = Path("infra/frontend.bicep")

if not frontend_path.exists():
    frontend_path.mkdir(parents=True, exist_ok=True)
    frontend_src.mkdir(parents=True, exist_ok=True)
    frontend_public.mkdir(parents=True, exist_ok=True)
    print("\n🎨 Scaffolding frontend React app for Azure Static Web Apps...")

    (frontend_src / "index.jsx").write_text(
        """import React from 'react';
import ReactDOM from 'react-dom/client';

const App = () => <h1>Hello from LegendOps Frontend</h1>;

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(<App />);
""")

    (frontend_public / "index.html").write_text(
        """<!DOCTYPE html>
<html>
  <head><title>LegendOps</title></head>
  <body><div id='root'></div></body>
</html>
""")

    # Basic package.json with SWA style build commands
    (frontend_path / "package.json").write_text(
        """{
  "name": "legendops-frontend",
  "version": "1.0.0",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0"
  },
  "devDependencies": {
    "vite": "^4.0.0"
  }
}
""")

    print("  🚀 Frontend scaffolded with React + Vite (no Docker)")

if not frontend_bicep_path.exists():
    static_web_bicep = f"""// Azure Static Web App
resource frontend 'Microsoft.Web/staticSites@2022-03-01' = {{
  name: 'legendops-frontend'
  location: '{LOCATION}'
  tags: {{
    Project: '{AZURE_TAG_PROJECT}'
    Environment: '{AZURE_TAG_ENVIRONMENT}'
    Owner: '{AZURE_TAG_OWNER}'
    CostCenter: '{AZURE_TAG_COSTCENTER}'
  }}
  properties: {{
    repositoryUrl: '' // Add GitHub repo link if needed
    branch: 'main'
    buildProperties: {{
      appLocation: 'frontend',
      outputLocation: 'dist'
    }}
  }}
}}
"""
    frontend_bicep_path.write_text(static_web_bicep)
    print("  🧱 Generated infra/frontend.bicep")

frontend_include = "module frontend './frontend.bicep' = { name: 'frontend_module' }"
if frontend_include not in main_bicep_lines:
    main_bicep_lines.append(frontend_include)

##################################################################
# 4. WRITE BACK main.bicep
##################################################################
if main_bicep_lines:
    main_bicep_path.write_text("\n".join(main_bicep_lines))
    print("  🔗 Updated main.bicep with app + infra module includes")

##################################################################
# FINAL MESSAGE
##################################################################
print("\n✅ All backend and frontend services scaffolded and integrated.")
