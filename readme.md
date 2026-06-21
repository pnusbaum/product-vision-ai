# Product Vision AI

Product Vision AI is a multimodal AI platform for e-commerce product understanding and retrieval.

The project combines two independent AI modules:

- **Product Description Generator** (Vision LLM + RAG + structured output)
- **Similar Product Search** (CLIP embeddings + vector similarity search)

The system is fully containerized and deployed in Google Cloud Platform using Terraform.

---

# Project Goal

The goal of this project is to solve real-world e-commerce problems:

- How to automatically generate product descriptions based on product image and metadata?
- How to find similar products based only on image or text?
- How to enrich product catalogs using AI?

Possible use cases:

- product recommendations
- product onboarding automation
- catalog enrichment
- duplicate detection
- visual product search
- SEO metadata generation

---

# Modules

## Module 1 — Product Description Generator

### Input

- product brand
- product name
- product image

### Output

- product category
- product tags
- extracted features
- marketing description
- SEO metadata

### Technologies

- OpenAI Vision LLM (GPT-4o)
- structured JSON output
- multi-step prompting
- lightweight RAG taxonomy retrieval

### Processing pipeline

```text
Input
 ↓
Prompt 1: Product routing
 ↓
RAG: Retrieve allowed taxonomy
 ↓
Prompt 2: Product analysis
 ↓
Prompt 3: Copywriting + SEO
 ↓
Structured output
```

---

## Module 2 — Similar Product Search

### Input

- product image
- text query

### Output

- visually similar products

### Technologies

- CLIP embeddings
- PostgreSQL + pgvector
- vector similarity search

### Processing pipeline

```text
Input
 ↓
Embedding generation
 ↓
Vector similarity search
 ↓
Top-N similar products
```

---

# Architecture

```text
User
 ↓
Streamlit Frontend
 ├── Product Description API
 └── Image Search API
         ↓
 Cloud SQL PostgreSQL + pgvector
         ↓
 Cloud Storage
```

---

# Project Structure

```text
product-vision-ai/
├── image-search-api/
├── product-description-api/
├── streamlit-app/
├── scripts/
├── infra/
│   └── terraform/
├── docker-compose.yml
├── .gitignore
└── README.md
```

---

# Local Development

## Run full stack locally

```bash
docker-compose up --build
```

Services:

- Streamlit → http://localhost:8501
- Image Search API → http://localhost:8000/docs
- Product Description API → http://localhost:8081/docs
- Adminer → http://localhost:8080

---

# Docker

Each service has its own:

- source code
- requirements.txt
- Dockerfile

Services:

- image-search-api
- product-description-api
- streamlit-app

Docker Compose is used for local orchestration.

---

# Infrastructure as Code

Infrastructure is fully managed with Terraform.

Location:

```text
infra/terraform/
```

Managed resources:

- Cloud Run
- Cloud SQL PostgreSQL
- Artifact Registry
- Cloud Storage
- IAM
- API enablement

---

# Deployment to Google Cloud Platform

## 1. Build Docker images

```bash
gcloud builds submit ./image-search-api --tag europe-central2-docker.pkg.dev/PROJECT_ID/docker-images/product-api:vX

gcloud builds submit ./product-description-api --tag europe-central2-docker.pkg.dev/PROJECT_ID/docker-images/product-description-api:vX

gcloud builds submit ./streamlit-app --tag europe-central2-docker.pkg.dev/PROJECT_ID/docker-images/product-streamlit:vX
```

---

## 2. Configure Terraform variables

Create:

```text
infra/terraform/terraform.tfvars
```

Example:

```hcl
project_id     = "your-project-id"
region         = "europe-central2"
openai_api_key = "sk-..."
db_password    = "your-db-password"
```

Important:

Do not commit this file.

---

## 3. Deploy infrastructure

```bash
terraform init
terraform fmt
terraform validate
terraform plan
terraform apply
```

---

# Cost Optimization

Stop Cloud SQL:

```bash
gcloud sql instances patch products-db --activation-policy=NEVER
```

Start Cloud SQL:

```bash
gcloud sql instances patch products-db --activation-policy=ALWAYS
```

---

# Tech Stack

## Backend

- FastAPI
- SQLAlchemy
- PostgreSQL
- pgvector
- CLIP
- OpenAI GPT-4o

## Frontend

- Streamlit

## Infrastructure

- Docker
- Docker Compose
- Terraform
- Google Cloud Run
- Google Cloud SQL
- Google Cloud Storage
- Artifact Registry

---

# Future Improvements

- Secret Manager integration
- CI/CD from GitHub Actions
- multilingual product descriptions
- advanced taxonomy retrieval
- recommendation engine
- admin panel

---

# Author

Piotr Nusbaum

This project was developed as part of an AI engineering course, focusing on multimodal product understanding, retrieval, and automated content generation for e-commerce.
