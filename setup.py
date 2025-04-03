import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from infra/.env
env_path = Path("infra/.env")
load_dotenv(dotenv_path=env_path)

# Set variables from .env
RESOURCE_GROUP = os.getenv("RESOURCE_GROUP")
LOCATION = os.getenv("LOCATION")
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_DB = os.getenv("POSTGRES_DB")

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
        import json
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
    if not main_path.exists():
        main_path.write_text("""from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return f'Hello from {__name__}!'

if __name__ == '__main__':
    app.run(debug=True)
""")
        print(f"  🚀 Scaffolded {main_path}")
    else:
        print(f"  ✅ Found {main_path}")

print("\n✅ All database and app scaffolding is complete.")
