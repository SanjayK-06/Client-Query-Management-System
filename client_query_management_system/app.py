import os
import streamlit as st
import psycopg2
import pandas as pd
import hashlib
import time
import matplotlib.pyplot as plt
from sqlalchemy import create_engine
from datetime import datetime
from dotenv import load_dotenv

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
# DB CONNECTION
# ========================================
def get_connection():
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
    )

def get_engine():
    return create_engine(
        f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )
    
# ========================================
# LOGIN ANALYTICS HELPERS (FIXED)
# ========================================
def format_time(seconds):
    hrs = int(seconds // 3600)
    mins = int((seconds % 3600) // 60)
    return f"{hrs}h {mins}m"


def get_daily_login_totals():
    query = """
        SELECT username,
        DATE(login_time) AS day,
        SUM(EXTRACT(EPOCH FROM (COALESCE(logout_time, NOW()) - login_time))) AS seconds
        FROM support_activities
        GROUP BY username, day
        ORDER BY day DESC
    """
    return pd.read_sql(query, get_engine())

# ========================================
# PASSWORD HASH
# ========================================
def make_hash(password):
    return hashlib.sha256(password.encode()).hexdigest()

# ========================================
# AUTH FUNCTIONS
# ========================================
def add_user(username, password, role):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO users (username, hashed_password, role) VALUES (%s,%s,%s)",
            (username.upper(), make_hash(password), role),
        )
        conn.commit()
        return True
    except psycopg2.errors.UniqueViolation:
        conn.rollback()
        return False
    finally:
        cur.close()
        conn.close()

def login_user(username, password, role):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT * FROM users WHERE username=%s AND hashed_password=%s AND role=%s",
        (username.upper(), make_hash(password), role),
    )
    user = cur.fetchone()
    if user:
        cur.execute(
            "INSERT INTO support_activities (username, login_time) VALUES (%s,%s)",
            (username.upper(), datetime.now()),
        )
        conn.commit()
    cur.close()
    conn.close()
    return user

def logout_user(username):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "UPDATE support_activities SET logout_time=%s WHERE username=%s AND logout_time IS NULL",
        (datetime.now(), username.upper()),
    )
    conn.commit()
    cur.close()
    conn.close()

# ========================================
# QUERY FUNCTIONS
# ========================================

def update_password(username, new_password):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "UPDATE users SET hashed_password=%s WHERE username=%s",
        (make_hash(new_password), username.upper()),
    )
    conn.commit()
    cur.close()
    conn.close()

def insert_query(email, mobile, heading, desc):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO queries (client_email, client_mobile, query_heading, query_description)
        VALUES (%s,%s,%s,%s)
        """,
        (email, mobile, heading, desc),
    )
    conn.commit()
    cur.close()
    conn.close()

def get_all_queries():
    return pd.read_sql(
        "SELECT * FROM queries ORDER BY date_raised DESC",
        get_engine()
    )

def update_query_status(qid, status):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "UPDATE queries SET status=%s, date_closed=%s WHERE id=%s",
        (status, datetime.now() if status == "Closed" else None, qid),
    )
    conn.commit()
    cur.close()
    conn.close()

# ========================================
# ASSIGNMENT
# ========================================
def bulk_assign_tickets(ticket_ids, supports, priority, sla):
    conn = get_connection()
    cur = conn.cursor()
    for tid in ticket_ids:
        assigned = ",".join([s.upper() for s in supports])
        cur.execute(
            """
            UPDATE queries
            SET priority=%s,
                sla_hours=%s,
                assigned_to=%s
            WHERE id=%s
            """,
            (priority, sla, assigned, tid),
        )
    conn.commit()
    cur.close()
    conn.close()

def get_assigned_open(username):
    return pd.read_sql(
        """
        SELECT *
        FROM queries
        WHERE status='Open'
        AND UPPER(assigned_to) LIKE %s
        ORDER BY date_raised DESC
        """,
        get_engine(),
        params=(f"%{username.upper()}%",),
    )

# ========================================
# WORK NOTE (FIXED to match function call)
# ========================================
def add_comment(qid, note, username=None):  
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE queries SET comments=%s WHERE id=%s", (note, qid))
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
# ------------------ SESSION ------------------
if "page" not in st.session_state:
    st.session_state.page = "login"
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "role" not in st.session_state:
    st.session_state.role = None
if "username" not in st.session_state:
    st.session_state.username = None

# ------------------ STYLES ------------------
def global_styles():
    st.markdown("""
    <style>
    .header-box{
        background:linear-gradient(90deg,#6A0DAD,#4B0082);
        color:white;padding:22px;text-align:center;
        font-size:1.6rem;font-weight:bold;border-radius:14px;
        max-width:1100px;margin:auto
    }
    .main-card{
        background:white;border-radius:14px;
        box-shadow:0 4px 14px rgba(0,0,0,.2);
        max-width:1100px;margin:auto;overflow:hidden
    }
    .row{display:flex;height:460px}
    .image{width:50%;padding:20px}
    .image img{width:60%%;height:auto;object-fit:contain}
    .form{width:50%;padding:40px}
    .stButton>button{
        width:100%;background:#6A0DAD;color:white;font-weight:bold
    }
    </style>
    """, unsafe_allow_html=True)
    

    

# ------------------ LOGIN PAGE (HOME) ------------------
def login_page():
    global_styles()

    # ================= HEADER =================
    st.markdown(
        """
        <div class="login-header">
            Client Query Management System
        </div>
        """,
        unsafe_allow_html=True
    )

    # ================= CARD + FOOTER STYLES =================
    st.markdown("""
        <style>
        /* HEADER */
        .login-header {
            background: linear-gradient(90deg, #6A0DAD, #4B0082);
            color: white;
            padding: 15px;
            text-align: center;
            border-radius: 10px;
            font-size: 24px;
            font-weight: bold;
            margin-bottom: 20px;
        }

        /* REMOVE GAP BETWEEN TWO BOXES */
        [data-testid="column"] {
            padding: 0 !important;
        }

        /* CARD CONTAINER */
        [data-testid="stHorizontalBlock"] > div {
            background: white;
            border-radius: 20px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.12);
            padding: 40px !important;
            min-height: auto;

            display: flex;
            flex-direction: column;
            justify-content: flex-start;
            align-items: stretch;
        }

        /* LEFT IMAGE */
        .login-image {
            display: flex;
            justify-content: center;
            align-items: flex-start;
        }

        .login-image img {
            width: 100%;
            height: auto;
            object-fit: contain;
        }

        /* INPUTS FULL WIDTH */
        .stTextInput, .stSelectbox {
            width: 100% !important;
        }

        /* LOGIN BUTTON — SAME AS HEADER */
        .stButton>button {
            width: 100%;
            border-radius: 30px;
            padding: 10px;
            background: linear-gradient(90deg, #6A0DAD, #4B0082);
            color: white;
            font-weight: 600;
            border: none;
        }

        .stButton>button:hover {
            background-color: #3a2355;
        }

        /* FOOTER */
        .login-footer {
            margin-top: 25px;
            background: linear-gradient(90deg, #6A0DAD, #4B0082);;
            color: white;
            text-align: center;
            padding: 10px;
            border-radius: 10px;
            font-size: 14px;
            font-weight: 500;
        }
        </style>
    """, unsafe_allow_html=True)

    # ================= MAIN LAYOUT (NO GAP) =================
    col1, col2 = st.columns(2, gap="small")

    # ================= LEFT CARD =================
    with col1:
        st.markdown("<div class='login-image'>", unsafe_allow_html=True)
        st.image(
            "https://img.freepik.com/free-vector/customer-support-illustration_23-2148887720.jpg",
            use_column_width=True
        )
        st.markdown("</div>", unsafe_allow_html=True)

    # ================= RIGHT CARD =================
    with col2:
        st.markdown(
            "<h2 style='color:#4b2d6e;margin-top:0;margin-bottom:20px;'>🔐 Login</h2>",
            unsafe_allow_html=True
        )

        u = st.text_input("Username", key="login_user")
        p = st.text_input("Password", type="password", key="login_pass")
        r = st.selectbox("Login as", ["Client", "Support", "Admin"], key="login_role")

        st.write("")

        if st.button("LOG IN"):
            user = login_user(u, p, r)
            if user:
                st.session_state.logged_in = True
                st.session_state.username = u.upper()
                st.session_state.role = r
                st.session_state.page = "home"
                st.rerun()
            else:
                st.error("❌ Invalid credentials")

        st.write("")

        c1, c2 = st.columns(2)
        with c1:
            if st.button("Forgot Password"):
                st.session_state.page = "forgot"
                st.rerun()
        with c2:
            if st.button("Register"):
                st.session_state.page = "register"
                st.rerun()

    # ================= FOOTER =================
    st.markdown(
        """
        <div class="login-footer">
            Made By Sanjay Kannan ❤ 
        </div>
        """,
        unsafe_allow_html=True
    )

# ------------------ FORGOT PASSWORD ------------------

def forgot_password_page():
    global_styles()
    st.markdown("<div class='header-box'>Reset Password</div>", unsafe_allow_html=True)
    st.markdown("<div class='main-card'><div class='form'>", unsafe_allow_html=True)

    u = st.text_input("Username", key="fp_user")
    np = st.text_input("New Password", type="password", key="fp_new")
    cp = st.text_input("Confirm Password", type="password", key="fp_conf")

    msg = st.empty()   #  placeholder

    if st.button("Change Password"):
        if np != cp:
            msg.error("❌ Passwords do not match")
        else:
            update_password(u, np)
            msg.success(
                "✅ Password changed successfully! Please login with your new password."
            )
            time.sleep(5)   
            msg.empty()       
            st.session_state.page = "login"
            st.rerun()

    if st.button("Back to Login"):
        st.session_state.page = "login"
        st.rerun()

    st.markdown("</div></div>", unsafe_allow_html=True)


# ------------------ REGISTER ------------------
def register_page():
    global_styles()
    st.markdown("<div class='header-box'>Register</div>", unsafe_allow_html=True)
    st.markdown("<div class='main-card'><div class='form'>", unsafe_allow_html=True)

    u = st.text_input("Username", key="reg_user")
    p = st.text_input("Password", type="password", key="reg_pass")
    r = st.selectbox("Role", ["Client","Support","Admin"], key="reg_role")

    if st.button("Create Account"):
        if add_user(u, p, r):
            st.success("✅ Registration successful! Your account has been created. Please login to continue.")
            st.session_state.page = "login"
            st.rerun()
        else:
            st.error("❌ Username already exists. Please choose a different username.")

    if st.button("Back to Login"):
        st.session_state.page = "login"
        st.rerun()

    st.markdown("</div></div>", unsafe_allow_html=True)


# ------------------ HOME (ROLE BASED) ------------------
def home_page():
    st.sidebar.write(f"👤 {st.session_state.username} ({st.session_state.role})")
    if st.sidebar.button("Logout"):
        logout_user(st.session_state.username)
        st.session_state.logged_in = False
        st.session_state.page = "login"
        st.rerun()

    # ================= CLIENT =================
    if st.session_state.role == "Client":

        def client_ticket_page():
            pass  # Removed call to undefined ticket_page_styles()

        st.header("📝 Create Ticket")

        with st.form("client_ticket_form"):
            col1, col2 = st.columns(2)
            with col1:
                email = st.text_input("Email")
                category = st.selectbox(
                    "Query Category",
                    ["Technical Issue","Account Issue","Payment Issue","Service Request","Other"]
                )
            with col2:
                mobile = st.text_input("Mobile")
                priority = st.selectbox(
                    "Priority", ["Low","Medium","High","Critical"]
                )

            subject = st.text_input("Ticket Subject")
            description = st.text_area("Detailed Description", height=150)

            if st.form_submit_button("SUBMIT TICKET"):
                if not all([email, mobile, subject, description]):
                    st.error("Please fill all required fields")
                else:
                    insert_query(email, mobile, subject, description)
                    st.success("🎉 Ticket submitted successfully!")


# ================= SUPPORT =================
    if st.session_state.role == "Support":
        st.header("🛠 Support Dashboard")

        if "support_success" not in st.session_state:
            st.session_state.support_success = False

        df = get_all_queries()
        df["date_raised"] = pd.to_datetime(df["date_raised"])

        c1, c2, c3 = st.columns(3)
        with c1: status_filter = st.selectbox("Status", ["All", "Open", "Closed"])
        with c2: date_filter = st.date_input("From Date", df["date_raised"].min().date())
        with c3: id_filter = st.number_input("Ticket ID", min_value=0)

        df_view = df.copy()
        if status_filter != "All":
            df_view = df_view[df_view["status"] == status_filter]
        df_view = df_view[df_view["date_raised"].dt.date >= date_filter]
        if id_filter > 0:
            df_view = df_view[df_view["id"] == id_filter]

        df_view.index = df_view.index + 1
        st.dataframe(df_view, use_container_width=True)

        st.divider()
        st.subheader("🎯 My Assigned Open Tickets")

        my_open = get_assigned_open(st.session_state.username)

        if not my_open.empty:
            my_open["date_raised"] = pd.to_datetime(my_open["date_raised"])
            st.dataframe(
                my_open[["id","query_heading","priority","sla_hours","date_raised"]],
                use_container_width=True
            )

            ticket_id = st.selectbox("Select Ticket", my_open["id"])
            ticket = my_open[my_open["id"] == ticket_id].iloc[0]

            st.markdown(
            f"""
            ### 🎫 Ticket Details
            **Heading:**        {ticket['query_heading']}  
            **Description:**    {ticket['query_description']}  
            **Priority:**       {ticket['priority']}  
            **SLA (hrs):**      {ticket['sla_hours']}  
            **Raised On:**      {ticket['date_raised']}  
            """
            )

            note = st.text_area("Add Work Note")
            new_status = st.selectbox("Change Status", ["Open", "Closed"])

            if st.button("Save Update"):
                update_query_status(ticket_id, new_status)
                if note.strip():
                    add_comment(ticket_id, note, st.session_state.username)
                st.session_state.support_success = True
                st.rerun()
        else:
            st.info("No open assigned tickets.")
        if st.session_state.support_success:
            st.success("✅ Ticket updated successfully!")
            st.session_state.support_success = False


# ================= ADMIN =================
    if st.session_state.role == "Admin":
        st.header("🧑‍💼 Admin Dashboard")

        if "admin_assign_success" not in st.session_state:
            st.session_state.admin_assign_success = False

        df = get_all_queries()
        df["date_raised"] = pd.to_datetime(df["date_raised"])

        # ---------- METRICS ----------
        st.markdown("### 📊 Ticket Overview")
        m1, m2, m3 = st.columns(3)

        m1.markdown(
            f"<div class='metric-card'><div class='metric-label'>Total Tickets</div><div class='metric-number'>{len(df)}</div></div>",
            unsafe_allow_html=True,
        )
        m2.markdown(
            f"<div class='metric-card'><div class='metric-label'>Open Tickets</div><div class='metric-number'>{len(df[df.status=='Open'])}</div></div>",
            unsafe_allow_html=True,
        )
        m3.markdown(
            f"<div class='metric-card'><div class='metric-label'>Closed Tickets</div><div class='metric-number'>{len(df[df.status=='Closed'])}</div></div>",
            unsafe_allow_html=True,
        )

        st.markdown("---")

        c1, c2, c3 = st.columns(3)
        with c1: status = st.selectbox("Status", ["All", "Open", "Closed"])
        with c2: date_val = st.date_input("From Date", df["date_raised"].min().date())
        with c3: tid = st.number_input("Ticket ID", min_value=0)

        dfv = df.copy()
        if status != "All":
            dfv = dfv[dfv["status"] == status]
        dfv = dfv[dfv["date_raised"].dt.date >= date_val]
        if tid > 0:
            dfv = dfv[dfv["id"] == tid]

        dfv.index = dfv.index + 1
        st.dataframe(dfv, use_container_width=True)

        st.divider()
        st.subheader("📦 Assign Tickets")

        ticket_ids = st.multiselect("Select Tickets", dfv["id"])
        supports = pd.read_sql(
            "SELECT username FROM users WHERE role='Support'",
            get_engine()
        )["username"]

        assign_to = st.multiselect("Assign To", supports)
        pr = st.selectbox("Priority", ["Low", "Medium", "High", "Critical"])
        sla = st.selectbox("SLA Hours", [4, 8, 24, 48])

        if st.button("Assign"):
            if ticket_ids and assign_to:
                bulk_assign_tickets(ticket_ids, assign_to, pr, sla)
                st.session_state.admin_assign_success = True
                st.rerun()
            else:
                st.error("Select tickets and support users first")
        if st.session_state.admin_assign_success:
            st.success("✅ Tickets assigned successfully!")
            st.session_state.admin_assign_success = False
        # ---------- ADMIN ANALYTICS ----------
        st.markdown("## 📊 Admin Analytics")
        st.caption("Ticket trends and resolution distribution")

        df_f = dfv.copy()

        if not df_f.empty:
            df_f["month"] = (
            df_f["date_raised"]
            .dt.tz_localize(None)
            .dt.to_period("M")
            .dt.to_timestamp()
            )

            monthly_counts = (
                df_f.groupby("month")
                .size()
                .reset_index(name="count")
                .sort_values("month")
            )

            status_counts = df_f["status"].value_counts()

            c1, c2 = st.columns(2)

            with c1:
                st.markdown("### 📅 Monthly Ticket Volume")
                fig1, ax1 = plt.subplots(figsize=(5, 3))
                ax1.bar(
                    monthly_counts["month"].dt.strftime("%Y-%m"),
                    monthly_counts["count"],
                )
                ax1.tick_params(axis="x", rotation=45)
                st.pyplot(fig1)

            with c2:
                st.markdown("### 📊 Ticket Status Distribution")
                fig2, ax2 = plt.subplots(figsize=(4.5, 3))
                ax2.pie(
                    status_counts.values,
                    labels=status_counts.index,
                    autopct="%1.1f%%",
                    startangle=90,
                )
                ax2.axis("equal")
                st.pyplot(fig2)
        else:
            st.info("No data available for analytics.")

        st.markdown("---")

        # ---------- DAILY LOGIN TOTALS ----------
        st.subheader("📅 Daily Login Details")

        daily = get_daily_login_totals()
        daily["day"] = pd.to_datetime(daily["day"]).dt.date

        today = pd.Timestamp.today().date()
        daily = daily[daily["day"] == today]

        daily["Total Time"] = daily["seconds"].apply(format_time)

        st.dataframe(
            daily[["username", "day", "Total Time"]],
            use_container_width=True
        )

        # ---------- WEEKLY LOGIN TOTALS ----------
        st.subheader("📅 Weekly Login Details")

        weekly = get_daily_login_totals()
        weekly["day"] = pd.to_datetime(weekly["day"])

        today = pd.Timestamp.today()
        start_date = today - pd.Timedelta(days=today.weekday())
        end_date = start_date + pd.Timedelta(days=4)

        weekly = weekly[
            (weekly["day"] >= start_date) &
            (weekly["day"] <= end_date)
        ]

        weekly = (
            weekly
            .groupby("username", as_index=False)["seconds"]
            .sum()
        )

        week_label = f"{start_date.strftime('%d/%m/%y')} to {end_date.strftime('%d/%m/%y')}"
        weekly["week"] = week_label
        weekly["Total Time"] = weekly["seconds"].apply(format_time)

        st.dataframe(
            weekly[["username", "week", "Total Time"]],
            use_container_width=True
        )

def run_app():
    if st.session_state.page == "login":
        login_page()
    elif st.session_state.page == "forgot":
        forgot_password_page()
    elif st.session_state.page == "register":
        register_page()
    elif st.session_state.page == "home" and st.session_state.logged_in:
        home_page()


run_app()


