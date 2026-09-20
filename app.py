import streamlit as st
import pandas as pd
import sqlite3
import hashlib
from datetime import datetime

# 1. Cấu hình trang web
st.set_page_config(
    page_title="ShipControl - Quản Lý Công Việc Tàu",
    page_icon="🚢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- KHỞI TẠO STATE THEME, AUTH & MENU ---
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

# --- CÔNG TẮC CHUYỂN THEME TRÊN ĐỈNH SIDEBAR ---
st.sidebar.markdown("<div style='padding-top: 10px;'></div>", unsafe_allow_html=True)
dark_mode_on = st.sidebar.toggle("🌙 Chế độ Tối (Dark)", value=(st.session_state["theme_mode"] == "Dark"), key="dark_toggle")
st.session_state["theme_mode"] = "Dark" if dark_mode_on else "Light"

is_dark = st.session_state["theme_mode"] == "Dark"

main_bg = "#0f172a" if is_dark else "#f8f9fa"
text_color = "#f8fafc" if is_dark else "#0f172a"
input_bg = "#1e293b" if is_dark else "#ffffff"
input_text = "#ffffff" if is_dark else "#0f172a"
border_color = "#334155" if is_dark else "#cbd5e1"

st.markdown(f"""
    <style>
    /* Nền ứng dụng chính */
    .stApp, .main {{
        background-color: {main_bg} !important;
        color: {text_color} !important;
    }}
    
    /* Sidebar */
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

    /* ======================================================== */
    /* 🔥 TẠO NÚT BẤM HÌNH CHỮ NHẬT TO CẢ 2 NƠI (SIDEBAR & AUTH) */
    /* ======================================================== */
    div.stButton > button {{
        width: 100% !important;
        min-height: 55px !important;
        border-radius: 10px !important;
        transition: all 0.2s ease !important;
        margin-bottom: 8px !important;
    }}

    /* NÚT PRIMARY -> XANH LÁ, CHỮ TRẮNG */
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

    /* NÚT SECONDARY -> XÁM SÁNG, CHỮ ĐEN TUYỀN */
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

    /* ======================================================== */
    /* 🔥 CSS PHÓNG TO BẢNG DỮ LIỆU (ST.DATAFRAME) & TIÊU ĐỀ    */
    /* ======================================================== */
    .big-table-title {{
        font-size: 1.8rem !important;
        font-weight: 800 !important;
        color: {text_color} !important;
        margin-top: 10px !important;
        margin-bottom: 15px !important;
    }}

    /* Chữ tiêu đề cột của bảng */
    div[data-testid="stDataFrame"] th, 
    div[data-testid="stTable"] th {{
        font-size: 1.15rem !important;
        font-weight: 800 !important;
        padding: 12px 8px !important;
    }}

    /* Chữ nội dung trong dòng của bảng */
    div[data-testid="stDataFrame"] td, 
    div[data-testid="stTable"] td,
    div[data-testid="stDataFrame"] [role="gridcell"] {{
        font-size: 1.1rem !important;
        font-weight: 600 !important;
        padding: 10px 8px !important;
    }}

    /* Ô NHẬP LIỆU */
    input, textarea, select, div[data-baseweb="select"] > div {{
        background-color: {input_bg} !important;
        color: {input_text} !important;
        border: 1px solid {border_color} !important;
        border-radius: 8px !important;
        font-size: 1.1rem !important;
    }}

    .stTextInput label, .stTextArea label, .stSelectbox label {{
        color: {text_color} !important;
        font-weight: 700 !important;
        font-size: 1.1rem !important;
    }}

    /* NÚT SUBMIT FORM */
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

# KẾT NỐI CSDL SQLITE
conn = sqlite3.connect("ship_control.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        fullname TEXT
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
        progress INTEGER,
        remark TEXT,
        image_path TEXT,
        is_deleted INTEGER DEFAULT 0
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS custom_cost_codes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        code TEXT UNIQUE,
        is_deleted INTEGER DEFAULT 0
    )
''')
conn.commit()

def hash_password(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

# --- TIÊU ĐỀ TRANG ---
st.markdown("<div class='main-title'>🚢 SHIPCONTROL - QUẢN LÝ CÔNG VIỆC TÀU</div>", unsafe_allow_html=True)

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
                        hashed_p = hash_password(login_pass)
                        user = cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (login_user, hashed_p)).fetchone()
                        if user:
                            st.session_state["logged_in"] = True
                            st.session_state["user_info"] = {"username": user[1], "fullname": user[3]}
                            st.success(f"Chào mừng {user[3]} đã quay trở lại!")
                            st.rerun()
                        else:
                            st.error("Sai tên tài khoản hoặc mật khẩu!")

        else:
            with st.form("form_register_system"):
                reg_fullname = st.text_input("Họ và Tên:")
                reg_user = st.text_input("Tên đăng nhập mới (Username):")
                reg_pass = st.text_input("Mật khẩu mới:", type="password")
                reg_confirm = st.text_input("Xác nhận lại mật khẩu:", type="password")
                btn_register = st.form_submit_button("✨ ĐĂNG KÝ NGAY")

                if btn_register:
                    if not reg_fullname or not reg_user or not reg_pass:
                        st.error("Vui lòng điền đầy đủ các thông tin!")
                    elif reg_pass != reg_confirm:
                        st.error("Mật khẩu xác nhận không trùng khớp!")
                    else:
                        try:
                            cursor.execute("INSERT INTO users (username, password, fullname) VALUES (?, ?, ?)", 
                                           (reg_user, hash_password(reg_pass), reg_fullname))
                            conn.commit()
                            st.success("Đăng ký tài khoản thành công! Bạn có thể chọn Tab Đăng Nhập phía trên.")
                        except sqlite3.IntegrityError:
                            st.error("Tên đăng nhập này đã tồn tại, vui lòng chọn tên khác!")

# ==========================================
# 🚢 GIAO DIỆN CHÍNH
# ==========================================
else:
    st.sidebar.markdown("<div class='sidebar-header'>☸️ Control Menu</div>", unsafe_allow_html=True)

    menu_options = [
        "🧰 Bảng Công Việc", 
        "⚙️ Quản Lý Danh Mục",
        "➕ Thêm Công Việc", 
        "✏️ Chỉnh Sửa/Xóa",
        "🗑️ Thùng Rác",
        "📊 Báo Cáo & Khai Báo"
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
    user_data = st.session_state["user_info"]
    
    st.sidebar.markdown(f"""
        <div class='user-card'>
            👋 <b>WELCOME</b><br>
            <span style='font-size: 1.1rem; font-weight: 800;'>{user_data['fullname']}</span><br>
            <small>@{user_data['username']}</small>
        </div>
    """, unsafe_allow_html=True)

    st.sidebar.markdown("<div class='made-by-minh'>Made By Minh</div>", unsafe_allow_html=True)

    if st.sidebar.button("🚪 Đăng Xuất", type="secondary", key="btn_logout_bottom"):
        st.session_state["logged_in"] = False
        st.session_state["user_info"] = None
        st.rerun()

    if menu == "🧰 Bảng Công Việc":
        # TIÊU ĐỀ ĐƯỢC LÀM TO NỔI BẬT
        st.markdown("<div class='big-table-title'>📋 Bảng Quản Lý Tiến Độ Công Việc</div>", unsafe_allow_html=True)
        
        df = pd.read_sql_query("SELECT task_id, task_name, task_cost_code, block, description, initial_by, initial_date, area, deck, frame, in_charge_by, plan_start_date, plan_finish_date, progress, remark FROM tasks WHERE is_deleted = 0", conn)
        
        if df.empty:
            st.info("Chưa có dữ liệu công việc nào trong hệ thống.")
        else:
            # BẢNG ĐƯỢC ÉP KÍCH THƯỚC CHỮ TO RÕ NỔI BẬT DƯỚI CSS
            st.dataframe(df, use_container_width=True, height=450)

    elif menu == "⚙️ Quản Lý Danh Mục":
        st.markdown("<div class='big-table-title'>🏷️ Quản Lý Danh Mục Mã Chi Phí (Cost Code)</div>", unsafe_allow_html=True)
        with st.form("add_cost_code_form", clear_on_submit=True):
            new_cost_code_input = st.text_input("Nhập Cost Code mới:")
            submit_cost_code = st.form_submit_button("✨ THÊM COST CODE MỚI")
            if submit_cost_code and new_cost_code_input.strip():
                code_clean = new_cost_code_input.strip()
                cursor.execute("INSERT OR REPLACE INTO custom_cost_codes (code, is_deleted) VALUES (?, 0)", (code_clean,))
                conn.commit()
                st.success(f"Đã thêm Cost Code: '{code_clean}'!")
                st.rerun()

    elif menu == "➕ Thêm Công Việc":
        st.markdown("<div class='big-table-title'>➕ Thêm Công Việc Mới</div>", unsafe_allow_html=True)
        cost_code_list = pd.read_sql_query("SELECT code FROM custom_cost_codes WHERE is_deleted = 0", conn)['code'].tolist()
        if not cost_code_list:
            st.warning("⚠️ Vui lòng vào 'Quản Lý Danh Mục' để tạo Cost Code trước.")
        else:
            with st.form("add_task_form", clear_on_submit=True):
                task_id = st.text_input("Task ID *")
                task_name_input = st.text_input("Task Name *")
                selected_cost_code = st.selectbox("Chọn Cost Code *", cost_code_list)
                submitted = st.form_submit_button("💾 LƯU CÔNG VIỆC MỚI")
                if submitted and task_id and task_name_input:
                    cursor.execute("INSERT INTO tasks (task_id, task_name, task_cost_code, is_deleted) VALUES (?, ?, ?, 0)", (task_id, task_name_input, selected_cost_code))
                    conn.commit()
                    st.success("Đã thêm thành công!")