# StockFlow Inventory Management System

## Project Overview
StockFlow is a B2B SaaS platform designed to help small businesses manage inventory across multiple warehouses and streamline supplier relationships. This repository contains a three-part technical solution addressing API debugging, database architecture, and predictive stock alerting.

---

## Project Structure

### 1. `backend.py` (Part 1: Code Review & Debugging)
This file contains the refactored `create_product` endpoint.It addresses several critical failures identified in the original implementation:
* **Transactional Integrity**: Uses `db.session.flush()` to generate product IDs without a final commit, ensuring that both Product and Inventory records are created as a single atomic transaction.
* **Data Validation**: 
    * Enforces SKU uniqueness at the database level to prevent duplicate mappings.
    * Validates that `initial_quantity` is a non-negative integer.
* **API Standards**: Implements proper `Content-Type` validation (JSON) and returns standardized responses with appropriate HTTP status codes (e.g., 201 for success, 400 for validation errors, 415 for media type errors).

### 2. `\system_design\schema.sql` (Part 2: Database Design)
A normalized relational schema designed for scalability and multi-warehouse support.
* **Key Tables**:
    * **Companies**: Stores top-level company details.
    * **Warehouses**: Linked to companies, allowing for multiple locations per business.
    * **Inventory**: Acts as a mapping table between Products and Warehouses to support stock tracking across different locations.
    * **Inventory Logs**: Provides a full audit trail of stock changes, including reasons and timestamps.
    * **Suppliers & Bundles**: Supports complex procurement tracking and product bundling (kit-to-stock).

### 3. `\system_design\third.py` (Part 3: API Implementation)
Implements a sophisticated **Low-Stock Alert** system based on real-world business rules.
* **Endpoint**: `GET /api/companies/{company_id}/alerts/low-stock`.
* **Business Logic**:
    * **Activity-Based Filtering**: Only triggers alerts for products sold within the last 30 days to avoid flagging stagnant stock.
    * **Predictive Analytics**: Calculates **Days Until Stockout** by dividing current stock by the average daily sales velocity from the last 30 days.
    * **Supplier Integration**: Includes primary supplier contact information directly in the alert to facilitate rapid reordering.

---

##  Setup and Usage

1.  **Environment**: Ensure you have Python and Flask-SQLAlchemy installed.
2.  **Database**: The applications use a SQLite database (`test.db`). 
3.  **Seeding**: Use the provided `seed.py` script to populate the database with test data (companies, warehouses, products, and 30-day sales history) to verify the alert logic.
4.  **Running**:
    * Run `python backend.py` to test product creation.
    * Run `python third.py` in system_design folder to test the low-stock alert endpoint.
