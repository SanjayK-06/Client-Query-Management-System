# Client Query Management System (PostgreSQL)

Built using Streamlit + PostgreSQL
Created by: Sanjay Kannan

📌 Summary

⦁	This is a simple ticket management system where:

⦁	Clients submit queries

⦁	Support team views & updates queries

⦁	Admins review all queries with date-range analytics

⦁	The project uses a pastel lavender UI theme and includes Matplotlib charts for monthly ticket stats and status split.


🚀 Features

⦁	Client ticket submission

⦁	Support ticket editing & status updates

⦁	Admin full dashboard

⦁	Date filters

⦁	Monthly bar chart (Matplotlib)

⦁	Pie chart for Open/Closed

⦁	PostgreSQL-backed storage

⦁	hashlib password hashing


📂 Project Structure
CLIENT_QUERY_MANAGEMENT_SYSTEM
│
├── app.py                    → Main Streamlit application
├── db_connection.py          → PostgreSQL connection helper (optional)
├── README.md                 → Documentation file
├── requirements.txt          → Python dependencies
├── .env                      → Database credentials (ignored from Git)
│
├── data/
│   └── synthetic_client_queries.csv
│   │
│   └── Screen_print & PPT 
│
└── Notebook/
    └── cqms.ipynb           → Data analysis / experimentation notebook


⚙️ Installation
    ⦁	pip install -r requirements.txt



Create .env:

DB_HOST=localhost
DB_PORT=5432
DB_NAME=client_query_db 
DB_USER=postgres
DB_PASSWORD=yourpassword

▶️ Run the App
    ⦁	streamlit run app.py


🛠 Tech Used

⦁	Streamlit

⦁	Python

⦁	PostgreSQL

⦁	Matplotlib

⦁	Pandas
