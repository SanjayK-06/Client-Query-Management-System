# 📩 Client Query Management System

A **web-based ticket management system** built using **Streamlit and PostgreSQL** that allows clients to submit queries, support teams to manage tickets, and administrators to analyze ticket data through interactive dashboards.

This project demonstrates a **full-stack data application workflow** including database integration, authentication, analytics, and data visualization.

---

# 📌 Project Overview

The **Client Query Management System (CQMS)** is designed to manage and track customer queries efficiently.

The system provides three levels of access:

* **Client** – Submit queries or tickets
* **Support Team** – View, edit, and update ticket statuses
* **Admin** – Monitor all tickets and analyze trends through dashboards

The application features a **clean pastel lavender UI theme** and includes **data visualizations for ticket analytics**.

---

# 🎯 Objectives

* Build a **ticket management system** using Streamlit
* Store and manage ticket data using **PostgreSQL**
* Implement **role-based access** (Client, Support, Admin)
* Provide **data analytics and visual insights**
* Ensure **secure password storage using SHA-256 hashing**

---

# ✨ Features

* Client ticket submission
* Support team ticket management
* Ticket status updates (Open / Closed)
* Admin analytics dashboard
* Date-range filtering for queries
* Monthly ticket statistics
* Ticket status distribution visualization
* PostgreSQL-backed persistent storage
* Secure authentication using **SHA-256 password hashing**

---

# 🧠 Skills Demonstrated

* Database Integration with PostgreSQL
* Streamlit Web Application Development
* Data Visualization with Matplotlib
* Backend Data Handling with Pandas
* Environment Variable Management
* Secure Password Hashing
* Dashboard Design and Analytics

---

# 🧰 Tech Stack

**Programming Language**

* Python

**Web Framework**

* Streamlit

**Database**

* PostgreSQL

**Data Processing**

* Pandas

**Visualization**

* Matplotlib

**Security**

* SHA-256 password hashing

---

# 📂 Project Structure

```
CLIENT_QUERY_MANAGEMENT_SYSTEM
│
├── app.py                    # Main Streamlit application
├── db_connection.py          # PostgreSQL connection helper
├── README.md                 # Project documentation
├── requirements.txt          # Python dependencies
├── .env                      # Database credentials (not uploaded to GitHub)
│
├── data/
│   ├── synthetic_client_queries.csv
│   └── Screen_print & PPT
│
└── Notebook/
    └── cqms.ipynb            # Data analysis and experimentation notebook
```

---

# 🗄 Database Configuration

Create a **`.env` file** in the project root with the following credentials:

```
DB_HOST=localhost
DB_PORT=5432
DB_NAME=client_query_db
DB_USER=postgres
DB_PASSWORD=yourpassword
```

This ensures **secure database configuration without exposing credentials in the repository**.

---

# 📊 Dashboard Analytics

The admin dashboard includes **visual insights for ticket analysis**:

### 📅 Monthly Ticket Volume

A **Matplotlib bar chart** showing the number of tickets submitted each month.

### 🟢 Ticket Status Distribution

A **pie chart** displaying the proportion of **Open vs Closed tickets**.

These visualizations help administrators **track workload and monitor support performance**.

---

# 🚀 Installation & Setup

## 1️⃣ Clone the Repository

```bash
git clone https://github.com/yourusername/client-query-management-system.git
cd client-query-management-system
```

---

## 2️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 3️⃣ Configure Environment Variables

Create the `.env` file with PostgreSQL database credentials.

---

## 4️⃣ Run the Application

```bash
streamlit run app.py
```

The application will open automatically in your browser.

---

# 📊 Workflow

1. **Client submits a query**
2. Query is stored in the **PostgreSQL database**
3. **Support team reviews and updates ticket status**
4. **Admin monitors ticket analytics through dashboards**

---

# 💼 Business Use Cases

### Customer Support Management

Centralized system for tracking and resolving customer issues.

### Support Team Productivity

Helps teams efficiently manage and update ticket statuses.

### Data-Driven Decision Making

Analytics dashboard provides insights into support workload and trends.

### Customer Experience Improvement

Ensures queries are tracked and resolved systematically.

---

# 🚀 Future Improvements

* Email notifications for ticket updates
* Role-based authentication system
* Real-time ticket status updates
* Cloud deployment (AWS / Streamlit Cloud)
* Advanced analytics dashboard using Plotly

---

# 👨‍💻 Author

**Sanjay Kannan**

Python | Data Analytics | Streamlit Developer


