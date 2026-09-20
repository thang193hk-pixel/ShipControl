import streamlit as st
import pandas as pd
import sqlite3
import hashlib
from datetime import datetime, date
import altair as alt

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

    /* NÚT BẤM HÌNH CHỮ NHẬT TO CẢ 2 NƠI */
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

    /* CSS PHÓNG TO BẢNG DỮ LIỆU */
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

    /* SỬA MÀU THÔNG BÁO CẢNH BÁO */
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

    /* Ô NHẬP LIỆU */
    input, textarea, select, div[data-baseweb="select"] > div {{
        background-color: {input_bg} !important;
        color: {input_text} !important;
        border: 1px solid {border_color} !important;
        border-radius: 8px !important;
        font-size: 1.1rem !important;
    }}

    .stTextInput label, .stTextArea label, .stSelectbox label, .stDateInput label, .stSlider label {{
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

# 2. KẾT NỐI VÀ CẤU HÌNH CƠ SỞ DỮ LIỆU SQLITE
conn = sqlite3.connect("ship_control.db", check_same_thread=False)
cursor = conn.cursor()

# Tạo bảng người dùng nếu chưa có
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        fullname TEXT
    )
''')

# Tạo bảng danh mục workshop
cursor.execute('''
    CREATE TABLE IF NOT EXISTS custom_cost_codes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        code TEXT UNIQUE,
        name TEXT,
        description TEXT,
        is_deleted INTEGER DEFAULT 0
    )
''')

# Tạo bảng công việc
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

# --- MIGRATION: TỰ ĐỘNG THÊM CỘT NẾU DATABASE CŨ TRÊN CLOUD BỊ THIẾU CỘT ---
tasks_schema_updates = {
    "task_cost_code": "TEXT",
    "block": "TEXT",
    "description": "TEXT",
    "initial_by": "TEXT",
    "initial_date": "TEXT",
    "area": "TEXT",
    "deck": "TEXT",
    "frame": "TEXT",
    "in_charge_by": "TEXT",
    "plan_start_date": "TEXT",
    "plan_finish_date": "TEXT",
    "progress": "INTEGER DEFAULT 0",
    "remark": "TEXT",
    "image_path": "TEXT",
    "is_deleted": "INTEGER DEFAULT 0"
}

cursor.execute("PRAGMA table_info(tasks)")
existing_cols = [col[1] for col in cursor.fetchall()]

for col_name, col_type in tasks_schema_updates.items():
    if col_name not in existing_cols:
        try:
            cursor.execute(f"ALTER TABLE tasks ADD COLUMN {col_name} {col_type}")
        except Exception:
            pass

conn.commit()

def hash_password(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

# --- TIÊU ĐỀ TRANG ---
st.markdown("<div class='main-title'>🚢 SHIPCONTROL - QUẢN LÝ CÔNG VIỆC TÀU</div>", unsafe_allow_html=True)

# ==========================================
# 🔐 HỆ THỐNG XÁC THỰC (ĐĂNG NHẬP / ĐĂNG KÝ)
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
# 🚢 GIAO DIỆN CHÍNH KHI ĐÃ ĐĂNG NHẬP
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

    # ----------------------------------------------------
    # 1. BẢNG CÔNG VIỆC
    # ----------------------------------------------------
    if menu == "🧰 Bảng Công Việc":
        st.markdown("<div class='big-table-title'>📋 Bảng Quản Lý Tiến Độ Công Việc</div>", unsafe_allow_html=True)
        
        df = pd.read_sql_query("""
            SELECT 
                task_id AS 'Task ID', 
                task_name AS 'Task Name', 
                task_cost_code AS 'WS Cost Code', 
                description AS 'Description',
                initial_by AS 'Initial By', 
                initial_date AS 'Initial Date', 
                block AS 'Block', 
                area AS 'Area', 
                deck AS 'Deck', 
                frame AS 'Frame', 
                in_charge_by AS 'In Charge By', 
                plan_start_date AS 'Plan Start Date', 
                plan_finish_date AS 'Plan Finish Date', 
                progress AS 'Progress (%)', 
                remark AS 'Remark' 
            FROM tasks WHERE is_deleted = 0
        """, conn)
        
        if df.empty:
            st.info("Chưa có dữ liệu công việc nào trong hệ thống.")
        else:
            st.dataframe(df, use_container_width=True, height=500)

    # ----------------------------------------------------
    # 2. QUẢN LÝ DANH MỤC
    # ----------------------------------------------------
    elif menu == "⚙️ Quản Lý Danh Mục":
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
                    cursor.execute("INSERT OR REPLACE INTO custom_cost_codes (code, name, description, is_deleted) VALUES (?, ?, ?, 0)", 
                                   (code_clean, name_clean, desc_clean))
                    conn.commit()
                    st.success(f"Đã thêm thành công: **{code_clean} - {name_clean}**")
                    st.rerun()

        st.markdown("---")
        st.markdown("### 📋 Danh Sách Workshop Đã Khai Báo")
        df_ws = pd.read_sql_query("SELECT code AS 'WS Cost Code', name AS 'Workshop Name', description AS 'Mô Tả' FROM custom_cost_codes WHERE is_deleted = 0", conn)
        if df_ws.empty:
            st.info("Chưa có Workshop nào trong danh mục.")
        else:
            st.dataframe(df_ws, use_container_width=True)

    # ----------------------------------------------------
    # 3. THÊM CÔNG VIỆC MỚI (ĐẦY ĐỦ TRƯỜNG EXCEL)
    # ----------------------------------------------------
    elif menu == "➕ Thêm Công Việc":
        st.markdown("<div class='big-table-title'>➕ Thêm Công Việc Mới</div>", unsafe_allow_html=True)
        
        cost_codes_df = pd.read_sql_query("SELECT code, name FROM custom_cost_codes WHERE is_deleted = 0", conn)
        
        if cost_codes_df.empty:
            st.warning("⚠️ CHƯA CÓ DỮ LIỆU WORKSHOP: Vui lòng vào mục 'Quản Lý Danh Mục' để tạo WS Cost Code trước khi thêm công việc!")
        else:
            options = [f"{row['code']} - {row['name']}" if row['name'] else row['code'] for _, row in cost_codes_df.iterrows()]
            
            with st.form("add_task_form_full", clear_on_submit=True):
                # Hàng 1: Task ID, Task Name, WS Cost Code
                c1, c2, c3 = st.columns([1, 2, 1])
                with c1:
                    task_id = st.text_input("Task ID *")
                with c2:
                    task_name_input = st.text_input("Task Name *")
                with c3:
                    selected_cost_code = st.selectbox("WS Cost Code *", options)

                # Hàng 2: Mô tả
                description = st.text_area("Description (Mô tả công việc):", height=80)

                # Hàng 3: Initial By, Initial Date, In Charge By
                c4, c5, c6 = st.columns(3)
                with c4:
                    initial_by = st.text_input("Initial By (Người khởi tạo):", value=user_data['fullname'])
                with c5:
                    initial_date = st.date_input("Initial Date (Ngày tạo):", value=date.today())
                with c6:
                    in_charge_by = st.text_input("In Charge By (Người phụ trách):")

                # Hàng 4: Block, Area, Deck, Frame
                c7, c8, c9, c10 = st.columns(4)
                with c7:
                    block = st.text_input("Block (Ví dụ: 170150):")
                with c8:
                    area = st.text_input("Area:")
                with c9:
                    deck = st.text_input("Deck:")
                with c10:
                    frame = st.text_input("Frame:")

                # Hàng 5: Plan Start Date, Plan Finish Date, Progress (%)
                c11, c12, c13 = st.columns(3)
                with c11:
                    plan_start = st.date_input("Plan Start Date:", value=date.today())
                with c12:
                    plan_finish = st.date_input("Plan Finish Date:", value=date.today())
                with c13:
                    progress_val = st.number_input("Progress (%)", min_value=0, max_value=100, value=0, step=5)

                # Hàng 6: Remark
                remark = st.text_input("Remark (Ghi chú):")

                st.markdown("<br>", unsafe_allow_html=True)
                submitted = st.form_submit_button("💾 LƯU CÔNG VIỆC MỚI")
                
                if submitted:
                    if not task_id.strip() or not task_name_input.strip():
                        st.error("Vui lòng điền đầy đủ thông tin bắt buộc: Task ID và Task Name!")
                    else:
                        ws_code_only = selected_cost_code.split(" - ")[0]
                        cursor.execute("""
                            INSERT INTO tasks (
                                task_id, task_name, task_cost_code, description,
                                initial_by, initial_date, block, area, deck, frame,
                                in_charge_by, plan_start_date, plan_finish_date,
                                progress, remark, is_deleted
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0)
                        """, (
                            task_id.strip(),
                            task_name_input.strip(),
                            ws_code_only,
                            description.strip(),
                            initial_by.strip(),
                            str(initial_date),
                            block.strip(),
                            area.strip(),
                            deck.strip(),
                            frame.strip(),
                            in_charge_by.strip(),
                            str(plan_start),
                            str(plan_finish),
                            int(progress_val),
                            remark.strip()
                        ))
                        conn.commit()
                        st.success(f"Đã lưu thành công công việc **{task_id} - {task_name_input}**!")

    # ----------------------------------------------------
    # 4. CHỈNH SỬA / XÓA TẠM
    # ----------------------------------------------------
    elif menu == "✏️ Chỉnh Sửa/Xóa":
        st.markdown("<div class='big-table-title'>✏️ Chỉnh Sửa & Xóa Công Việc</div>", unsafe_allow_html=True)
        
        tasks_df = pd.read_sql_query("SELECT id, task_id, task_name, progress FROM tasks WHERE is_deleted = 0", conn)
        if tasks_df.empty:
            st.info("Hiện không có công việc nào để chỉnh sửa hoặc xóa.")
        else:
            task_list = [f"{row['id']} | {row['task_id']} - {row['task_name']}" for _, row in tasks_df.iterrows()]
            selected_task_str = st.selectbox("Chọn công việc cần thao tác:", task_list)
            selected_id = int(selected_task_str.split(" | ")[0])
            
            col_del, col_space = st.columns([1, 2])
            with col_del:
                if st.button("🗑️ Chuyển Vào Thùng Rác (Xóa Tạm)", type="secondary", key="btn_soft_delete"):
                    cursor.execute("UPDATE tasks SET is_deleted = 1 WHERE id = ?", (selected_id,))
                    conn.commit()
                    st.success("Đã chuyển công việc vào Thùng Rác thành công!")
                    st.rerun()

    # ----------------------------------------------------
    # 5. THÙNG RÁC VÀ KHÔI PHỤC
    # ----------------------------------------------------
    elif menu == "🗑️ Thùng Rác":
        st.markdown("<div class='big-table-title'>🗑️ Thùng Rác & Khôi Phục Dữ Liệu</div>", unsafe_allow_html=True)
        
        deleted_df = pd.read_sql_query("SELECT id, task_id, task_name, task_cost_code, initial_by, initial_date FROM tasks WHERE is_deleted = 1", conn)
        
        if deleted_df.empty:
            st.info("Thùng rác hiện tại đang trống.")
        else:
            st.markdown("### 📋 Danh sách các công việc đã xóa tạm:")
            st.dataframe(deleted_df, use_container_width=True)
            
            st.markdown("---")
            st.markdown("### 🔄 Khôi Phục Công Việc")
            
            del_options = [f"{row['id']} | {row['task_id']} - {row['task_name']}" for _, row in deleted_df.iterrows()]
            restore_target = st.selectbox("Chọn công việc muốn khôi phục:", del_options)
            restore_id = int(restore_target.split(" | ")[0])
            
            col_res1, col_res2 = st.columns(2)
            with col_res1:
                if st.button("♻️ KHÔI PHỤC CÔNG VIỆC NÀY", type="primary", key="btn_restore_task"):
                    cursor.execute("UPDATE tasks SET is_deleted = 0 WHERE id = ?", (restore_id,))
                    conn.commit()
                    st.success("Đã khôi phục công việc thành công quay trở lại Bảng Công Việc!")
                    st.rerun()
            
            with col_res2:
                if st.button("💥 XÓA VĨNH VIỄN", type="secondary", key="btn_perm_delete"):
                    cursor.execute("DELETE FROM tasks WHERE id = ?", (restore_id,))
                    conn.commit()
                    st.warning("Đã xóa vĩnh viễn công việc khỏi hệ thống!")
                    st.rerun()

    # ----------------------------------------------------
    # 6. BÁO CÁO & THỐNG KÊ
    # ----------------------------------------------------
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