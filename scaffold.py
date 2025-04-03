import os

directories = [
    ".github/workflows",
    "apps/web",
    "apps/billing",
    "apps/auth",
    "apps/catalog",
    "db/auth_db",
    "db/billing_db",
    "db/portal_db",
    "db/catalog_db",
    "frontend/public",
    "frontend/src",
    "infra",
    "media/product-images",
    "media/visio-stencils",
    "scripts",
    "docs"
]

files = {
    "docker-compose.yml": "",
    "frontend/Dockerfile": "",
    "media/README.md": "# Media Folder\n\nThis folder contains product images and Visio stencils.",
    "infra/main.bicep": "",
    "infra/monitor.bicep": "",
    "infra/db.bicep": "",
    "infra/identity.bicep": "",
    "infra/networking.bicep": "",
    "README.md": "",  # already populated manually
}

def scaffold():
    print("📁 Scaffolding local project structure...\n")
    for path in directories:
        os.makedirs(path, exist_ok=True)
        print(f"  ➕ {path}/")

    for path, content in files.items():
        if not os.path.exists(path):
            with open(path, "w") as f:
                f.write(content)
            print(f"  📝 {path}")
        else:
            print(f"  ✅ {path} already exists")

    print("\n✅ Done. Your project structure is now ready.")

if __name__ == "__main__":
    scaffold()
