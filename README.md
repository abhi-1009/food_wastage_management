# 🌿 Local Food Wastage Management System

A data-driven web application that connects surplus food providers with receivers to reduce food wastage. Built with MySQL, Python, and Streamlit — fully deployed on Streamlit Cloud.

## 📌 Project Overview

Every day, tonnes of food go to waste while millions of people remain hungry. This system bridges that gap by:

1) Tracking food donations from restaurants, supermarkets, grocery stores, and catering services
2) Connecting surplus food with NGOs, shelters, charities, and individuals
3) Providing SQL-powered analysis to identify wastage trends and high-demand areas
4) Offering a live interactive dashboard for real-time monitoring and management

---

## 🔗 Live Application

**Deployed  App:** https://foodwastagemanagement-bjhhzi5p7hqjfgexkmtnsa.streamlit.app/

**GitHub Repository:** https://github.com/abhi-1009/food_wastage_management

---

## 🎯 Project Objectives

* Reduce food wastage through efficient redistribution.
* Connect food providers and receivers through a centralized platform.
* Track food listings and claims.
* Enable real-time food search and filtering.
* Generate actionable business insights using SQL analytics.
* Support data-driven decision-making through interactive dashboards.

---

## 🛠️ Tech Stack

| Layer          | Technology                              |
| -----------    | -----------                             |
| Database       | MySQL 8.0 (local) + Aiven MySQL (cloud) |
| DB Management  | MySQL Workbench                         |
| Data Analysis  | Python — pandas, matplotlib, seaborn    |
| Web App        | Python — Streamlit, Plotly              |
| DB Connector   | SQLAlchemy + mysql-connector-python     |
| Version Control| Git + GitHub                            |
| Deployment     | Streamlit Cloud (Application Hosting)   |
| IDE            | Visual Studio Code                      |

---

## 🗂️ Dataset

## 🗄️ Database Structure

The project uses four relational tables:

1. Providers
2. Receivers
3. Food Listings
4. Claims

## Key Statistics:

* Total Records: 4,000 across 4 tables
* 25,794 total food units available
* 624 cities covered
* 339 completed claims | 325 pending | 336 cancelled
* Date range: March 2025

---

### Providers

Stores information about food providers.

| Column      |
| ----------- |
| Provider_ID |
| Name        |
| Type        |
| Address     |
| City        |
| Contact     |

### Receivers

Stores information about food receivers.

| Column      |
| ----------- |
| Receiver_ID |
| Name        |
| Type        |
| City        |
| Contact     |

### Food Listings

Stores available food donations.

| Column        |
| ------------- |
| Food_ID       |
| Food_Name     |
| Quantity      |
| Expiry_Date   |
| Provider_ID   |
| Provider_Type |
| Location      |
| Food_Type     |
| Meal_Type     |

### Claims

Stores claim records.

| Column      |
| ----------- |
| Claim_ID    |
| Food_ID     |
| Receiver_ID |
| Status      |
| Timestamp   |

---

## 📊 Key Features

### 🏠 Dashboard

* Total food units available
* 5 KPI metric cards (food units, claims, completed, pending, cities)
* Claim status donut chart
* Top 10 cities by listings
* Completed & Pending claims
* City-wise food availability
* Meal Type Analysis

### 📊 SQL Analytics

* 15 business-Oriented SQL queries
* Dropdown to select any of 15 queries
* Results shown as data table + interactive chart
* All 15 results available as expandable sections

### 🗂️ Browse Data

* Providers tab — filter by city and type
* Receivers tab — filter by type
* Claims tab — filter by status

### ✏️ CRUD Operations

* Add — Insert new food listing with live preview
* Update — Change claim status or food quantity with before/after display
* Delete — Remove listing with cascade warning and confirmation checkbox

### 🔍 Search & Filter

* Filter food by city, food type, meal type, provider type
* Provider contact details shown in results
* Separate receiver contact lookup

### 💡 Business Insights

* 6 data-backed insight cards (live from MySQL)
* Supporting charts for each insightBusiness Insights

### 📌 Recommendations

* 7 Data-driven recommendations to reduce food wastage
* Demand forecasting insights
* Food redistribution strategies
* Improve food distribution efficiency
* Increase successful food claims
 
---

## 📈 Analytical Insights Generated

The application answers several business questions, including:

1. Which cities have the highest food availability?
2. Which provider types contribute the most food?
3. Which receivers claim the most food?
4. What percentage of claims are completed?
5. Which meal types are most frequently wasted?
6. Which cities have the highest food demand?
7. How do food claims change over time?

---

## ☁️ Deployment Architecture

Local Development Environment

Python + Streamlit 

MySQL Database -- MySQL Cloud Database hosted on Aiven.

Cloud Deployment

Streamlit Cloud -- Application deployed using Streamlit Community Cloud.

Aiven Cloud MySQL Database

Version Control

GitHub Repository

---

## 🚀 Local Setup

# Prerequisites

* Python 3.12+
* MySQL 8.0
* MySQL Workbench

# Installation

1. Clone the repository
```bash
git clone https://github.com/abhi-1009/food_wastage_management.git
cd food_wastage_management
```

2. Install Python dependencies

```bash
pip install -r requirements.txt
```
3. Set up the database

* Open MySQL Workbench and run the SQL script to create tables:
```bash
sql
CREATE DATABASE food_wastage;
USE food_wastage;
-- Run the full SQL script to create all tables
```
* Load data using the staging table approach with MySQL Workbench Import Wizard.

4. Update credentials in the Python file

* python
* HOST     = "localhost"
* PORT     = 3306
* USER     = "root"
* PASSWORD = "your_password"
* DATABASE = "food_wastage"

5. Run the Streamlit app

```bash
streamlit run Food_WastageManagement.py
```
6. Run EDA charts (optional)

```bash
python eda.py
```

---

## 📂 Project Structure

food_wastage_management/
│
├── Food_WastageManagement.py   # Main Streamlit application (7 pages)
├── eda.py                      # Python EDA script (16 charts)
├── requirements.txt            # Python dependencies
├── README.md                   # This file
│
├── eda_charts/                 # Generated EDA chart images
│   ├── 01_provider_type.png
│   ├── 02_receiver_type.png
│   └── ... (16 charts total)
│
└── (CSV files — not pushed to GitHub)
    ├── providers.csv
    ├── receivers.csv
    ├── food_listings.csv
    └── claims.csv

---

## 🔒 Security

* Database credentials are not stored in source code.
* Streamlit Secrets are used for secure credential management.
* GitHub Secret Scanning compliance implemented.
---

## 👨‍💻 Author

**Abhijit Sinha**
---
GitHub: https://github.com/abhi-1009
LinkedIn: (www.linkedin.com/in/abhijit-sinha-053b159a)
---

## ⭐ Future Enhancements

* User Authentication
* Login & Registration
* Email Notifications
* Automated Food Expiry Alerts
* Advanced Analytics Dashboard
* Mobile Responsive Interface
* Report Download Functionality

---

## 📜 License

This project is developed for educational and portfolio purposes. 
