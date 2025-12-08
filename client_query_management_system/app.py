import os
import streamlit as st
import psycopg2
import pandas as pd
import hashlib
from datetime import datetime
from dotenv import load_dotenv
import matplotlib.pyplot as plt

# ========================================
# LOAD ENV
# ========================================
load_dotenv()
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

# ========================================
# DATABASE CONNECTION
# ========================================
def get_connection():
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
    )

# ========================================
# PASSWORD HASHING
# ========================================
def make_hash(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

# ========================================
# TABLE CREATION
# ========================================
def create_users_table():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(100) UNIQUE NOT NULL,
            hashed_password VARCHAR(255) NOT NULL,
            role VARCHAR(20) CHECK (role IN ('Client','Support','Admin')) NOT NULL
        );
        """
    )
    conn.commit()
    cur.close()
    conn.close()


def create_queries_table():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS queries (
            id SERIAL PRIMARY KEY,
            client_email VARCHAR(255),
            client_mobile VARCHAR(20),
            query_heading VARCHAR(255),
            query_description TEXT,
            status VARCHAR(20) CHECK (status IN ('Open','Closed')) DEFAULT 'Open',
            date_raised TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            date_closed TIMESTAMP
        );
        """
    )
    conn.commit()
    cur.close()
    conn.close()


create_users_table()
create_queries_table()

# ========================================
# CRUD FUNCTIONS
# ========================================
def add_user(username: str, password: str, role: str):
    conn = get_connection()
    cur = conn.cursor()
    hashed = make_hash(password)
    cur.execute(
        "INSERT INTO users (username, hashed_password, role) VALUES (%s,%s,%s)",
        (username.upper(), hashed, role),
    )
    conn.commit()
    cur.close()
    conn.close()


def login_user(username: str, password: str, role: str):
    conn = get_connection()
    cur = conn.cursor()
    hashed = make_hash(password)
    cur.execute(
        "SELECT * FROM users WHERE username=%s AND hashed_password=%s AND role=%s",
        (username.upper(), hashed, role),
    )
    data = cur.fetchone()
    cur.close()
    conn.close()
    return data


def insert_query(email: str, mobile: str, heading: str, description: str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO queries (client_email, client_mobile, query_heading, query_description)
        VALUES (%s,%s,%s,%s)
        """,
        (email, mobile, heading, description),
    )
    conn.commit()
    cur.close()
    conn.close()


def get_all_queries() -> pd.DataFrame:
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM queries ORDER BY date_raised DESC", conn)
    conn.close()
    return df


def update_query(
    id: int, email: str, mobile: str, heading: str, description: str, status: str
):
    conn = get_connection()
    cur = conn.cursor()
    close_time = datetime.now() if status == "Closed" else None
    cur.execute(
        """
        UPDATE queries
        SET client_email=%s,
            client_mobile=%s,
            query_heading=%s,
            query_description=%s,
            status=%s,
            date_closed=%s
        WHERE id=%s
        """,
        (email, mobile, heading, description, status, close_time, id),
    )
    conn.commit()
    cur.close()
    conn.close()

# ========================================
# STREAMLIT CONFIG
# ========================================
st.set_page_config(page_title="Client Query System", layout="wide")

# ========================================
# PASTEL THEME CSS
# ========================================
st.markdown("""
<style>

    /* MAIN BACKGROUND — SOFT DEEP LAVENDER */
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(145deg, #ede7f6 0%, #d8c9f0 50%, #c7b4e8 100%);
        background-attachment: fixed;
    }

    /* SIDEBAR — PASTEL LAVENDER + WHITE BLUR */
    [data-testid="stSidebar"] {
        background: rgba(240, 232, 255, 0.75);
        backdrop-filter: blur(10px);
        border-right: 1px solid #cab6eb;
    }
    [data-testid="stSidebar"] * {
        color:#4a3c7a !important;
    }

    /* MAIN TITLE */
    .big-title {
        font-size: 48px;
        font-weight: 900;
        text-align: center;
        color: #4b2d6e;
        text-shadow: 0px 2px 8px rgba(0,0,0,0.12);
        margin-bottom: 5px;
    }

    /* SUB TITLE */
    .sub-title {
        text-align:center;
        font-size:17px;
        color:#755ca8;
        margin-bottom:32px;
    }

    /* SECTION / METRIC CARDS */
    .section-card, .metric-card, .feature-card {
        background: #faf6ff;
        border: 1px solid #ccb7ef;
        border-radius: 18px;
        padding: 22px;
        box-shadow: 0px 6px 18px rgba(0,0,0,0.06);
    }

    .metric-number {
        font-size: 34px;
        font-weight: 800;
        color: #4b2d6e;
    }
    .metric-label {
        font-size: 16px;
        color: #6b5998;
    }

    .feature-title {
        font-weight: 700;
        font-size: 1rem;
        color: #4b2d6e;
    }
    .feature-text {
        color:#6b5a93;
        font-size:0.92rem;
    }

    .step-badge {
        width: 26px;
        height: 26px;
        border-radius: 999px;
        background: #d49ce6;
        color: #3a2158;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-right:10px;
        font-weight:700;
    }

    .stButton>button {
        border-radius: 30px;
        padding: 8px 22px;
        background: linear-gradient(135deg,#b087e3,#d9b4f5);
        color: white;
        font-weight: 600;
        border: none;
        box-shadow: 0px 6px 20px rgba(0,0,0,0.12);
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.2);
    }

    .role-client {
        background:#dff5ec;
        color:#1d4c3b;
        padding:5px 14px;
        border-radius:999px;
        font-weight:600;
    }
    .role-support {
        background:#e3d1ff;
        color:#3b2b73;
        padding:5px 14px;
        border-radius:999px;
        font-weight:600;
    }
    .role-admin {
        background:#f7d0e8;
        color:#611a3b;
        padding:5px 14px;
        border-radius:999px;
        font-weight:600;
    }

    .footer-text {
        text-align:center;
        color:#6d5c96;
        margin-top:20px;
        font-size:0.9rem;
    }

</style>
""", unsafe_allow_html=True)

# ========================================
# SESSION STATE
# ========================================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# ========================================
# NOT LOGGED IN → HOME + LOGIN/REGISTER
# ========================================
if not st.session_state.logged_in:
    st.markdown(
        "<div class='big-title'>Client Query Management System</div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<div class='sub-title'>Simple ticketing for clients, support teams and admins.</div>",
        unsafe_allow_html=True,
    )

    c1, c2, c3 = st.columns(3)
    with c1:
        st.button("🧑‍💻 Login as Client", help="Use Login tab below and select Client")
    with c2:
        st.button("🛠 Login as Support", help="Use Login tab below and select Support")
    with c3:
        st.button("🧑‍💼 Login as Admin", help="Use Login tab below and select Admin")

    st.caption("Scroll down to use the Login / Register tabs and start using the system.")

    df = get_all_queries()

    col1, col2, col3 = st.columns(3)
    total = len(df)
    open_count = len(df[df["status"] == "Open"]) if not df.empty else 0
    closed_count = len(df[df["status"] == "Closed"]) if not df.empty else 0

    col1.markdown(
        f"""
        <div class='metric-card'>
          <div class='metric-label'>Total Queries</div>
          <div class='metric-number'>{total}</div>
          <div style='font-size:0.8rem;color:#9ca3af;margin-top:4px;'>
            All tickets created
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    col2.markdown(
        f"""
        <div class='metric-card'>
          <div class='metric-label'>Open</div>
          <div class='metric-number'>{open_count}</div>
          <div style='font-size:0.8rem;color:#9ca3af;margin-top:4px;'>
            Waiting for resolution
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    col3.markdown(
        f"""
        <div class='metric-card'>
          <div class='metric-label'>Closed</div>
          <div class='metric-number'>{closed_count}</div>
          <div style='font-size:0.8rem;color:#9ca3af;margin-top:4px;'>
            Successfully resolved
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("### 🧾 Project Overview")
    o1, o2 = st.columns((1.4, 1))
    with o1:
        st.markdown(
            """
            <div class="section-card">
              <h4>What does this app do?</h4>
              <ul style="color:#6E6E8A;font-size:0.9rem;">
                <li>Clients raise queries with their contact details.</li>
                <li>Support team views, updates and closes tickets.</li>
                <li>Admins monitor overall ticket volume and status.</li>
              </ul>
              <p style="color:#9ca3af;font-size:0.85rem;margin-top:6px;">
                All actions are stored centrally in PostgreSQL, so every role sees the latest data.
              </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with o2:
        st.markdown(
            """
            <div class="section-card">
              <h4>User roles</h4>
              <ul style="color:#6E6E8A;font-size:0.9rem;">
                <li><b>Client</b> – Submit new queries.</li>
                <li><b>Support</b> – Work on and close tickets.</li>
                <li><b>Admin</b> – Filter by date, review and edit tickets.</li>
              </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("---")

    f1, f2, f3 = st.columns(3)
    with f1:
        st.markdown(
            """
            <div class="feature-card">
              <div class="feature-title">🧑‍💻 Client Portal</div>
              <div class="feature-text">
                Simple form to log queries with email, mobile and a short description.
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with f2:
        st.markdown(
            """
            <div class="feature-card">
              <div class="feature-title">🛠 Support Dashboard</div>
              <div class="feature-text">
                See all tickets, filter by status/date and update details in one place.
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with f3:
        st.markdown(
            """
            <div class="feature-card">
              <div class="feature-title">🧑‍💼 Admin View</div>
              <div class="feature-text">
                Monitor tickets with date filters and quick edit access.
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("### 🚀 Workflow in 3 steps")
    s1, s2, s3 = st.columns(3)
    with s1:
        st.markdown(
            """
            <div style="display:flex;align-items:flex-start;color:#4A4A68;">
              <div class="step-badge">1</div>
              <div>
                <b>Client submits</b><br>
                Login as Client and create a new query.
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with s2:
        st.markdown(
            """
            <div style="display:flex;align-items:flex-start;color:#4A4A68;">
              <div class="step-badge">2</div>
              <div>
                <b>Support resolves</b><br>
                Support updates details and closes the ticket.
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with s3:
        st.markdown(
            """
            <div style="display:flex;align-items:flex-start;color:#4A4A68;">
              <div class="step-badge">3</div>
              <div>
                <b>Admin reviews</b><br>
                Admin checks performance using date filters.
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown(
        """
        <hr style="margin-top:30px;margin-bottom:10px;border-color:#E3DEEB;">
        <div class="footer-text">
          Client Query Management System · Built by <b>Sanjay Kannan ❤ </b>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("---")

    tab_login, tab_register = st.tabs(["🔐 Login", "📝 Register"])

    with tab_login:
        st.subheader("🔐 Login")
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        r = st.selectbox("Select Role", ["Client", "Support", "Admin"])

        if st.button("Login"):
            data = login_user(u, p, r)
            if data:
                st.session_state.logged_in = True
                st.session_state.username = data[1]
                st.session_state.role = data[3]
                st.success(f"Welcome {data[1]} ({data[3]})")
                st.experimental_rerun()
            else:
                st.error("Invalid credentials.")

    with tab_register:
        st.subheader("📝 Register")
        ru = st.text_input("New Username")
        rp = st.text_input("New Password", type="password")
        rr = st.selectbox("Role", ["Client", "Support", "Admin"])

        if st.button("Create Account"):
            if ru and rp:
                try:
                    add_user(ru, rp, rr)
                    st.success("Account Created Successfully!")
                except Exception as e:
                    st.error(f"Username already exists or error: {e}")
            else:
                st.error("Enter username & password.")

# ========================================
# LOGGED IN → ONLY DASHBOARD (NO HOME)
# ========================================
else:
    role = st.session_state.role
    if role == "Client":
        role_tag = "<span class='role-client'>Client</span>"
    elif role == "Support":
        role_tag = "<span class='role-support'>Support</span>"
    else:
        role_tag = "<span class='role-admin'>Admin</span>"

    st.sidebar.markdown(
        f"Logged in as <b>{st.session_state.username}</b><br>{role_tag}",
        unsafe_allow_html=True,
    )

    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.experimental_rerun()

    if role == "Client":
        nav = st.sidebar.radio("Menu", ["Client Panel"])
    elif role == "Support":
        nav = st.sidebar.radio("Menu", ["Support Panel"])
    elif role == "Admin":
        nav = st.sidebar.radio("Menu", ["Admin Panel"])
    else:
        nav = None

    # -------- CLIENT PANEL --------
    if role == "Client" and nav == "Client Panel":
        st.subheader("📝 Submit New Query")
        email = st.text_input("Email")
        mob = st.text_input("Mobile")
        head = st.text_input("Heading")
        desc = st.text_area("Description")

        if st.button("Submit Query"):
            if email and mob and head and desc:
                insert_query(email, mob, head, desc)
                st.success("Query Submitted!")
            else:
                st.error("Fill all fields before submitting.")

    # -------- SUPPORT PANEL --------
    if role == "Support" and nav == "Support Panel":
        st.subheader("🛠 Support Dashboard")

        df = get_all_queries()
        if df.empty:
            st.info("No tickets yet.")
        else:
            df["date_raised"] = pd.to_datetime(df["date_raised"])

            fc1, fc2 = st.columns(2)
            with fc1:
                status_filter = st.selectbox("Filter by Status", ["All", "Open", "Closed"])
            with fc2:
                min_date = df["date_raised"].min().date()
                date_filter = st.date_input("Filter from Date", value=min_date)

            df_view = df.copy()
            if status_filter != "All":
                df_view = df_view[df_view["status"] == status_filter]
            if date_filter:
                df_view = df_view[df_view["date_raised"].dt.date >= date_filter]

            st.markdown("### 📋 Tickets")
            st.dataframe(df_view, use_container_width=True)

            st.markdown("### ✏️ Work on a Ticket")
            ticket_ids = df_view["id"].tolist()
            if ticket_ids:
                tid = st.selectbox("Select Ticket ID", ticket_ids)
                sel = df_view[df_view["id"] == tid].iloc[0]

                email = st.text_input("Email", sel["client_email"])
                mob = st.text_input("Mobile", sel["client_mobile"])
                head = st.text_input("Heading", sel["query_heading"])
                desc = st.text_area("Description", sel["query_description"])
                stat = st.selectbox(
                    "Status", ["Open", "Closed"],
                    index=0 if sel["status"] == "Open" else 1,
                )

                if st.button("Update Ticket"):
                    update_query(tid, email, mob, head, desc, stat)
                    st.success("Ticket Updated! (Refresh to see latest data)")
            else:
                st.info("No tickets in selected filter set.")

            # Support analytics – MONTHLY bar + pie with matplotlib
            st.markdown("### 📊 Support Analytics")
            if not df_view.empty:
                df_view["month"] = df_view["date_raised"].dt.to_period("M").dt.to_timestamp()
                monthly_counts = (
                    df_view.groupby("month")
                    .size()
                    .reset_index(name="count")
                    .sort_values("month")
                )
                status_counts = df_view["status"].value_counts()

                c1, c2 = st.columns(2)

                # Bar chart
                with c1:
                    fig1, ax1 = plt.subplots(figsize=(5, 3))
                    ax1.bar(
                        monthly_counts["month"].dt.strftime("%Y-%m"),
                        monthly_counts["count"],
                        color="#6b21a8",
                        edgecolor="#3b0764",
                        linewidth=1.5,
                    )
                    ax1.set_title("Support – Monthly Tickets")
                    ax1.set_xlabel("Month")
                    ax1.set_ylabel("Tickets")
                    ax1.tick_params(axis="x", rotation=45)
                    fig1.tight_layout()
                    st.pyplot(fig1)

                # Pie chart
                with c2:
                    fig2, ax2 = plt.subplots(figsize=(4.5, 3))
                    ax2.pie(
                        status_counts.values,
                        labels=status_counts.index,
                        autopct="%1.1f%%",
                        startangle=90,
                    )
                    ax2.set_title("Status Split")
                    ax2.axis("equal")
                    fig2.tight_layout()
                    st.pyplot(fig2)

    # -------- ADMIN PANEL --------
    if role == "Admin" and nav == "Admin Panel":
        st.subheader("🧑‍💼 Admin Dashboard")

        df = get_all_queries()
        if df.empty:
            st.info("No tickets available.")
        else:
            df["date_raised"] = pd.to_datetime(df["date_raised"])

            col_d1, col_d2 = st.columns(2)
            min_date = df["date_raised"].min().date()
            max_date = df["date_raised"].max().date()
            start_date = col_d1.date_input("From date", value=min_date)
            end_date = col_d2.date_input("To date", value=max_date)

            df_f = df[
                (df["date_raised"].dt.date >= start_date)
                & (df["date_raised"].dt.date <= end_date)
            ].copy()

            if df_f.empty:
                st.info("No tickets in the selected date range.")
            else:
                total = len(df_f)
                open_count = (df_f["status"] == "Open").sum()
                closed_count = (df_f["status"] == "Closed").sum()

                ac1, ac2, ac3 = st.columns(3)
                ac1.markdown(
                    f"<div class='metric-card'><div class='metric-label'>Total Tickets</div><div class='metric-number'>{total}</div></div>",
                    unsafe_allow_html=True,
                )
                ac2.markdown(
                    f"<div class='metric-card'><div class='metric-label'>Open Tickets</div><div class='metric-number'>{open_count}</div></div>",
                    unsafe_allow_html=True,
                )
                ac3.markdown(
                    f"<div class='metric-card'><div class='metric-label'>Closed Tickets</div><div class='metric-number'>{closed_count}</div></div>",
                    unsafe_allow_html=True,
                )

                st.markdown("### 📋 Tickets in selected range")
                st.dataframe(df_f, use_container_width=True)

                # Admin charts – MONTHLY bar + pie with matplotlib
                st.markdown("### 📊 Admin Analytics")
                df_f["month"] = df_f["date_raised"].dt.to_period("M").dt.to_timestamp()
                monthly_counts = (
                    df_f.groupby("month")
                    .size()
                    .reset_index(name="count")
                    .sort_values("month")
                )
                status_counts = df_f["status"].value_counts()

                c1, c2 = st.columns(2)

                with c1:
                    fig1, ax1 = plt.subplots(figsize=(5, 3))
                    ax1.bar(
                        monthly_counts["month"].dt.strftime("%Y-%m"),
                        monthly_counts["count"],
                        color="#4c1d95",
                        edgecolor="#2e1065",
                        linewidth=1.5,
                    )
                    ax1.set_title("Admin – Monthly Tickets")
                    ax1.set_xlabel("Month")
                    ax1.set_ylabel("Tickets")
                    ax1.tick_params(axis="x", rotation=45)
                    fig1.tight_layout()
                    st.pyplot(fig1)

                with c2:
                    fig2, ax2 = plt.subplots(figsize=(4.5, 3))
                    ax2.pie(
                        status_counts.values,
                        labels=status_counts.index,
                        autopct="%1.1f%%",
                        startangle=90,
                    )
                    ax2.set_title("Status Split")
                    ax2.axis("equal")
                    fig2.tight_layout()
                    st.pyplot(fig2)

                # Admin edit any ticket in filtered set
                st.markdown("### ✏️ Edit Ticket")
                t_ids = df_f["id"].tolist()
                tid = st.selectbox("Select Ticket to Edit", t_ids)
                sel = df_f[df_f["id"] == tid].iloc[0]

                email = st.text_input("Email", sel["client_email"])
                mob = st.text_input("Mobile", sel["client_mobile"])
                head = st.text_input("Heading", sel["query_heading"])
                desc = st.text_area("Description", sel["query_description"])
                stat = st.selectbox(
                    "Status",
                    ["Open", "Closed"],
                    index=0 if sel["status"] == "Open" else 1,
                )

                if st.button("Save Changes"):
                    update_query(tid, email, mob, head, desc, stat)
                    st.success("Ticket Updated! (Refresh to see latest data)")
