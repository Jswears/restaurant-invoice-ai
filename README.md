# 🍽️ Restaurant Invoice AI Processor

An intelligent invoice processing system designed specifically for restaurants to automate invoice data extraction, supplier management, and financial analytics using AI-powered document processing.

## 🎯 Project Vision

This system will help restaurants:

- 🔄 **Automate Invoice Processing**: Upload PDFs/images and extract structured data using AI
- 📊 **Supplier Management**: Track vendors, spending patterns, and payment due dates
- 📈 **Financial Analytics**: Generate insights on spending trends and cost optimization
- ⚡ **Scale Efficiently**: Start simple, expand to full automation with email integration
- 🤖 **Future-Ready**: Built for chatbot integration and advanced AI features

---

## 🏗️ Planned Architecture

```
User (Web App)
   ↓
Next.js Frontend  ←→  FastAPI Backend  ←→  PostgreSQL (Supabase/RDS)
                        ↓
                     S3 (Invoices Storage)
                        ↓
                OpenAI (GPT-4o or GPT-5) → Invoice JSON Extraction
```

_(Will expand with AWS Lambda, API Gateway, SQS queues for automation)_

---

## ⚡ Planned Tech Stack

| Layer                            | Technology                                 | Why it's Ideal                                                   |
| -------------------------------- | ------------------------------------------ | ---------------------------------------------------------------- |
| **Frontend (Web App)**           | Next.js + React + TailwindCSS              | Great developer experience, modern UI, fast dashboards           |
| **Backend API**                  | FastAPI (Python)                           | Async, lightweight, perfect for AI workloads and PDF parsing     |
| **Database (MVP)**               | Supabase (hosted PostgreSQL)               | Free tier, instant setup, easy migrations + auth                 |
| **Database (Production)**        | AWS RDS for PostgreSQL                     | AWS-native, durable, scalable, backups, secure                   |
| **File Storage**                 | AWS S3                                     | Invoices/PDF storage; versioning, cheap, secure                  |
| **AI Model (Parsing)**           | OpenAI GPT-4o or GPT-4.1 Vision            | Best OCR + reasoning for invoices; supports multilingual layouts |
| **Optional Fallback**            | GPT-5 or Claude 3.5 Sonnet via AWS Bedrock | For higher accuracy, vendor-specific tuning, EU privacy          |
| **Authentication**               | NextAuth.js (or Supabase Auth)             | Simple user login for owners, accountants                        |
| **ORM / DB Layer**               | SQLAlchemy + Alembic                       | Clean models, migration control, works with Postgres + RDS       |
| **Deployment (MVP)**             | Render.com / Railway / Fly.io              | Easiest deployment — no DevOps, auto HTTPS                       |
| **Deployment (Production)**      | AWS ECS Fargate or EC2                     | AWS-integrated, scalable, no server maintenance                  |
| **Email Invoice Intake (later)** | AWS SES or Gmail API                       | Auto-fetch invoices from supplier emails                         |

---

## 🗃️ Planned Database Schema

| Table             | Purpose                  | Example Fields                                                                                       |
| ----------------- | ------------------------ | ---------------------------------------------------------------------------------------------------- |
| **suppliers**     | Restaurant vendors       | id, name, address, VAT ID                                                                            |
| **invoices**      | One invoice per upload   | id, supplier_id, invoice_number, date, due_date, net_total, tax_total, gross_total, currency, s3_url |
| **invoice_items** | Line items from AI       | id, invoice_id, description, quantity, unit, unit_price, net_amount, tax_rate                        |
| **users (later)** | Restaurant owners, staff | id, email, password_hash, role                                                                       |

---

## 🚀 Planned API Endpoints

| Method | Endpoint             | Description                                       |
| ------ | -------------------- | ------------------------------------------------- |
| POST   | `/invoices/upload`   | Upload PDF/JPG invoice → send to AI → return JSON |
| GET    | `/invoices/{id}`     | Fetch stored structured invoice from DB           |
| GET    | `/suppliers`         | List all suppliers & total spend                  |
| GET    | `/analytics/monthly` | Total spend by month/supplier                     |
| POST   | `/auth/login`        | User authentication                               |

---

## 📁 Current Project Structure

```
restaurant-invoice-ai/
├── README.md                   # Project documentation
├── backend/                    # FastAPI backend (to be implemented)
├── frontend/                   # Next.js frontend (to be implemented)
├── docs/                      # Documentation and specs
└── infra/                     # Infrastructure configurations
```

---

## 💡 Why This Architecture?

### ✅ **Advantages Over Pure Serverless (Lambda/API Gateway)**

| Issue                            | Lambda Limitation                      | Our Planned Solution                         |
| -------------------------------- | -------------------------------------- | -------------------------------------------- |
| Long invoice parsing (PDF + LLM) | Lambda max runtime = 15 min            | FastAPI runs continuously — no timeout       |
| Debugging AI logic               | Lambda logs are painful                | FastAPI + local environment = easy debugging |
| Cold starts                      | Slower, especially Python + heavy libs | Containers or VM keep app warm               |
| Database connections             | Lambda ↔ RDS = slow/cold/VPC pain      | FastAPI keeps persistent Postgres connection |
| Complexity too early             | IAM, S3 triggers, API Gateway setup    | MVP stays simple, scalable later             |

### ✅ **Key Design Principles**

- **Fast Development**: Python for AI/OCR with no hacky workarounds
- **Scalable Database**: PostgreSQL (relational, scalable, widely supported)
- **Cloud Agnostic**: Not locked to one cloud provider, but AWS-ready
- **Maintainable**: Clear separation between core logic & AI processing
- **Modern Frontend**: Next.js makes dashboard analytics easy & fast
- **Industry Standard**: S3 is the gold standard for storing original documents
- **Future-Proof**: Simple MVP that scales to enterprise features

---

## 🛣️ Development Roadmap

| Phase                              | Infrastructure                                                                   |
| ---------------------------------- | -------------------------------------------------------------------------------- |
| **🚀 MVP (Phase 1)**               | FastAPI + Supabase/Postgres + S3 + OpenAI + Next.js on Render/Fly.io             |
| **📦 Production (Phase 2)**        | Migrate DB to AWS RDS, host API on API Gateway + Lambda, frontend on AWS Amplify |
| **⚡ Auto-scaling (Phase 3)**      | Add SQS + Lambda for background invoice processing                               |
| **🤖 AI Enhancement (Phase 4)**    | LangChain + Postgres Vector for conversational analytics                         |
| **💰 Cost Optimization (Phase 5)** | Hybrid OCR (Tesseract + GPT fallbacks), AI prompt compression                    |

---

## 🎯 Current Status

**Project Phase**: Initial Planning & Architecture Design

**Next Steps**:

1. 🏗️ Set up project structure and development environment
2. 🔧 Implement FastAPI backend with basic invoice processing
3. 🎨 Create Next.js frontend with file upload interface
4. 🤖 Integrate OpenAI GPT-4 Vision for invoice parsing
5. 📊 Build dashboard for supplier and spending analytics

---

## 🚀 Getting Started (Coming Soon)

This project is in the initial planning phase. Once implementation begins, this section will include:

- Prerequisites and setup instructions
- Environment configuration
- Development workflow
- Deployment guidelines

---

**Building the future of restaurant invoice processing with AI! 🚀**
