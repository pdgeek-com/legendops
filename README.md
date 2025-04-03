# LegendOps

## 🔧 Overview
LegendOps is a scalable multi-tenant SaaS platform for MSPs, integrating Azure AD, Pax8, QuickBooks, and SuperOps. This repository is designed with modular microservices, secure infrastructure-as-code, and dev-first CI/CD workflows for enterprise-grade deployments.

## 📁 Repository Structure
```
legendops/
├── .github/              # CI/CD Workflows (Azure DevOps or GitHub Actions)
├── apps/                 # Microservices (Flask API, billing-service, etc.)
│   ├── web/              # Python Flask backend
│   ├── billing/          # Pax8 + QuickBooks billing service
│   ├── auth/             # Azure AD login and session service
│   └── catalog/          # Product and service catalog API
├── db/                  # Microservice DB folders
│   ├── auth_db/          # DB schema and migrations for auth service
│   │   └── schema.sql
│   ├── billing_db/       # DB schema and migrations for billing
│   │   └── schema.sql
│   ├── portal_db/        # DB schema and migrations for portal
│   │   └── schema.sql
│   └── catalog_db/       # DB schema and migrations for catalog
│       └── schema.sql
├── frontend/             # React + Tailwind frontend
│   ├── public/
│   ├── src/
│   └── Dockerfile
├── infra/                # Bicep Infrastructure-as-Code
│   ├── main.bicep        # Main deployment file
│   ├── monitor.bicep     # Grafana Cloud / Azure Monitor setup
│   ├── db.bicep          # PostgreSQL and diagnostic settings
│   ├── identity.bicep    # Azure AD + Managed Identities
│   ├── networking.bicep  # NSGs, vNet, App Gateway
│   ├── variables.bicep   # Common variables for reuse
│   ├── tags.bicep        # Tag schema for billing and tracking
│   └── microdb.bicep     # Module to deploy per-service PostgreSQL DBs
├── media/                # Product images, diagrams, and stencils
│   ├── product-images/
│   ├── visio-stencils/
│   └── README.md         # Explain how to store and access product media
├── scripts/              # Python automation, seeders, deployment helpers
├── docs/                 # Internal documentation & onboarding
├── docker-compose.yml   # Local dev Docker stack
└── README.md
```

## ☁️ Azure Architecture Overview
- Resource Group per environment (`legendops-dev`, `legendops-prod`)
- Azure Subscription configurable via .env
- Tags: `Project`, `Environment`, `Owner`, `CostCenter`
- Azure Container Apps (frontend, backend, microservices)
- Azure Database for PostgreSQL Flexible Server (per-db setup)
- Azure Blob Storage (for product images, Visio stencils)
- Azure Key Vault + App Config
- Azure Monitor Workspace
- Azure AD B2B (M365 login per tenant)
- App Gateway or Front Door for ingress
- NSGs + private vNet routing for backend services
- Auto-scaling enabled
- Shutdown script to deallocate resources in Dev when idle

## 🔐 Security & Identity
### Azure AD (Multi-Tenant)
- B2B guest login for clients
- Role-based access with scopes:
  - `super_admin`
  - `tenant_admin`
  - `billing_viewer`
  - `support_user`
- Conditional Access Policies (MFA for Admin)

### Key Vault
- Unique client secrets/API keys per service
- Access control via managed identities + RBAC

### Network
- App Gateway with WAF
- NSG rules for backend-only access to DB
- Private endpoints for DB, KV
- DDoS Basic (can upgrade to Standard)

## 🤔 Database Design (PostgreSQL)
**Multi-db per microservice pattern:**
- `auth_db`: Users, sessions, tokens
- `billing_db`: Invoices, usage data, Pax8 sync
- `portal_db`: Customers, org data, audit trails
- `catalog_db`: Products, services, relationships, categories, stencils

**Blob Storage Containers:**
- `product-images/`
- `visio-stencils/`
- `documents/`

Common conventions:
- UUIDs for all IDs
- Timestamps: `created_at`, `updated_at`
- Row-level security support for multi-tenant isolation

## ⚙️ Microservices
### web (Flask)
- Main backend for portal
- REST API + session management

### billing-service
- Scheduled usage fetches from Pax8
- QuickBooks invoice generation

### auth-service
- Azure AD login, token validation
- JWT / session creation

### catalog-service
- Access to product/service catalog
- Media links, categories, and stencils

## 🚨 Monitoring (Grafana Cloud + Azure Monitor)
| Layer | What’s Monitored | Tooling | Alert Routing |
|-------|------------------|---------|---------------|
| Infra (Bicep) | VM/container metrics | Azure Monitor → Grafana Cloud | Slack/email alerts |
| App Services | Logs, uptime | Loki (Promtail) + App Insights | Grafana alerts |
| PostgreSQL | Query perf, errors | Azure PG Insights | Grafana dashboard |
| Network | NSG flow, DDoS | Azure Watcher | Alerts on traffic spikes |
| Secrets | Access logs | KV diagnostics → Grafana | Admin alert on secret read |
| Services | Healthchecks | Blackbox Exporter | Uptime alerting |
| Blob Media | Access + upload activity | Storage Analytics + Grafana | Audit alerts |

### Dashboards
- Azure Infra Overview
- PostgreSQL DB Performance
- Flask API error rate
- React frontend uptime
- Billing sync job status
- KV Secret Access logs
- Blob Storage Access + Errors

### Optional Self-hosted Later
- Prometheus + Grafana + Loki on Azure VM or Container App

## 🚀 Deployment Timeline
| Week | Milestone |
|------|-----------|
| Week 1 | Dev environment infra via Bicep, local dev runs via Docker |
| Week 2 | Push app containers to Azure Container Apps (Dev only) |
| Week 3 | Enable Azure AD login + seed customer data |
| Week 4 | Billing + Pax8/QuickBooks integration stable |
| Week 5 | Create staging + production infrastructure |
| Week 6 | Prod launch w/ Grafana Cloud and Key Vault monitoring |
| Week 7 | Product Catalog API + media storage |
| Week 8 | Stencil management + cable calculation framework |
