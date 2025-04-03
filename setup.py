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

# Define app versioning by environment
APP_VERSION = {
    "Dev": "dev-latest",
    "Test": "test-latest",
    "Prod": "prod-latest"
}.get(AZURE_TAG_ENVIRONMENT, "dev-latest")

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

main_bicep_path = Path("infra/main.bicep")
main_bicep_lines = main_bicep_path.read_text().splitlines() if main_bicep_path.exists() else []

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
        image: 'ghcr.io/pdgeek-com/legendops/{app}:{APP_VERSION}'
      }}]
    }}
  }}
}}
""")
        print(f"  🧱 Generated {bicep_path}")

    module_include = f"module {app} './{app}.bicep' = {{ name: '{app}_module' }}"
    if module_include not in main_bicep_lines:
        main_bicep_lines.append(module_include)

# React Frontend
frontend_path = Path("frontend")
frontend_src = frontend_path / "src"
frontend_public = frontend_path / "public"
frontend_bicep = Path("infra/frontend.bicep")
frontend_env = frontend_path / ".env"

if not frontend_src.exists():
    frontend_src.mkdir(parents=True)
    (frontend_src / "index.js").write_text("console.log('LegendOps React loaded');")
    print("  🧱 Created frontend/src/index.js")

if not frontend_public.exists():
    frontend_public.mkdir(parents=True)
    (frontend_public / "index.html").write_text("""<!DOCTYPE html>
<html>
  <head><title>LegendOps</title></head>
  <body><div id='root'></div></body>
</html>
""")
    print("  🧱 Created frontend/public/index.html")

if not frontend_env.exists():
    frontend_env.write_text("REACT_APP_API_URL=http://localhost:5000\n")
    print("  ⚙️  Created frontend/.env")

if not frontend_bicep.exists():
    frontend_bicep.write_text(f"""// Frontend deployment as Azure Static Web App
resource frontend 'Microsoft.Web/staticSites@2022-03-01' = {{
  name: 'legendops-frontend'
  location: '{LOCATION}'
  sku: {{ name: 'Free' }}
  tags: {{
    Project: '{AZURE_TAG_PROJECT}'
    Environment: '{AZURE_TAG_ENVIRONMENT}'
    Owner: '{AZURE_TAG_OWNER}'
    CostCenter: '{AZURE_TAG_COSTCENTER}'
  }}
  properties: {{
    repositoryUrl: 'https://github.com/pdgeek-com/legendops'
    branch: 'main'
    buildProperties: {{
      appLocation: '/frontend'
      outputLocation: 'build'
    }}
  }}
}}
""")
    print("  🌐 Generated frontend.bicep")

frontend_module = "module frontend './frontend.bicep' = { name: 'frontend_module' }"
if frontend_module not in main_bicep_lines:
    main_bicep_lines.append(frontend_module)

# PostgreSQL Bicep
postgres_bicep = Path("infra/postgres.bicep")
if not postgres_bicep.exists():
    postgres_bicep.write_text(f"""// Azure Database for PostgreSQL Flexible Server
resource postgres 'Microsoft.DBforPostgreSQL/flexibleServers@2022-12-01' = {{
  name: 'legendops-pg'
  location: '{LOCATION}'
  tags: {{
    Project: '{AZURE_TAG_PROJECT}'
    Environment: '{AZURE_TAG_ENVIRONMENT}'
    Owner: '{AZURE_TAG_OWNER}'
    CostCenter: '{AZURE_TAG_COSTCENTER}'
  }}
  properties: {{
    administratorLogin: '{POSTGRES_USER}'
    administratorLoginPassword: '{POSTGRES_PASSWORD}'
    version: '15'
    storage: {{ storageSizeGB: 32 }}
    network: {{ publicNetworkAccess: 'Enabled' }}
  }}
  sku: {{ name: 'Standard_B1ms', tier: 'Burstable', capacity: 1 }}
}}
""")
    print("  🧱 Generated postgres.bicep")

pg_module = "module postgres './postgres.bicep' = { name: 'postgres_module' }"
if pg_module not in main_bicep_lines:
    main_bicep_lines.append(pg_module)

# Write back main.bicep
if main_bicep_lines:
    main_bicep_path.write_text("\n".join(main_bicep_lines))
    print("  🔗 Updated main.bicep with app + infra module includes")

print("\n✅ All database, app, web, and frontend scaffolding is complete.")