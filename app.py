import streamlit as st
import pandas as pd
import sqlite3
import hashlib
import hmac
import html
import secrets
from datetime import datetime, date, timedelta
import altair as alt
import extra_streamlit_components as stx
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def get_secret(key, default=None):
    """Đọc cấu hình bí mật từ .streamlit/secrets.toml (hoặc Secrets trên Streamlit Cloud)."""
    try:
        return st.secrets[key]
    except Exception:
        return default


# 📍 1. ĐƯỜNG LINK TRANG WEB (đặt APP_URL trong Secrets)
APP_URL = get_secret("APP_URL", "https://your-app.streamlit.app")

# CẤU HÌNH GIAO DIỆN
st.set_page_config(
    page_title="ShipControl - Quản Lý Công Việc Tàu",
    page_icon="🚢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# KHỞI TẠO COOKIE MANAGER
cookie_manager = stx.CookieManager(key="shipcontrol_cookie_mgr")
SESSION_COOKIE = "shipcontrol_session"
SESSION_DAYS = 30

# 2. KẾT NỐI CƠ SỞ DỮ LIỆU SQLITE & AUTO-MIGRATION
conn = sqlite3.connect("ship_control.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        fullname TEXT,
        role TEXT DEFAULT 'Pending',
        is_deleted INTEGER DEFAULT 0
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS custom_cost_codes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        code TEXT UNIQUE,
        name TEXT,
        description TEXT,
        is_deleted INTEGER DEFAULT 0
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        task_id TEXT UNIQUE,
        task_name TEXT,
        task_cost_code TEXT,
        block TEXT,
        description TEXT,
        initial_by TEXT,
        initial_date TEXT,
        area TEXT,
        deck TEXT,
        frame TEXT,
        in_charge_by TEXT,
        plan_start_date TEXT,
        plan_finish_date TEXT,
        progress INTEGER DEFAULT 0,
        remark TEXT,
        image_path TEXT,
        is_deleted INTEGER DEFAULT 0
    )
''')

# AUTO-MIGRATION
try:
    cursor.execute("ALTER TABLE users ADD COLUMN role TEXT DEFAULT 'Pending'")
except sqlite3.OperationalError:
    pass

try:
    cursor.execute("ALTER TABLE users ADD COLUMN is_deleted INTEGER DEFAULT 0")
except sqlite3.OperationalError:
    pass

tasks_schema_updates = {
    "task_cost_code": "TEXT", "block": "TEXT", "description": "TEXT",
    "initial_by": "TEXT", "initial_date": "TEXT", "area": "TEXT",
    "deck": "TEXT", "frame": "TEXT", "in_charge_by": "TEXT",
    "plan_start_date": "TEXT", "plan_finish_date": "TEXT",
    "progress": "INTEGER DEFAULT 0", "remark": "TEXT",
    "image_path": "TEXT", "is_deleted": "INTEGER DEFAULT 0"
}
cursor.execute("PRAGMA table_info(tasks)")
existing_cols = [col[1] for col in cursor.fetchall()]
for col_name, col_type in tasks_schema_updates.items():
    if col_name not in existing_cols:
        try:
            cursor.execute(f"ALTER TABLE tasks ADD COLUMN {col_name} {col_type}")
        except Exception:
            pass


# 🏭 CỘT WORKSHOP CHO NGƯỜI DÙNG (mỗi tài khoản thuộc 1 workshop / phòng ban)
try:
    cursor.execute("ALTER TABLE users ADD COLUMN workshop TEXT")
except sqlite3.OperationalError:
    pass

# 👥 TEAM & GIAO VIỆC
#   users.leader_id          : Worker thuộc team của Team Leader / Foreman nào
#   tasks.assigned_leader_id : WOS Manager giao việc cho Team Leader / Foreman nào
#   tasks.assigned_worker_id : Team Leader / Foreman giao việc cho Worker nào
for _sql in ["ALTER TABLE users ADD COLUMN leader_id INTEGER",
             "ALTER TABLE tasks ADD COLUMN assigned_leader_id INTEGER",
             "ALTER TABLE tasks ADD COLUMN assigned_worker_id INTEGER"]:
    try:
        cursor.execute(_sql)
    except sqlite3.OperationalError:
        pass

LEADER_ROLES = ["Team Leader", "Foreman"]

# 🏭 DANH SÁCH WORKSHOP / PHÒNG BAN MẶC ĐỊNH (theo bảng Excel)
DEFAULT_WORKSHOPS = [
    ("WOS_01", "Fabrication WS"),
    ("WOS_02", "Hull WS 02"),
    ("WOS_03", "Hull WS 03"),
    ("WOS_04", "Outfitting WS"),
    ("WOS_05", "Piping WS"),
    ("WOS_06", "Painting WS"),
    ("DEP_01", "Technical Dept"),
    ("DEP_02", "QA QC Department"),
    ("DEP_03", "Safety Department"),
    ("DEP_04", "Planing Department"),
    ("DEP_05", "Project Department"),
    ("DEP_06", "Finance Department"),
    ("DEP_07", "HR Department"),
    ("DEP_08", "Security Department"),
]
for ws_code, ws_name in DEFAULT_WORKSHOPS:
    cursor.execute("INSERT OR IGNORE INTO custom_cost_codes (code, name, description, is_deleted) VALUES (?, ?, '', 0)",
                   (ws_code, ws_name))

# 🔐 BẢNG PHIÊN ĐĂNG NHẬP (cookie chỉ chứa token ngẫu nhiên, không chứa username)
cursor.execute('''
    CREATE TABLE IF NOT EXISTS sessions (
        token TEXT PRIMARY KEY,
        user_id INTEGER,
        expires_at TEXT
    )
''')


# ==========================================
# 🔑 HÀM BẢO MẬT MẬT KHẨU
# ==========================================
PBKDF2_ITERATIONS = 200_000

def hash_password(password):
    """Băm mật khẩu bằng PBKDF2-SHA256 có salt ngẫu nhiên."""
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, PBKDF2_ITERATIONS)
    return f"pbkdf2${PBKDF2_ITERATIONS}${salt.hex()}${digest.hex()}"

def verify_password(password, stored):
    """Kiểm tra mật khẩu. Hỗ trợ cả hash SHA-256 kiểu cũ để người dùng cũ vẫn đăng nhập được."""
    if not stored:
        return False
    if stored.startswith("pbkdf2$"):
        try:
            _, iters, salt_hex, digest_hex = stored.split("$")
            digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), bytes.fromhex(salt_hex), int(iters))
            return hmac.compare_digest(digest.hex(), digest_hex)
        except Exception:
            return False
    legacy = hashlib.sha256(password.encode("utf-8")).hexdigest()
    return hmac.compare_digest(legacy, stored)

def is_legacy_hash(stored):
    return bool(stored) and not stored.startswith("pbkdf2$")

LEGACY_DEFAULT_ADMIN_HASH = hashlib.sha256("admin123".encode()).hexdigest()


# ==========================================
# 🎫 HÀM QUẢN LÝ PHIÊN ĐĂNG NHẬP
# ==========================================
def create_session(user_id):
    token = secrets.token_urlsafe(32)
    expires = (datetime.now() + timedelta(days=SESSION_DAYS)).isoformat()
    cursor.execute("INSERT INTO sessions (token, user_id, expires_at) VALUES (?, ?, ?)", (token, user_id, expires))
    conn.commit()
    return token

def get_user_by_session(token):
    row = cursor.execute("""
        SELECT u.id, u.username, u.fullname, u.role, u.workshop
        FROM sessions s JOIN users u ON u.id = s.user_id
        WHERE s.token = ? AND s.expires_at > ? AND u.is_deleted = 0
    """, (token, datetime.now().isoformat())).fetchone()
    return row

def delete_session(token):
    cursor.execute("DELETE FROM sessions WHERE token = ?", (token,))
    conn.commit()

def delete_user_sessions(user_id):
    cursor.execute("DELETE FROM sessions WHERE user_id = ?", (user_id,))
    conn.commit()

# Dọn các phiên đã hết hạn
cursor.execute("DELETE FROM sessions WHERE expires_at <= ?", (datetime.now().isoformat(),))


# TẠO TÀI KHOẢN WOS MANAGER MẶC ĐỊNH (mật khẩu lấy từ Secrets, KHÔNG hardcode)
admin_exists = cursor.execute("SELECT id FROM users WHERE username = 'admin'").fetchone()
if not admin_exists:
    initial_admin_pw = get_secret("ADMIN_PASSWORD")
    if not initial_admin_pw:
        initial_admin_pw = secrets.token_urlsafe(12)
        print("=" * 60)
        print(f"[ShipControl] Mật khẩu admin tạm thời: {initial_admin_pw}")
        print("Hãy đăng nhập và đổi mật khẩu ngay, hoặc đặt ADMIN_PASSWORD trong Secrets.")
        print("=" * 60)
    cursor.execute("INSERT INTO users (username, password, fullname, role, is_deleted) VALUES (?, ?, ?, ?, 0)",
                   ('admin', hash_password(initial_admin_pw), 'System Admin', 'Admin'))

# Tài khoản 'admin' luôn là Admin hệ thống (chỉ cấp quyền WOS Manager + workshop)
cursor.execute("UPDATE users SET role = 'Admin' WHERE username = 'admin'")

# 🆘 KHÔI PHỤC TÀI KHOẢN ADMIN: đặt RESET_ADMIN_PASSWORD trong Secrets để đặt lại mật khẩu admin.
# Sau khi đăng nhập được, hãy XÓA dòng RESET_ADMIN_PASSWORD khỏi Secrets.
reset_admin_pw = get_secret("RESET_ADMIN_PASSWORD")
if reset_admin_pw:
    cursor.execute("UPDATE users SET password = ?, role = 'Admin', is_deleted = 0 WHERE username = 'admin'",
                   (hash_password(str(reset_admin_pw)),))

conn.commit()


# 📧 HÀM GỬI EMAIL THÔNG BÁO CÓ NGƯỜI ĐĂNG KÝ MỚI
# Email chỉ thông báo. Việc cấp Role phải làm trong app bằng tài khoản WOS Manager,
# nên không ai có thể tự cấp quyền cho mình bằng cách sửa đường link.
def send_new_user_email(target_username, target_fullname):
    sender_email = get_secret("SMTP_EMAIL")
    sender_password = get_secret("SMTP_APP_PASSWORD")
    receiver_email = get_secret("ADMIN_EMAIL", sender_email)
    if not sender_email or not sender_password or not receiver_email:
        print("[ShipControl] Chưa cấu hình SMTP trong Secrets - bỏ qua gửi email.")
        return False

    safe_user = html.escape(target_username)
    safe_name = html.escape(target_fullname)
    subject = f"🔔 [ShipControl] Tài khoản mới chờ duyệt: {target_username}"
    body = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; padding: 20px; border: 1px solid #e2e8f0; border-radius: 10px;">
        <h2 style="color: #0284c7;">🚢 CÓ TÀI KHOẢN ĐĂNG KÝ MỚI</h2>
        <p>Có người dùng vừa đăng ký trên hệ thống <b>ShipControl</b>:</p>
        <hr>
        <p><b>Họ và Tên:</b> {safe_name}</p>
        <p><b>Tên đăng nhập (Username):</b> {safe_user}</p>
        <hr>
        <p>Đăng nhập bằng tài khoản <b>Admin</b> hoặc <b>WOS Manager</b>, vào mục <b>👥 Quản Lý Phân Quyền</b> để cấp Role.</p>
        <a href="{APP_URL}" style="display: inline-block; background-color: #16a34a; color: white; padding: 10px 18px; text-decoration: none; border-radius: 6px; font-weight: bold;">👉 Mở ShipControl</a>
    </div>
    """

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'html'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587, timeout=15)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, receiver_email, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        print("Lỗi gửi email:", e)
        return False

# --- KHỞI TẠO STATE THEME, AUTH & SUB-TABS ---
if "theme_mode" not in st.session_state:
    st.session_state["theme_mode"] = "Light"

if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if "user_info" not in st.session_state:
    st.session_state["user_info"] = None

if "auth_tab" not in st.session_state:
    st.session_state["auth_tab"] = "login"

if "current_menu" not in st.session_state:
    st.session_state["current_menu"] = "🧰 Bảng Công Việc"

if "edit_sub_tab" not in st.session_state:
    st.session_state["edit_sub_tab"] = "task"

if "trash_sub_tab" not in st.session_state:
    st.session_state["trash_sub_tab"] = "task"

# --- CÔNG TẮC CHUYỂN THEME ---
st.sidebar.markdown("<div style='padding-top: 10px;'></div>", unsafe_allow_html=True)
dark_mode_on = st.sidebar.toggle("🌙 Chế độ Tối (Dark)", value=(st.session_state["theme_mode"] == "Dark"), key="dark_toggle")
st.session_state["theme_mode"] = "Dark" if dark_mode_on else "Light"

is_dark = st.session_state["theme_mode"] == "Dark"

main_bg = "#0f172a" if is_dark else "#f8f9fa"
text_color = "#ffffff" if is_dark else "#000000"
input_bg = "#1e293b" if is_dark else "#ffffff"
input_text = "#ffffff" if is_dark else "#000000"
border_color = "#334155" if is_dark else "#cbd5e1"

st.markdown(f"""
    <style>
    .stApp, .main {{
        background-color: {main_bg} !important;
        color: {text_color} !important;
    }}
    
    section[data-testid="stSidebar"] {{
        background-color: #0284c7 !important;
        width: 330px !important;
    }}
    
    .sidebar-header {{
        font-size: 2rem;
        font-weight: 800;
        color: #facc15;
        text-align: center;
        padding: 10px 0;
        margin-bottom: 10px;
    }}

    .made-by-minh {{
        background-color: #facc15;
        color: #0369a1;
        font-size: 1.5rem;
        font-weight: 900;
        font-style: italic;
        text-align: center;
        padding: 10px;
        border-radius: 12px;
        margin-top: 15px;
    }}

    .user-card {{
        background-color: rgba(255, 255, 255, 0.15);
        padding: 12px;
        border-radius: 12px;
        margin-top: 15px;
        text-align: center;
        color: white;
    }}

    div.stButton > button {{
        width: 100% !important;
        min-height: 55px !important;
        border-radius: 10px !important;
        transition: all 0.2s ease !important;
        margin-bottom: 8px !important;
    }}

    div.stButton > button[kind="primary"],
    div.stButton > button[data-testid="baseButton-primary"] {{
        background-color: #22c55e !important;
        background-image: none !important;
        border: 2px solid #16a34a !important;
        box-shadow: 0 4px 10px rgba(34, 197, 94, 0.3) !important;
    }}
    
    div.stButton > button[kind="primary"] *,
    div.stButton > button[data-testid="baseButton-primary"] * {{
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
        font-size: 1.2rem !important;
        font-weight: 900 !important;
        opacity: 1 !important;
    }}

    div.stButton > button[kind="secondary"],
    div.stButton > button[data-testid="baseButton-secondary"] {{
        background-color: #e2e8f0 !important;
        background-image: none !important;
        border: 2px solid #cbd5e1 !important;
    }}
    
    div.stButton > button[kind="secondary"] *,
    div.stButton > button[data-testid="baseButton-secondary"] * {{
        color: #000000 !important;
        -webkit-text-fill-color: #000000 !important;
        font-size: 1.2rem !important;
        font-weight: 900 !important;
        opacity: 1 !important;
    }}

    .big-table-title {{
        font-size: 1.8rem !important;
        font-weight: 800 !important;
        color: {text_color} !important;
        margin-top: 10px !important;
        margin-bottom: 15px !important;
    }}

    div[data-testid="stDataFrame"] th, 
    div[data-testid="stTable"] th {{
        font-size: 1.15rem !important;
        font-weight: 800 !important;
        padding: 12px 8px !important;
    }}

    div[data-testid="stDataFrame"] td, 
    div[data-testid="stTable"] td,
    div[data-testid="stDataFrame"] [role="gridcell"] {{
        font-size: 1.1rem !important;
        font-weight: 600 !important;
        padding: 10px 8px !important;
    }}

    div[data-testid="stAlert"] {{
        background-color: #fef08a !important;
        border: 2px solid #eab308 !important;
        border-radius: 10px !important;
    }}
    
    div[data-testid="stAlert"] * {{
        color: #854d0e !important;
        -webkit-text-fill-color: #854d0e !important;
        font-size: 1.15rem !important;
        font-weight: 800 !important;
    }}

    input, textarea, select, div[data-baseweb="select"] > div {{
        background-color: {input_bg} !important;
        color: {input_text} !important;
        border: 1px solid {border_color} !important;
        border-radius: 8px !important;
        font-size: 1.1rem !important;
    }}

    /* Chữ của nút chọn Role (radio), nhãn các ô nhập và số liệu báo cáo: luôn cùng màu chữ chính */
    .stRadio label, .stRadio label p, .stRadio div[role="radiogroup"] *,
    .stNumberInput label, .stNumberInput label p,
    .stCheckbox label, .stCheckbox label p,
    .stMain [data-testid="stWidgetLabel"], .stMain [data-testid="stWidgetLabel"] p,
    .main [data-testid="stWidgetLabel"], .main [data-testid="stWidgetLabel"] p,
    [data-testid="stMetricLabel"], [data-testid="stMetricLabel"] *,
    [data-testid="stMetricValue"], [data-testid="stMetricValue"] * {{
        color: {text_color} !important;
        -webkit-text-fill-color: {text_color} !important;
        opacity: 1 !important;
    }}
    .stRadio div[role="radiogroup"] p {{
        font-size: 1.1rem !important;
        font-weight: 700 !important;
    }}

    .stTextInput label, .stTextArea label, .stSelectbox label, .stDateInput label, .stSlider label {{
        color: {text_color} !important;
        font-weight: 700 !important;
        font-size: 1.1rem !important;
    }}

    div[data-testid="stFormSubmitButton"] > button {{
        background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%) !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 16px 24px !important;
        width: 100% !important;
        min-height: 55px !important;
    }}

    div[data-testid="stFormSubmitButton"] > button *,
    div[data-testid="stFormSubmitButton"] > button p {{
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
        font-size: 1.25rem !important;
        font-weight: 900 !important;
    }}

    .main-title {{
        font-size: 2.3rem;
        color: {text_color} !important;
        font-weight: 800;
        text-align: center;
        padding: 10px 0;
        border-bottom: 3px solid #22c55e;
        margin-bottom: 25px;
    }}
    </style>
""", unsafe_allow_html=True)

# --- TIÊU ĐỀ TRANG ---
st.markdown("<div class='main-title'>🚢 SHIPCONTROL - QUẢN LÝ CÔNG VIỆC TÀU</div>", unsafe_allow_html=True)

# --- KHỞI TẠO KHỔI PHỤC ĐĂNG NHẬP CHUẨN ĐỒNG BỘ COOKIE ---
all_cookies = cookie_manager.get_all()

if all_cookies is None:
    st.stop()

saved_token = all_cookies.get(SESSION_COOKIE)

if not st.session_state["logged_in"] and saved_token:
    user_db = get_user_by_session(saved_token)
    if user_db and user_db[3] and user_db[3] != 'Pending':
        st.session_state["logged_in"] = True
        st.session_state["session_token"] = saved_token
        st.session_state["user_info"] = {"id": user_db[0], "username": user_db[1], "fullname": user_db[2], "role": user_db[3], "workshop": user_db[4]}
        st.rerun()

# Nếu đang đăng nhập, kiểm tra lại mỗi lần tải trang: tài khoản bị khóa hoặc đổi Role sẽ có hiệu lực ngay
if st.session_state["logged_in"]:
    fresh = cursor.execute("SELECT fullname, role, workshop FROM users WHERE id = ? AND is_deleted = 0",
                           (st.session_state["user_info"]["id"],)).fetchone()
    if not fresh or not fresh[1] or fresh[1] == 'Pending':
        tok = st.session_state.get("session_token")
        if tok:
            delete_session(tok)
        st.session_state["logged_in"] = False
        st.session_state["user_info"] = None
        st.rerun()
    st.session_state["user_info"]["fullname"] = fresh[0]
    st.session_state["user_info"]["role"] = fresh[1]
    st.session_state["user_info"]["workshop"] = fresh[2]

# ==========================================
# 🔐 HỆ THỐNG XÁC THỰC
# ==========================================
if not st.session_state["logged_in"]:
    st.sidebar.markdown("<div class='sidebar-header'>🔐 Xác Thực</div>", unsafe_allow_html=True)
    st.sidebar.info("Vui lòng đăng nhập hoặc đăng ký để tiếp tục.")
    st.sidebar.markdown("<div class='made-by-minh'>Made By Minh</div>", unsafe_allow_html=True)

    col_space1, col_center, col_space2 = st.columns([1, 2, 1])
    
    with col_center:
        is_login = st.session_state["auth_tab"] == "login"
        t_col1, t_col2 = st.columns(2)
        
        with t_col1:
            if st.button("🔑 Đăng Nhập", type="primary" if is_login else "secondary", use_container_width=True, key="btn_auth_tab_login"):
                st.session_state["auth_tab"] = "login"
                st.rerun()
                
        with t_col2:
            if st.button("📝 Đăng Ký Tài Khoản", type="primary" if not is_login else "secondary", use_container_width=True, key="btn_auth_tab_reg"):
                st.session_state["auth_tab"] = "register"
                st.rerun()

        st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)

        if st.session_state["auth_tab"] == "login":
            with st.form("form_login_system"):
                login_user = st.text_input("Tên tài khoản (Username):")
                login_pass = st.text_input("Mật khẩu (Password):", type="password")
                btn_login = st.form_submit_button("🚀 ĐĂNG NHẬP")

                if btn_login:
                    if not login_user or not login_pass:
                        st.error("Vui lòng nhập đầy đủ Username và Mật khẩu!")
                    else:
                        user = cursor.execute("SELECT id, username, password, fullname, role, workshop FROM users WHERE username = ? AND is_deleted = 0", (login_user.strip(),)).fetchone()
                        if user and not verify_password(login_pass, user[2]):
                            user = None
                        if user:
                            # Tự động nâng cấp hash cũ (SHA-256) lên PBKDF2
                            if is_legacy_hash(user[2]):
                                cursor.execute("UPDATE users SET password = ? WHERE id = ?", (hash_password(login_pass), user[0]))
                                conn.commit()
                            user_role = user[4] if len(user) > 4 and user[4] else 'Pending'
                            
                            if user_role == 'Pending':
                                st.warning("⏳ Tài khoản của bạn đang chờ Admin / WOS Manager cấp Role. Vui lòng quay lại sau!")
                            else:
                                st.session_state["logged_in"] = True
                                st.session_state["user_info"] = {"id": user[0], "username": user[1], "fullname": user[3], "role": user_role, "workshop": user[5]}
                                
                                token = create_session(user[0])
                                st.session_state["session_token"] = token
                                cookie_manager.set(SESSION_COOKIE, token, max_age=SESSION_DAYS*24*3600)
                                st.success(f"Chào mừng {user[3]} ({user_role}) đã quay trở lại!")
                                st.rerun()
                        else:
                            st.error("Sai tên tài khoản, mật khẩu hoặc tài khoản đã bị khóa/xóa!")

        else:
            with st.form("form_register_system"):
                reg_fullname = st.text_input("Họ và Tên:")
                reg_user = st.text_input("Tên đăng nhập mới (Username):")
                reg_pass = st.text_input("Mật khẩu mới:", type="password")
                reg_confirm = st.text_input("Xác nhận lại mật khẩu:", type="password")
                
                btn_register = st.form_submit_button("✨ ĐĂNG KÝ NGAY")

                if btn_register:
                    reg_user = reg_user.strip()
                    reg_fullname = reg_fullname.strip()
                    if not reg_fullname or not reg_user or not reg_pass:
                        st.error("Vui lòng điền đầy đủ các thông tin!")
                    elif len(reg_pass) < 8:
                        st.error("Mật khẩu phải có ít nhất 8 ký tự!")
                    elif len(reg_user) > 50 or len(reg_fullname) > 100:
                        st.error("Username hoặc Họ tên quá dài!")
                    elif reg_pass != reg_confirm:
                        st.error("Mật khẩu xác nhận không trùng khớp!")
                    else:
                        try:
                            # LƯU VỚI ROLE LÀ Pending CHỜ ADMIN DUYỆT EMAIL
                            cursor.execute("INSERT INTO users (username, password, fullname, role, is_deleted) VALUES (?, ?, ?, 'Pending', 0)", 
                                           (reg_user, hash_password(reg_pass), reg_fullname))
                            conn.commit()
                            
                            # GỬI EMAIL THÔNG BÁO ĐẾN ADMIN (không chứa link cấp quyền)
                            send_new_user_email(reg_user, reg_fullname)
                            
                            st.success("🎉 Đăng ký thành công! Tài khoản đang chờ WOS Manager phê duyệt Role.")
                        except sqlite3.IntegrityError:
                            st.error("Tên đăng nhập này đã tồn tại, vui lòng chọn tên khác!")

# ==========================================
# 🚢 GIAO DIỆN CHÍNH
# ==========================================
else:
    user_data = st.session_state["user_info"]
    current_role = user_data.get("role", "Worker")

    st.sidebar.markdown("<div class='sidebar-header'>☸️ Control Menu</div>", unsafe_allow_html=True)

    is_admin = current_role == "Admin"
    is_manager_up = current_role in ["Admin", "WOS Manager"]

    if is_manager_up:
        menu_options = [
            "🧰 Bảng Công Việc", 
            "⚙️ Quản Lý Danh Mục",
            "➕ Thêm Công Việc", 
            "📋 Giao Việc",
            "✏️ Chỉnh Sửa/Xóa",
            "👥 Quản Lý Phân Quyền",
            "🗑️ Thùng Rác",
            "📊 Báo Cáo & Khai Báo",
            "🔑 Đổi Mật Khẩu"
        ]
    elif current_role == "Foreman":
        menu_options = [
            "🧰 Bảng Công Việc", 
            "⚙️ Quản Lý Danh Mục",
            "➕ Thêm Công Việc", 
            "📋 Giao Việc",
            "✏️ Chỉnh Sửa/Xóa",
            "📊 Báo Cáo & Khai Báo",
            "🔑 Đổi Mật Khẩu"
        ]
    elif current_role == "Team Leader":
        menu_options = [
            "🧰 Bảng Công Việc", 
            "➕ Thêm Công Việc",
            "📋 Giao Việc",
            "📊 Báo Cáo & Khai Báo",
            "🔑 Đổi Mật Khẩu"
        ]
    else:
        menu_options = [
            "🧰 Bảng Công Việc",
            "📊 Báo Cáo & Khai Báo",
            "🔑 Đổi Mật Khẩu"
        ]

    for item in menu_options:
        is_selected = (st.session_state["current_menu"] == item)
        if st.sidebar.button(
            item, 
            type="primary" if is_selected else "secondary", 
            use_container_width=True, 
            key=f"btn_menu_{item}"
        ):
            st.session_state["current_menu"] = item
            st.rerun()

    menu = st.session_state["current_menu"]
    
    role_icons = {
        "Admin": "🛡️ Admin",
        "WOS Manager": "👑 WOS Manager",
        "Foreman": "👔 Foreman",
        "Team Leader": "🧢 Team Leader",
        "Worker": "👷 Worker"
    }
    role_badge = role_icons.get(current_role, f"👤 {current_role}")

    st.sidebar.markdown(f"""
        <div class='user-card'>
            👋 <b>WELCOME</b><br>
            <span style='font-size: 1.1rem; font-weight: 800;'>{html.escape(str(user_data['fullname']))}</span><br>
            <small>@{html.escape(str(user_data['username']))} | <b>{html.escape(role_badge)}</b></small>
            {"<br><small>🏭 " + html.escape(str(user_data.get('workshop'))) + "</small>" if user_data.get('workshop') else ""}
        </div>
    """, unsafe_allow_html=True)

    st.sidebar.markdown("<div class='made-by-minh'>Made By Minh</div>", unsafe_allow_html=True)

    my_pw = cursor.execute("SELECT password FROM users WHERE id = ?", (user_data['id'],)).fetchone()
    if my_pw and verify_password("admin123", my_pw[0]):
        st.error("⚠️ Tài khoản này vẫn dùng mật khẩu mặc định 'admin123'. Vào mục 🔑 Đổi Mật Khẩu và đổi NGAY!")

    if st.sidebar.button("🚪 Đăng Xuất", type="secondary", key="btn_logout_bottom"):
        tok = st.session_state.get("session_token")
        if tok:
            delete_session(tok)
        try:
            cookie_manager.delete(SESSION_COOKIE)
        except Exception:
            pass
        st.session_state["logged_in"] = False
        st.session_state["user_info"] = None
        st.rerun()

    # 1. BẢNG CÔNG VIỆC
    if menu == "🧰 Bảng Công Việc":
        st.markdown("<div class='big-table-title'>📋 Bảng Quản Lý Tiến Độ Công Việc</div>", unsafe_allow_html=True)
        
        df = pd.read_sql_query("""
            SELECT 
                t.id AS _id,
                t.assigned_leader_id AS _leader_id,
                t.assigned_worker_id AS _worker_id,
                t.task_id AS 'Task ID', 
                t.task_name AS 'Task Name', 
                t.task_cost_code AS 'WS Cost Code', 
                t.description AS 'Description',
                t.initial_by AS 'Initial By', 
                t.initial_date AS 'Initial Date', 
                t.block AS 'Block', 
                t.area AS 'Area', 
                t.deck AS 'Deck', 
                t.frame AS 'Frame', 
                t.in_charge_by AS 'In Charge By', 
                l.fullname AS 'Leader / Foreman',
                w.fullname AS 'Worker',
                t.plan_start_date AS 'Plan Start Date', 
                t.plan_finish_date AS 'Plan Finish Date', 
                t.progress AS 'Progress (%)', 
                t.remark AS 'Remark' 
            FROM tasks t
            LEFT JOIN users l ON l.id = t.assigned_leader_id
            LEFT JOIN users w ON w.id = t.assigned_worker_id
            WHERE t.is_deleted = 0
        """, conn)

        my_id = user_data['id']
        if current_role == "Worker":
            df = df[df['_worker_id'] == my_id]
            st.caption("👷 Đây là các công việc được giao cho bạn.")
        elif current_role in LEADER_ROLES:
            only_team = st.toggle("Chỉ xem công việc của team tôi", value=True)
            if only_team:
                df = df[df['_leader_id'] == my_id]
        
        if df.empty:
            st.info("Chưa có công việc nào để hiển thị.")
        else:
            st.dataframe(df.drop(columns=['_id', '_leader_id', '_worker_id']), use_container_width=True, height=400)
            
            st.markdown("---")
            st.markdown("### ⚡ Cập Nhật Tiến Độ Công Việc Nhanh")

            # Ai được cập nhật việc nào: Worker = việc của mình, Leader = việc của team, Manager = tất cả
            if current_role == "Worker":
                upd_df = df
            elif current_role in LEADER_ROLES:
                upd_df = df[df['_leader_id'] == my_id]
            else:
                upd_df = df

            if upd_df.empty:
                st.info("Bạn chưa có công việc nào để cập nhật tiến độ.")
            else:
                options_tasks = [f"{row['_id']} | {row['Task ID']} - {row['Task Name']} (Hiện tại: {row['Progress (%)']}%)" for _, row in upd_df.iterrows()]
                selected_update_task = st.selectbox("Chọn công việc cần cập nhật tiến độ:", options_tasks)
                selected_task_id = int(selected_update_task.split(" | ")[0])
                
                curr_task = cursor.execute("SELECT progress, remark FROM tasks WHERE id = ?", (selected_task_id,)).fetchone()
                
                with st.form("quick_update_progress_form"):
                    u_col1, u_col2 = st.columns([1, 2])
                    with u_col1:
                        new_progress = st.number_input("Mức Tiến Độ Mới (%)", min_value=0, max_value=100, value=int(curr_task[0] or 0), step=5)
                    with u_col2:
                        new_remark = st.text_input("Ghi Chú Thi Công (Remark):", value=curr_task[1] if curr_task[1] else "")
                    
                    btn_update_p = st.form_submit_button("🚀 CẬP NHẬT TIẾN ĐỘ")
                    if btn_update_p:
                        cursor.execute("UPDATE tasks SET progress = ?, remark = ? WHERE id = ?", (new_progress, new_remark.strip(), selected_task_id))
                        conn.commit()
                        st.success("Đã cập nhật tiến độ công việc thành công!")
                        st.rerun()

    # 2. QUẢN LÝ DANH MỤC
    elif menu == "⚙️ Quản Lý Danh Mục" and current_role in ["Foreman", "WOS Manager", "Admin"]:
        st.markdown("<div class='big-table-title'>⚙️ Quản Lý Danh Mục Workshop / Cost Code</div>", unsafe_allow_html=True)
        
        with st.form("add_cost_code_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                ws_id = st.text_input("WS Cost Code (Ví dụ: EW): *")
            with col2:
                ws_name = st.text_input("Tên xưởng / Workshop Name: *")
            
            ws_desc = st.text_input("Mô tả chi tiết (Tùy chọn):")
            submit_cost_code = st.form_submit_button("✨ THÊM WORKSHOP MỚI")
            
            if submit_cost_code:
                if not ws_id.strip() or not ws_name.strip():
                    st.error("Vui lòng điền đầy đủ WS Cost Code và Tên Workshop!")
                else:
                    code_clean = ws_id.strip()
                    name_clean = ws_name.strip()
                    desc_clean = ws_desc.strip()
                    existing_ws = cursor.execute("SELECT is_deleted FROM custom_cost_codes WHERE code = ?", (code_clean,)).fetchone()
                    if existing_ws and existing_ws[0] == 0:
                        st.error(f"WS Cost Code **{code_clean}** đã tồn tại!")
                    elif existing_ws:
                        st.error(f"WS Cost Code **{code_clean}** đang nằm trong Thùng Rác. Hãy khôi phục thay vì tạo mới.")
                    else:
                        cursor.execute("INSERT INTO custom_cost_codes (code, name, description, is_deleted) VALUES (?, ?, ?, 0)", 
                                       (code_clean, name_clean, desc_clean))
                        conn.commit()
                        st.success(f"Đã thêm thành công: **{code_clean} - {name_clean}**")
                        st.rerun()

        st.markdown("---")
        st.markdown("### 📋 Danh Sách Workshop Đang Hoạt Động")
        df_ws = pd.read_sql_query("SELECT id, code AS 'WS Cost Code', name AS 'Workshop Name', description AS 'Mô Tả' FROM custom_cost_codes WHERE is_deleted = 0", conn)
        if df_ws.empty:
            st.info("Chưa có Workshop nào trong danh mục.")
        else:
            st.dataframe(df_ws.drop(columns=['id']), use_container_width=True)
            
            st.markdown("#### 🗑️ Xóa Tạm Workshop")
            ws_del_options = [f"{row['id']} | {row['WS Cost Code']} - {row['Workshop Name']}" for _, row in df_ws.iterrows()]
            ws_del_selected = st.selectbox("Chọn Workshop cần chuyển vào Thùng Rác:", ws_del_options)
            ws_del_id = int(ws_del_selected.split(" | ")[0])
            
            if st.button("🗑️ Chuyển Workshop Vào Thùng Rác", type="secondary", key="btn_del_ws"):
                cursor.execute("UPDATE custom_cost_codes SET is_deleted = 1 WHERE id = ?", (ws_del_id,))
                conn.commit()
                st.success("Đã chuyển Workshop vào Thùng Rác thành công!")
                st.rerun()

    # 3. THÊM CÔNG VIỆC MỚI
    elif menu == "➕ Thêm Công Việc" and current_role in ["Team Leader", "Foreman", "WOS Manager", "Admin"]:
        st.markdown("<div class='big-table-title'>➕ Thêm Công Việc Mới</div>", unsafe_allow_html=True)
        
        cost_codes_df = pd.read_sql_query("SELECT code, name FROM custom_cost_codes WHERE is_deleted = 0", conn)
        
        if cost_codes_df.empty:
            st.warning("⚠️ CHƯA CÓ DỮ LIỆU WORKSHOP: Vui lòng liên hệ Foreman/WOS Manager để tạo WS Cost Code trước khi thêm công việc!")
        else:
            options = [f"{row['code']} - {row['name']}" if row['name'] else row['code'] for _, row in cost_codes_df.iterrows()]
            
            with st.form("add_task_form_full", clear_on_submit=True):
                c1, c2, c3 = st.columns([1, 2, 1])
                with c1:
                    task_id = st.text_input("Task ID *")
                with c2:
                    task_name_input = st.text_input("Task Name *")
                with c3:
                    selected_cost_code = st.selectbox("WS Cost Code *", options)

                description = st.text_area("Description (Mô tả công việc):", height=80)

                c4, c5, c6 = st.columns(3)
                with c4:
                    initial_by = st.text_input("Initial By (Người khởi tạo):", value=user_data['fullname'])
                with c5:
                    initial_date = st.date_input("Initial Date (Ngày tạo):", value=date.today())
                with c6:
                    in_charge_by = st.text_input("In Charge By (Người phụ trách):")

                c7, c8, c9, c10 = st.columns(4)
                with c7:
                    block = st.text_input("Block (Ví dụ: 170150):")
                with c8:
                    area = st.text_input("Area:")
                with c9:
                    deck = st.text_input("Deck:")
                with c10:
                    frame = st.text_input("Frame:")

                c11, c12, c13 = st.columns(3)
                with c11:
                    plan_start = st.date_input("Plan Start Date:", value=date.today())
                with c12:
                    plan_finish = st.date_input("Plan Finish Date:", value=date.today())
                with c13:
                    progress_val = st.number_input("Progress (%)", min_value=0, max_value=100, value=0, step=5)

                remark = st.text_input("Remark (Ghi chú):")

                # Giao việc ngay khi tạo
                new_task_leader_id = None
                if current_role in LEADER_ROLES:
                    new_task_leader_id = user_data['id']
                    st.caption("📌 Công việc này sẽ thuộc team của bạn. Vào 📋 Giao Việc để giao cho Worker.")
                else:
                    leaders_df_add = pd.read_sql_query(
                        "SELECT id, fullname, role, workshop FROM users WHERE is_deleted = 0 AND role IN ('Team Leader', 'Foreman') ORDER BY fullname", conn)
                    leader_opts_add = {None: "— Chưa giao —"}
                    for _, r in leaders_df_add.iterrows():
                        leader_opts_add[int(r['id'])] = f"{r['fullname']} ({r['role']}{', ' + r['workshop'] if r['workshop'] else ''})"
                    new_task_leader_id = st.selectbox("Giao cho Team Leader / Foreman:", list(leader_opts_add.keys()),
                                                      format_func=lambda k: leader_opts_add[k])

                st.markdown("<br>", unsafe_allow_html=True)
                submitted = st.form_submit_button("💾 LƯU CÔNG VIỆC MỚI")
                
                if submitted:
                    if not task_id.strip() or not task_name_input.strip():
                        st.error("Vui lòng điền đầy đủ thông tin bắt buộc: Task ID và Task Name!")
                    elif plan_finish < plan_start:
                        st.error("Plan Finish Date không được trước Plan Start Date!")
                    elif cursor.execute("SELECT 1 FROM tasks WHERE task_id = ?", (task_id.strip(),)).fetchone():
                        st.error(f"Task ID **{task_id.strip()}** đã tồn tại (có thể đang trong Thùng Rác). Vui lòng dùng ID khác!")
                    else:
                        ws_code_only = selected_cost_code.split(" - ")[0]
                        cursor.execute("""
                            INSERT INTO tasks (
                                task_id, task_name, task_cost_code, description,
                                initial_by, initial_date, block, area, deck, frame,
                                in_charge_by, plan_start_date, plan_finish_date,
                                progress, remark, assigned_leader_id, is_deleted
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0)
                        """, (
                            task_id.strip(), task_name_input.strip(), ws_code_only,
                            description.strip(), initial_by.strip(), str(initial_date),
                            block.strip(), area.strip(), deck.strip(), frame.strip(),
                            in_charge_by.strip(), str(plan_start), str(plan_finish),
                            int(progress_val), remark.strip(), new_task_leader_id
                        ))
                        conn.commit()
                        st.success(f"Đã lưu thành công công việc **{task_id} - {task_name_input}**!")

    # 3B. GIAO VIỆC
    #    - WOS Manager / Admin: giao công việc cho Team Leader / Foreman
    #    - Team Leader / Foreman: giao công việc của team mình cho Worker trong team
    elif menu == "📋 Giao Việc" and current_role in ["Team Leader", "Foreman", "WOS Manager", "Admin"]:
        st.markdown("<div class='big-table-title'>📋 Giao Việc</div>", unsafe_allow_html=True)

        if is_manager_up:
            st.info("👑 Chọn công việc và giao cho một **Team Leader** hoặc **Foreman**. Họ sẽ giao tiếp cho Worker trong team.")
            tasks_df = pd.read_sql_query("""
                SELECT t.id, t.task_id, t.task_name, t.task_cost_code, t.assigned_leader_id, l.fullname AS leader_name
                FROM tasks t LEFT JOIN users l ON l.id = t.assigned_leader_id
                WHERE t.is_deleted = 0 ORDER BY t.id DESC
            """, conn)
            leaders_df = pd.read_sql_query(
                "SELECT id, fullname, role, workshop FROM users WHERE is_deleted = 0 AND role IN ('Team Leader', 'Foreman') ORDER BY fullname", conn)

            if tasks_df.empty:
                st.info("Chưa có công việc nào. Vào ➕ Thêm Công Việc để tạo.")
            elif leaders_df.empty:
                st.warning("Chưa có Team Leader / Foreman nào. Vào 👥 Quản Lý Phân Quyền để cấp role trước.")
            else:
                show_unassigned = st.toggle("Chỉ hiện công việc chưa giao", value=False)
                if show_unassigned:
                    tasks_df = tasks_df[tasks_df['assigned_leader_id'].isna()]
                if tasks_df.empty:
                    st.success("Tất cả công việc đã được giao!")
                else:
                    task_opts = {int(r['id']): f"{r['task_id']} - {r['task_name']} ({r['task_cost_code']}) → "
                                               f"{r['leader_name'] if r['leader_name'] else 'Chưa giao'}"
                                 for _, r in tasks_df.iterrows()}
                    sel_task = st.selectbox("Chọn công việc:", list(task_opts.keys()), format_func=lambda k: task_opts[k])

                    leader_opts = {None: "— Chưa giao —"}
                    for _, r in leaders_df.iterrows():
                        leader_opts[int(r['id'])] = f"{r['fullname']} ({r['role']}{', ' + r['workshop'] if r['workshop'] else ''})"
                    cur_leader = tasks_df.loc[tasks_df['id'] == sel_task, 'assigned_leader_id'].iloc[0]
                    cur_leader = None if pd.isna(cur_leader) else int(cur_leader)
                    keys = list(leader_opts.keys())
                    sel_leader = st.selectbox("Giao cho Team Leader / Foreman:", keys,
                                              index=keys.index(cur_leader) if cur_leader in keys else 0,
                                              format_func=lambda k: leader_opts[k])

                    if st.button("💾 LƯU GIAO VIỆC", type="primary", key="btn_assign_leader"):
                        if sel_leader != cur_leader:
                            # Đổi người phụ trách thì bỏ Worker cũ (vì Worker thuộc team cũ)
                            cursor.execute("UPDATE tasks SET assigned_leader_id = ?, assigned_worker_id = NULL WHERE id = ?",
                                           (sel_leader, sel_task))
                            conn.commit()
                        st.success(f"Đã giao công việc cho **{leader_opts[sel_leader]}**!")
                        st.rerun()

        else:
            my_id = user_data['id']
            team_df = pd.read_sql_query(
                "SELECT id, username, fullname FROM users WHERE is_deleted = 0 AND role = 'Worker' AND leader_id = ? ORDER BY fullname",
                conn, params=(my_id,))

            st.markdown("### 👷 Team Của Tôi")
            if team_df.empty:
                st.info("Team của bạn chưa có Worker nào. Nhờ WOS Manager thêm Worker vào team ở mục 👥 Quản Lý Phân Quyền.")
            else:
                st.dataframe(team_df.rename(columns={'username': 'Username', 'fullname': 'Họ và Tên'}).drop(columns=['id']),
                             use_container_width=True)

            st.markdown("---")
            st.markdown("### 📌 Giao Việc Cho Worker")
            my_tasks = pd.read_sql_query("""
                SELECT t.id, t.task_id, t.task_name, t.progress, t.assigned_worker_id, w.fullname AS worker_name
                FROM tasks t LEFT JOIN users w ON w.id = t.assigned_worker_id
                WHERE t.is_deleted = 0 AND t.assigned_leader_id = ? ORDER BY t.id DESC
            """, conn, params=(my_id,))

            if my_tasks.empty:
                st.info("Bạn chưa được giao công việc nào.")
            elif team_df.empty:
                st.warning("Cần có Worker trong team trước khi giao việc.")
            else:
                task_opts = {int(r['id']): f"{r['task_id']} - {r['task_name']} ({r['progress']}%) → "
                                           f"{r['worker_name'] if r['worker_name'] else 'Chưa giao'}"
                             for _, r in my_tasks.iterrows()}
                sel_task = st.selectbox("Chọn công việc:", list(task_opts.keys()), format_func=lambda k: task_opts[k])

                worker_opts = {None: "— Chưa giao —"}
                for _, r in team_df.iterrows():
                    worker_opts[int(r['id'])] = f"{r['fullname']} (@{r['username']})"
                cur_worker = my_tasks.loc[my_tasks['id'] == sel_task, 'assigned_worker_id'].iloc[0]
                cur_worker = None if pd.isna(cur_worker) else int(cur_worker)
                keys = list(worker_opts.keys())
                sel_worker = st.selectbox("Giao cho Worker:", keys,
                                          index=keys.index(cur_worker) if cur_worker in keys else 0,
                                          format_func=lambda k: worker_opts[k])

                if st.button("💾 LƯU GIAO VIỆC", type="primary", key="btn_assign_worker"):
                    cursor.execute("UPDATE tasks SET assigned_worker_id = ? WHERE id = ? AND assigned_leader_id = ?",
                                   (sel_worker, sel_task, my_id))
                    conn.commit()
                    st.success(f"Đã giao công việc cho **{worker_opts[sel_worker]}**!")
                    st.rerun()

    # 4. CHỈNH SỬA / XÓA TẠM
    elif menu == "✏️ Chỉnh Sửa/Xóa" and current_role in ["Foreman", "WOS Manager", "Admin"]:
        st.markdown("<div class='big-table-title'>✏️ Chỉnh Sửa & Xóa Quản Lý</div>", unsafe_allow_html=True)
        
        btn_col1, btn_col2, btn_col_space = st.columns([1.5, 2, 2.5])
        is_edit_task = st.session_state["edit_sub_tab"] == "task"
        
        with btn_col1:
            if st.button("🧰 Xóa Tạm Công Việc", type="primary" if is_edit_task else "secondary", key="btn_sub_edit_task"):
                st.session_state["edit_sub_tab"] = "task"
                st.rerun()
                
        with btn_col2:
            if st.button("👤 Xóa Tạm Tài Khoản Người Dùng", type="primary" if not is_edit_task else "secondary", key="btn_sub_edit_user"):
                st.session_state["edit_sub_tab"] = "user"
                st.rerun()

        st.markdown("---")

        if st.session_state["edit_sub_tab"] == "task":
            tasks_df = pd.read_sql_query("SELECT id, task_id, task_name FROM tasks WHERE is_deleted = 0", conn)
            if tasks_df.empty:
                st.info("Hiện không có công việc nào để chỉnh sửa hoặc xóa.")
            else:
                task_list = [f"{row['id']} | {row['task_id']} - {row['task_name']}" for _, row in tasks_df.iterrows()]
                selected_task_str = st.selectbox("Chọn công việc cần chuyển vào Thùng Rác:", task_list)
                selected_id = int(selected_task_str.split(" | ")[0])
                
                if st.button("🗑️ Chuyển Công Việc Vào Thùng Rác", type="secondary", key="btn_soft_delete_task"):
                    cursor.execute("UPDATE tasks SET is_deleted = 1 WHERE id = ?", (selected_id,))
                    conn.commit()
                    st.success("Đã chuyển công việc vào Thùng Rác thành công!")
                    st.rerun()

        else:
            users_df = pd.read_sql_query("SELECT id, username, fullname, role FROM users WHERE is_deleted = 0", conn)
            users_df = users_df[users_df['id'] != user_data['id']]
            users_df = users_df[users_df['role'] != "Admin"]
            if current_role == "WOS Manager":
                # WOS Manager không được khóa WOS Manager khác
                users_df = users_df[users_df['role'] != "WOS Manager"]
            elif current_role != "Admin":
                # Foreman chỉ được khóa Worker, Team Leader và tài khoản đang chờ duyệt
                users_df = users_df[users_df['role'].isin(["Worker", "Team Leader", "Pending"])]
            
            if users_df.empty:
                st.info("Không có tài khoản khác khả dụng để xóa.")
            else:
                user_list = [f"{row['id']} | @{row['username']} - {row['fullname']} ({row['role']})" for _, row in users_df.iterrows()]
                selected_user_str = st.selectbox("Chọn tài khoản muốn khóa/xóa tạm:", user_list)
                selected_user_id = int(selected_user_str.split(" | ")[0])
                
                if st.button("🗑️ Khóa/Xóa Tạm Tài Khoản Này", type="secondary", key="btn_soft_delete_user"):
                    cursor.execute("UPDATE users SET is_deleted = 1 WHERE id = ?", (selected_user_id,))
                    conn.commit()
                    delete_user_sessions(selected_user_id)
                    st.success("Đã khóa/chuyển tài khoản vào Thùng Rác thành công!")
                    st.rerun()

    # 5. QUẢN LÝ PHÂN QUYỀN
    #    - Admin: CHỈ cấp role WOS Manager và chọn workshop cho Manager
    #    - WOS Manager: cấp Worker / Team Leader / Foreman trong workshop của mình
    elif menu == "👥 Quản Lý Phân Quyền" and is_manager_up:
        st.markdown("<div class='big-table-title'>👥 Quản Lý & Cấp Quyền Tài Khoản (Role List)</div>", unsafe_allow_html=True)

        ws_df = pd.read_sql_query("SELECT code, name FROM custom_cost_codes WHERE is_deleted = 0 ORDER BY code", conn)
        ws_label = {row['code']: f"{row['code']} - {row['name']}" for _, row in ws_df.iterrows()}

        all_users = pd.read_sql_query("""
            SELECT u.id, u.username, u.fullname, u.role, u.workshop, u.leader_id, l.fullname AS leader_name
            FROM users u LEFT JOIN users l ON l.id = u.leader_id
            WHERE u.is_deleted = 0
        """, conn)
        all_users = all_users[(all_users['id'] != user_data['id']) & (all_users['role'] != "Admin")]

        if is_admin:
            visible_users = all_users
            st.info("🛡️ Admin chỉ cấp quyền **WOS Manager** và chọn **Workshop** mà Manager đó phụ trách. "
                    "Các role Worker / Team Leader / Foreman do WOS Manager cấp.")
        else:
            st.info("👑 Bạn có thể cấp **Worker / Team Leader / Foreman**, chọn **Workshop**, "
                    "và xếp Worker vào **team** của một Team Leader / Foreman.")
            visible_users = all_users[all_users['role'] != "WOS Manager"]

        show_df = visible_users.copy()
        show_df['workshop'] = show_df['workshop'].map(lambda c: ws_label.get(c, c) if c else "—")
        show_df['leader_name'] = show_df['leader_name'].fillna("—")
        show_df = show_df.rename(columns={'username': 'Username', 'fullname': 'Họ và Tên',
                                          'role': 'Vai Trò (Role)', 'workshop': 'Workshop',
                                          'leader_name': 'Team của'})
        st.dataframe(show_df.drop(columns=['id', 'leader_id']), use_container_width=True)

        st.markdown("---")
        st.markdown("### 🔄 Thay Đổi Quyền Hạn Cho Tài Khoản")

        if visible_users.empty:
            st.info("Không có tài khoản nào để cấp quyền.")
        else:
            user_roles_list = [f"{row['id']} | @{row['username']} - {row['fullname']} (Hiện tại: {row['role']})"
                               for _, row in visible_users.iterrows()]
            target_role_user = st.selectbox("Chọn tài khoản cần chuyển đổi Role:", user_roles_list)
            target_user_id = int(target_role_user.split(" | ")[0])

            if is_admin:
                if ws_df.empty:
                    st.warning("⚠️ Chưa có Workshop nào. Vào ⚙️ Quản Lý Danh Mục để thêm trước.")
                else:
                    action = st.radio("Chọn thao tác:", ["👑 Cấp quyền WOS Manager", "⛔ Thu hồi quyền (về Pending)"], horizontal=True)
                    chosen_ws = None
                    if action.startswith("👑"):
                        chosen_ws = st.selectbox("Workshop mà Manager này phụ trách:", list(ws_label.keys()),
                                                 format_func=lambda c: ws_label[c])
                    if st.button("💾 LƯU THAY ĐỔI", type="primary", key="btn_save_role_admin"):
                        if chosen_ws:
                            cursor.execute("UPDATE users SET role = 'WOS Manager', workshop = ? WHERE id = ?", (chosen_ws, target_user_id))
                            msg = f"Đã cấp **WOS Manager** cho workshop **{ws_label[chosen_ws]}**!"
                        else:
                            cursor.execute("UPDATE users SET role = 'Pending' WHERE id = ?", (target_user_id,))
                            msg = "Đã thu hồi quyền, tài khoản trở về trạng thái Pending."
                        conn.commit()
                        delete_user_sessions(target_user_id)
                        st.success(msg)
                        st.rerun()
            else:
                target_row = visible_users[visible_users['id'] == target_user_id].iloc[0]
                role_choices = ["Worker", "Team Leader", "Foreman", "Pending"]
                cur_role = target_row['role'] if target_row['role'] in role_choices else "Worker"
                new_role = st.radio("Chọn Role Mới:", role_choices, index=role_choices.index(cur_role), horizontal=True)

                ws_keys = list(ws_label.keys())
                default_ws = target_row['workshop'] if target_row['workshop'] in ws_keys else user_data.get("workshop")
                new_ws = st.selectbox("Workshop:", ws_keys,
                                      index=ws_keys.index(default_ws) if default_ws in ws_keys else 0,
                                      format_func=lambda c: ws_label[c]) if ws_keys else None

                new_leader = None
                if new_role == "Worker":
                    leaders_in_ws = all_users[(all_users['role'].isin(LEADER_ROLES)) & (all_users['workshop'] == new_ws)]
                    leader_opts = {None: "— Chưa xếp team —"}
                    for _, r in leaders_in_ws.iterrows():
                        leader_opts[int(r['id'])] = f"{r['fullname']} ({r['role']})"
                    cur_ld = None if pd.isna(target_row['leader_id']) else int(target_row['leader_id'])
                    ld_keys = list(leader_opts.keys())
                    new_leader = st.selectbox("Thuộc team của (Team Leader / Foreman):", ld_keys,
                                              index=ld_keys.index(cur_ld) if cur_ld in ld_keys else 0,
                                              format_func=lambda k: leader_opts[k])
                    if len(leader_opts) == 1:
                        st.caption("Workshop này chưa có Team Leader / Foreman nào.")

                if st.button("💾 LƯU THAY ĐỔI ROLE", type="primary", key="btn_save_role"):
                    cursor.execute("UPDATE users SET role = ?, workshop = ?, leader_id = ? WHERE id = ?",
                                   (new_role, new_ws, new_leader, target_user_id))
                    if new_role not in LEADER_ROLES:
                        # Không còn là Leader: giải tán team và trả công việc về trạng thái chưa giao
                        cursor.execute("UPDATE users SET leader_id = NULL WHERE leader_id = ?", (target_user_id,))
                        cursor.execute("UPDATE tasks SET assigned_leader_id = NULL, assigned_worker_id = NULL WHERE assigned_leader_id = ?",
                                       (target_user_id,))
                    if new_role != "Worker":
                        cursor.execute("UPDATE tasks SET assigned_worker_id = NULL WHERE assigned_worker_id = ?", (target_user_id,))
                    else:
                        # Worker đổi team: bỏ các việc không thuộc team mới
                        cursor.execute("""UPDATE tasks SET assigned_worker_id = NULL
                                          WHERE assigned_worker_id = ? AND (assigned_leader_id IS NULL OR assigned_leader_id != ?)""",
                                       (target_user_id, new_leader if new_leader else -1))
                    conn.commit()
                    st.success(f"Đã cập nhật: **{new_role}** – workshop **{ws_label.get(new_ws, '')}**!")
                    st.rerun()

    # 6. THÙNG RÁC TỔNG HỢP (CHỈ WOS MANAGER)
    elif menu == "🗑️ Thùng Rác" and is_manager_up:
        st.markdown("<div class='big-table-title'>🗑️ Thùng Rác & Khôi Phục Tổng Hợp</div>", unsafe_allow_html=True)
        
        t_col1, t_col2, t_col3, t_space = st.columns([1.5, 1.5, 1.5, 1.5])
        
        is_t_task = st.session_state["trash_sub_tab"] == "task"
        is_t_ws = st.session_state["trash_sub_tab"] == "ws"
        is_t_user = st.session_state["trash_sub_tab"] == "user"
        
        with t_col1:
            if st.button("🧰 Thùng Rác Công Việc", type="primary" if is_t_task else "secondary", key="btn_t_task"):
                st.session_state["trash_sub_tab"] = "task"
                st.rerun()
                
        with t_col2:
            if st.button("⚙️ Thùng Rác Workshop", type="primary" if is_t_ws else "secondary", key="btn_t_ws"):
                st.session_state["trash_sub_tab"] = "ws"
                st.rerun()

        with t_col3:
            if st.button("👤 Thùng Rác Tài Khoản", type="primary" if is_t_user else "secondary", key="btn_t_user"):
                st.session_state["trash_sub_tab"] = "user"
                st.rerun()

        st.markdown("---")

        if st.session_state["trash_sub_tab"] == "task":
            deleted_tasks = pd.read_sql_query("SELECT id, task_id, task_name, task_cost_code, initial_by FROM tasks WHERE is_deleted = 1", conn)
            if deleted_tasks.empty:
                st.info("Thùng rác công việc đang trống.")
            else:
                st.dataframe(deleted_tasks, use_container_width=True)
                task_del_options = [f"{row['id']} | {row['task_id']} - {row['task_name']}" for _, row in deleted_tasks.iterrows()]
                restore_task_target = st.selectbox("Chọn công việc để xử lý:", task_del_options, key="sb_res_task")
                res_task_id = int(restore_task_target.split(" | ")[0])
                
                col_r1, col_r2 = st.columns(2)
                with col_r1:
                    if st.button("♻️ KHÔI PHỤC CÔNG VIỆC", type="primary", key="btn_res_task"):
                        cursor.execute("UPDATE tasks SET is_deleted = 0 WHERE id = ?", (res_task_id,))
                        conn.commit()
                        st.success("Đã khôi phục công việc!")
                        st.rerun()
                with col_r2:
                    if st.button("💥 XÓA VĨNH VIỄN CÔNG VIỆC", type="secondary", key="btn_perm_del_task"):
                        cursor.execute("DELETE FROM tasks WHERE id = ?", (res_task_id,))
                        conn.commit()
                        st.warning("Đã xóa vĩnh viễn công việc!")
                        st.rerun()

        elif st.session_state["trash_sub_tab"] == "ws":
            deleted_ws = pd.read_sql_query("SELECT id, code AS 'WS Code', name AS 'Workshop Name' FROM custom_cost_codes WHERE is_deleted = 1", conn)
            if deleted_ws.empty:
                st.info("Thùng rác Workshop đang trống.")
            else:
                st.dataframe(deleted_ws, use_container_width=True)
                ws_res_options = [f"{row['id']} | {row['WS Code']} - {row['Workshop Name']}" for _, row in deleted_ws.iterrows()]
                restore_ws_target = st.selectbox("Chọn Workshop để xử lý:", ws_res_options, key="sb_res_ws")
                res_ws_id = int(restore_ws_target.split(" | ")[0])
                
                col_w1, col_w2 = st.columns(2)
                with col_w1:
                    if st.button("♻️ KHÔI PHỤC WORKSHOP", type="primary", key="btn_res_ws"):
                        cursor.execute("UPDATE custom_cost_codes SET is_deleted = 0 WHERE id = ?", (res_ws_id,))
                        conn.commit()
                        st.success("Đã khôi phục Workshop!")
                        st.rerun()
                with col_w2:
                    if st.button("💥 XÓA VĨNH VIỄN WORKSHOP", type="secondary", key="btn_perm_del_ws"):
                        cursor.execute("DELETE FROM custom_cost_codes WHERE id = ?", (res_ws_id,))
                        conn.commit()
                        st.warning("Đã xóa vĩnh viễn Workshop!")
                        st.rerun()

        else:
            deleted_users = pd.read_sql_query("SELECT id, username, fullname, role FROM users WHERE is_deleted = 1", conn)
            if deleted_users.empty:
                st.info("Thùng rác tài khoản đang trống.")
            else:
                st.dataframe(deleted_users, use_container_width=True)
                user_res_options = [f"{row['id']} | @{row['username']} - {row['fullname']} ({row['role']})" for _, row in deleted_users.iterrows()]
                restore_user_target = st.selectbox("Chọn tài khoản để xử lý:", user_res_options, key="sb_res_user")
                res_user_id = int(restore_user_target.split(" | ")[0])
                
                col_u1, col_u2 = st.columns(2)
                with col_u1:
                    if st.button("♻️ MỞ KHÓA / KHÔI PHỤC TÀI KHOẢN", type="primary", key="btn_res_user"):
                        cursor.execute("UPDATE users SET is_deleted = 0 WHERE id = ?", (res_user_id,))
                        conn.commit()
                        st.success("Đã khôi phục tài khoản người dùng!")
                        st.rerun()
                with col_u2:
                    if st.button("💥 XÓA VĨNH VIỄN TÀI KHOẢN", type="secondary", key="btn_perm_del_user"):
                        cursor.execute("DELETE FROM users WHERE id = ?", (res_user_id,))
                        conn.commit()
                        delete_user_sessions(res_user_id)
                        st.warning("Đã xóa vĩnh viễn tài khoản khỏi cơ sở dữ liệu!")
                        st.rerun()

    # 7. BÁO CÁO & THỐNG KÊ
    elif menu == "📊 Báo Cáo & Khai Báo":
        st.markdown("<div class='big-table-title'>📊 Báo Cáo & Thống Kê Tiến Độ</div>", unsafe_allow_html=True)
        
        df_all = pd.read_sql_query("SELECT task_id, task_name, task_cost_code, block, in_charge_by, progress FROM tasks WHERE is_deleted = 0", conn)
        
        if df_all.empty:
            st.info("Chưa có dữ liệu công việc để tạo báo cáo. Vui lòng thêm công việc trước!")
        else:
            df_all['progress'] = pd.to_numeric(df_all['progress'], errors='coerce').fillna(0)
            
            total_tasks = len(df_all)
            completed_tasks = len(df_all[df_all['progress'] == 100])
            in_progress_tasks = len(df_all[(df_all['progress'] > 0) & (df_all['progress'] < 100)])
            avg_progress = round(df_all['progress'].mean(), 1)
            
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Tổng Số Công Việc", f"{total_tasks}")
            m2.metric("Đã Hoàn Thành (100%)", f"{completed_tasks}", f"{(completed_tasks/total_tasks*100):.1f}%")
            m3.metric("Đang Thực Hiện", f"{in_progress_tasks}")
            m4.metric("Tiến Độ Trung Bình", f"{avg_progress}%")
            
            st.markdown("---")
            
            col_chart1, col_chart2 = st.columns(2)
            
            with col_chart1:
                st.markdown("### 📈 Phân Bố Tiến Độ Công Việc")
                progress_bins = pd.cut(df_all['progress'], bins=[-1, 0, 50, 99, 100], labels=['Chưa bắt đầu (0%)', 'Đang làm (1-50%)', 'Sắp xong (51-99%)', 'Hoàn thành (100%)'])
                progress_dist = progress_bins.value_counts().reset_index()
                progress_dist.columns = ['Trạng Thái', 'Số Lượng']
                
                chart = alt.Chart(progress_dist).mark_bar(color='#3b82f6').encode(
                    x=alt.X('Trạng Thái:N', axis=alt.Axis(labelAngle=0, labelFontSize=12, title="Trạng Thái")),
                    y=alt.Y('Số Lượng:Q', axis=alt.Axis(title="Số Lượng Công Việc", tickMinStep=1, format='d')),
                    tooltip=['Trạng Thái', 'Số Lượng']
                ).properties(height=350)
                
                st.altair_chart(chart, use_container_width=True)

            with col_chart2:
                st.markdown("### 🏭 Thống Kê Theo Workshop")
                ws_stats = df_all.groupby('task_cost_code').agg(
                    Tổng_CV=('task_id', 'count'),
                    Tiến_Độ_TB=('progress', 'mean')
                ).reset_index()
                ws_stats['Tiến_Độ_TB'] = ws_stats['Tiến_Độ_TB'].round(1)
                ws_stats.columns = ['WS Cost Code', 'Tổng Công Việc', 'Tiến Độ Trung Bình (%)']
                st.dataframe(ws_stats, use_container_width=True)

            st.markdown("---")
            st.markdown("### 📥 Tải Báo Cáo Dữ Liệu")
            
            csv_data = df_all.to_csv(index=False).encode('utf-8-sig')
            st.download_button(
                label="📥 Tải Báo Cáo Bảng Công Việc (File CSV/Excel)",
                data=csv_data,
                file_name=f"ShipControl_Report_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                mime="text/csv",
                type="primary"
            )

    # 8. ĐỔI MẬT KHẨU (MỌI ROLE)
    elif menu == "🔑 Đổi Mật Khẩu":
        st.markdown("<div class='big-table-title'>🔑 Đổi Mật Khẩu</div>", unsafe_allow_html=True)
        with st.form("change_password_form", clear_on_submit=True):
            old_pw = st.text_input("Mật khẩu hiện tại:", type="password")
            new_pw = st.text_input("Mật khẩu mới (ít nhất 8 ký tự):", type="password")
            new_pw2 = st.text_input("Nhập lại mật khẩu mới:", type="password")
            btn_change_pw = st.form_submit_button("💾 ĐỔI MẬT KHẨU")
            if btn_change_pw:
                row = cursor.execute("SELECT password FROM users WHERE id = ?", (user_data['id'],)).fetchone()
                if not row or not verify_password(old_pw, row[0]):
                    st.error("Mật khẩu hiện tại không đúng!")
                elif len(new_pw) < 8:
                    st.error("Mật khẩu mới phải có ít nhất 8 ký tự!")
                elif new_pw != new_pw2:
                    st.error("Mật khẩu xác nhận không trùng khớp!")
                elif new_pw == "admin123":
                    st.error("Không được dùng lại mật khẩu mặc định!")
                else:
                    cursor.execute("UPDATE users SET password = ? WHERE id = ?", (hash_password(new_pw), user_data['id']))
                    conn.commit()
                    # Đăng xuất mọi thiết bị khác
                    cursor.execute("DELETE FROM sessions WHERE user_id = ? AND token != ?",
                                   (user_data['id'], st.session_state.get("session_token", "")))
                    conn.commit()
                    st.success("✅ Đã đổi mật khẩu thành công! Các thiết bị khác đã bị đăng xuất.")