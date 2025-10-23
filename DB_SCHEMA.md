# 🗃️ Database Schema

### 1. `suppliers`

| Field      | Type      | Notes            |
| ---------- | --------- | ---------------- |
| id         | UUID (PK) | Primary key      |
| name       | VARCHAR   | Supplier name    |
| address    | TEXT      | Physical address |
| vat_id     | VARCHAR   | Tax identifier   |
| created_at | TIMESTAMP | For auditing     |
| updated_at | TIMESTAMP | Auto-updated     |

---

### 2. `invoices`

| Field          | Type           | Notes                                 |
| -------------- | -------------- | ------------------------------------- |
| id             | UUID (PK)      | Primary key                           |
| supplier_id    | UUID (FK)      | Linked to `suppliers(id)`             |
| invoice_number | VARCHAR        | From document                         |
| invoice_date   | DATE           | Date of invoice                       |
| due_date       | DATE           | Payment due                           |
| net_total      | NUMERIC(12, 2) | Before tax                            |
| tax_total      | NUMERIC(12, 2) | Total tax                             |
| gross_total    | NUMERIC(12, 2) | Net + tax                             |
| currency       | CHAR(3)        | ISO 4217 code (e.g., USD, EUR)        |
| s3_url         | TEXT           | S3 location of original invoice       |
| ai_status      | VARCHAR        | e.g., `pending`, `processed`, `error` |
| created_at     | TIMESTAMP      |                                       |
| updated_at     | TIMESTAMP      |                                       |

---

### 3. `invoice_items`

| Field       | Type           | Notes                       |
| ----------- | -------------- | --------------------------- |
| id          | UUID (PK)      | Primary key                 |
| invoice_id  | UUID (FK)      | Linked to `invoices(id)`    |
| description | TEXT           | Item name or description    |
| quantity    | NUMERIC(10, 2) | Supports decimal quantities |
| unit        | VARCHAR(20)    | e.g., `kg`, `litre`, `box`  |
| unit_price  | NUMERIC(12, 4) | Price per unit              |
| net_amount  | NUMERIC(12, 2) | quantity × unit_price       |
| tax_rate    | NUMERIC(5, 2)  | e.g., 20.00 for 20% VAT     |
| created_at  | TIMESTAMP      |                             |

---

### 4. `users` _(optional now, but structured for later use)_

| Field         | Type             | Notes                           |
| ------------- | ---------------- | ------------------------------- |
| id            | UUID (PK)        | Primary key                     |
| email         | VARCHAR (unique) | User login                      |
| password_hash | TEXT             | Hashed password                 |
| role          | VARCHAR(20)      | e.g., `admin`, `staff`, `owner` |
| created_at    | TIMESTAMP        |                                 |
| updated_at    | TIMESTAMP        |                                 |

---
